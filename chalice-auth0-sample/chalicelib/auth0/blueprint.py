from functools import wraps
import json
import os
from urllib.request import urlopen

from chalice import Blueprint, Response
from jose import jwt

# Auth0 Resources
ALGORITHMS = os.environ['ALGORITHMS'].split(',')
API_AUDIENCE = os.environ['API_AUDIENCE']
AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']

# Auth0 Blueprint
auth0 = Blueprint(__name__)

# Auth0 Components
class AuthError(Exception):
    def __init__(self, error):
        self.error = error

def auth_error_handler(e):
    ''' Handler for AuthError exceptions '''
    return Response(
        body=json.dumps({
            'message': e.error['message']
        }),
        status_code = 401,
        headers = {'Content-Type': 'application/json'}
    )

def get_token_auth_header():
    ''' Gets access token from the Authorization header ''' 
    # Get current_request object
    request = auth0.current_request

    # Get Authorization header
    auth = request.headers.get('Authorization', None)

    # Handle missing Authorization header
    if not auth:
        raise AuthError({'message': 'Missing authorization header'})

    # Parse authorization header
    parts = auth.split()

    # Check for correct authorization type
    if parts[0].lower() != 'bearer':
        raise AuthError({'message': 'Invalid authorization header, must start with Bearer.'})

    # Check for correct number of parts    
    elif len(parts) == 1:
        raise AuthError({'message': 'Invalid authorization header, token not found.'})

    elif len(parts) > 2:
        raise AuthError({'message': 'Invalid authorization header, too many parts.'})

    # Return authorization token
    token = parts[1]
    return token

def requires_auth(f):
    ''' Wrapper for protected endpoints '''
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Get token from authorization header
            token = get_token_auth_header()

            # Get JSON Web Key Sets from Auth0
            jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
            jwks = json.loads(jsonurl.read())

            # Decode header
            try:
                unverified_header = jwt.get_unverified_header(token)
            except:
                raise AuthError({'message': 'Invalid authorization header. Use an RS256 signed JWT Access Token.'})

            # Get key from JSON Web Key Set
            rsa_key = {}
            for key in jwks['keys']:
                if key['kid'] == unverified_header['kid']:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e']
                    }

            # Validate token
            if not rsa_key:
                raise AuthError({'message': 'Invalid authorization header. Unable to find appropriate key.'})

            # Verify JWT signature and validate claims
            else:
                try:
                    payload = jwt.decode(
                        token,
                        rsa_key,
                        algorithms = ALGORITHMS,
                        audience = API_AUDIENCE,
                        issuer = f'https://{AUTH0_DOMAIN}/'
                    )

                # Handle expired signatures
                except jwt.ExpiredSignatureError:
                    raise AuthError({'message': 'Authorization token expired.'})

                # Handle invalid claims
                except jwt.JWTClaimsError:
                    raise AuthError({'message': 'Invalid claims. Please check the audience and issuer.'})

                # Handle everything else
                except Exception as e:
                    raise AuthError({'message': f'Unable to parse authentication token: {e}'})

                # Update context object for current request
                auth0.current_request.context.update(payload)

                # Return wrapped function
                return f(*args, **kwargs)

        # Handle exceptions
        except AuthError as e:
            return auth_error_handler(e)

    # Return decorated function
    return decorated