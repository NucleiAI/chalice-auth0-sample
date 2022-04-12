import json
import os
import urllib3

# Auth0 Resources
API_AUDIENCE = os.environ['API_AUDIENCE']
AUTH0_APP_CLIENT_ID = os.environ['AUTH0_APP_CLIENT_ID']
AUTH0_APP_CLIENT_SECRET = os.environ['AUTH0_APP_CLIENT_SECRET']
AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']

# HTTP Client
http = urllib3.PoolManager()

def get_token():
    ''' Get a token from Auth0 '''
    # Compose URL
    url = f'https://{AUTH0_DOMAIN}/oauth/token'

    # Compose headers
    headers = {'content-type': 'application/json'}

    # Compose body
    body = json.dumps({
        'client_id': AUTH0_APP_CLIENT_ID,
        'client_secret': AUTH0_APP_CLIENT_SECRET,
        'audience': API_AUDIENCE,
        'grant_type': 'client_credentials'
    })

    # Make request
    r = http.request(method = 'POST', url = url, headers=headers, body=body)

    print(f'Response from Auth0: {r.status}')

    if r.status == 200:
        return json.loads(r.data.decode('utf-8'))
    else:
        print(r.data.decode('utf-8'))