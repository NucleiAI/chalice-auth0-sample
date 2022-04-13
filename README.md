# chalice-auth0-sample
This repository provides sample code demonstrating integration of AWS Chalice API endpoints with Auth0.

```python
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
```

## Quickstart
First create and activate a virtual environment in Python:
```bash
$ python3 --version
Python 3.9.10
$ python3 -m venv venv39
$ . venv39/bin/activate
```

Next, download the sample code:
```bash
git clone https://github.com/NucleiAI/chalice-auth0-sample.git
```

Install dependencies
```bash
cd chalice-auth0-sample
pip install -r requirements.txt
```

## Create an Auth0 API
To use Auth0 authentication, you need an Auth0 account. If you don't have an account yet, you can sign up for a free Auth0 account [here](https://auth0.com/signup).

After signing up (and signing in):

1. Go to the Auth0 [Dashboard](https://manage.auth0.com/dashboard)
2. Select the **Applications** dropdown, and then select **APIs**
3. Click **Create API**
4. Enter a **Name** for your API, and a unique **Identifer** for the API.
5. Select **Create**
6. Select the **Test** tab

You can use the bearer token available here for making authenticated requests to the API's [private endpoint](#private-endpoint).

NOTE: You will also need the unique **Identifier** you created in Step 3 when completing the [Chalice Configuration](#chalice-configuration).


## Credentials
Before you can deploy the application, be sure you have AWS credentials configured. If you have previously configured your machine to run boto3 (the AWS SDK for Python) or the AWS CLI then you can skip this section.

If this is your first time configuring credentials for AWS you can follow these steps to quickly get started:

```bash
$ mkdir ~/.aws
$ cat >> ~/.aws/config
[default]
aws_access_key_id=YOUR_ACCESS_KEY_HERE
aws_secret_access_key=YOUR_SECRET_ACCESS_KEY
region=YOUR_REGION (such as us-west-2, us-west-1, etc)
```

If you want more information on all the supported methods for configuring credentials, see the [boto3 docs](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html).

## Chalice Configuration
Before deploying the app, you will need to update the `environment_variables` in the `.chalice/chalice.json` file:

```json
{
  "version": "2.0",
  "app_name": "chalice-auth0-sample",
  "environment_variables": {
    "ALGORITHMS": "RS256",
    "API_AUDIENCE": "https://unique-idenfier-for-the-api",
    "AUTH0_DOMAIN": "dev-12345678.us.auth0.com"
  },
  "stages": {
    "dev": {
      "api_gateway_stage": "api"
    }
  }
}
```

## Deployment
To deploy the sample app, make sure that you are in the `chalice-auth0-sample` directory and run `chalice deploy`:

```bash
$ chalice deploy
Creating deployment package.
Creating IAM role: chalicelib-auth0-sample-dev
Creating lambda function: chalicelib-auth0-sample-dev
Creating Rest API
Resources deployed:
  - Lambda ARN: arn:aws:lambda:us-west-2:12345:function:chalicelib-auth0-sample-dev
  - Rest API URL: https://abcd.execute-api.us-west-2.amazonaws.com/api/
```

## Testing
The below examples use the [HTTPie CLI](https://httpie.io/cli) to make requests to the deployed API:

```bash
$ http GET {your REST API URL} Authorization:"Bearer {your bearer token}"
```

Alternatively you can test the API endpoints using `curl`:

```bash
$ curl {your REST API URL} -H "Authorization: Bearer {your bearer token}"
```

### Public endpoint
To test the sample app's public endpoint with HTTPie:

```bash
$ http GET {your REST API URL}
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 91
Content-Type: application/json
Date: Tue, 12 Apr 2022 17:35:45 GMT
Via: 1.1 12345.cloudfront.net (CloudFront)
X-Amz-Cf-Id: 12345-wrkWFLNwRyJDCQktZ-LFraxlA==
X-Amz-Cf-Pop: 12345-C1
X-Amzn-Trace-Id: Root=1-12345-678912345;Sampled=0
X-Cache: Miss from cloudfront
x-amz-apigw-id: AbcDeFghIGKMnoP=
x-amzn-RequestId: 4dab531c-a8c4-42eb-9444-adfb4b3d1048

{
    "message": "Hello from a public endpoint! You don't need to be authenticated to see this."
}
```

### Private endpoint
To test the sample app's private endpoint with HTTPie:

```bash
$ http GET {your REST API URL}/private Authorization:"Bearer {your test Auth0 token}"
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 91
Content-Type: application/json
Date: Tue, 12 Apr 2022 17:35:45 GMT
Via: 1.1 12345.cloudfront.net (CloudFront)
X-Amz-Cf-Id: 12345-wrkWFLNwRyJDCQktZ-LFraxlA==
X-Amz-Cf-Pop: 12345-C1
X-Amzn-Trace-Id: Root=1-12345-678912345;Sampled=0
X-Cache: Miss from cloudfront
x-amz-apigw-id: AbcDeFghIGKMnoP=
x-amzn-RequestId: 4dab531c-a8c4-42eb-9444-adfb4b3d1048

{
    "message": "Hello from a private endpoint! You need to be authenticated to see this."
}
```

## Cleaning Up
If you’re done experimenting with the app and you’d like to cleanup, you can use the `chalice delete` command, and Chalice will delete all the resources it created when running the `chalice deploy` command.

```bash
$ chalice delete
Deleting Rest API: abcd4kwyl4
Deleting function aws:arn:lambda:region:123456789:chalice-auth0-sample-dev
Deleting IAM Role chalice-auth0-sample-dev
```
