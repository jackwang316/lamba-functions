import boto3
import json
import logging

client = boto3.client('cognito-idp')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    
    Client_ID = '209orkolrkqkrtletf0qmfg1fr'
    
    try:
        logger.info('Attempting to authenticate email {email}'.format(email = event['email']))
        # Authentication
        authresponse = client.admin_initiate_auth(
            UserPoolId = 'us-east-1_uYhGEnnzt',
            ClientId = Client_ID,
            AuthFlow = 'ADMIN_USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME' : event['email'],
                'PASSWORD': event['password'],
            }
        )
        
        logger.info('Authentication successful')
        
        # Look up user based on access token and retrieves necessary attributes
        lookup_response = client.get_user(
            AccessToken=authresponse['AuthenticationResult']['AccessToken']
        )

        attributes = lookup_response['UserAttributes']
        
        
        _id = lookup_response['Username']
        
        logger.info('Returning user data for email {email}'.format(email = event['email']))
        response = {
            "token" : authresponse['AuthenticationResult']['AccessToken'],
            "user" : {
                "_id": _id,
                "firstname": attributes[2]['Value'],
                "lastname": attributes[3]['Value'],
                "email": attributes[4]['Value'],
                "iat": "What is this for",
            }
        }
        
        return {
            "isBase64Encoded": True,
            "statusCode" : 200,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": response
        }
    except Exception as e:
        logger.error('Authentication unsuccessful for email {email}'.format(email = event['email']))
        return {
            "isBase64Encoded": True,
            "statusCode" : 500,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps({'error' : str(e)})
        }
                 
