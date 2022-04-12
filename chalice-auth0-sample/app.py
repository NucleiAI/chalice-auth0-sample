from chalice import Chalice
from chalicelib.auth0.blueprint import auth0, requires_auth

# App Configuration
app = Chalice(app_name='chalice-auth0-sample')
app.register_blueprint(auth0)

# App Routes
@app.route('/')
def public():
    return {'message': 'Hello from a public endpoint! You don\'t need to be authenticated to see this.'}

@app.route('/private', methods=['GET', 'POST'])
@requires_auth
def private():
    return {'message': 'Hello from a private endpoint! You need to be authenticated to see this.'}