import json
import jwt
import uuid
import datetime


SECRET_KEY = "46a12cca-25e0-4848-a678-388ff5664aff"

def login(event, context):

    payload = {
        'user_id': 123,
        'username': 'testing',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    
    # Create JWT token
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return {
        'statusCode': 200,
        'body': json.dumps({
            'token': token
        })
    }


def userauthentication(event, context):
    token = event['headers']['Authorization'].split()[1]

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        policy = generate_policy('user', 'Allow', event['methodArn'])
        event['decoded_token'] = decoded_token
    except jwt.ExpiredSignatureError:
        policy = generate_policy('user', 'Deny', event['methodArn'])
    except jwt.DecodeError:
        policy = generate_policy('user', 'Deny', event['methodArn'])

    return policy


def generate_policy(principal_id, effect, resource):
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
    }
