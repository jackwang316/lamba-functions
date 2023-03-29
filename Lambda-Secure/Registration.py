import boto3
import json
import logging

client = boto3.client('cognito-idp')
Client_ID = '209orkolrkqkrtletf0qmfg1fr'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        logger.info('Attempting to create user with email {email}'.format(email = event['email']))
        # Creates user based on provided attributes
        response = client.admin_create_user(
            UserPoolId = 'us-east-1_uYhGEnnzt',
            Username = event['email'],
            TemporaryPassword = event['password'],
            UserAttributes = [
                {
                    "Name": "email",
                    "Value": event['email']
                },
                {
                    "Name": "given_name",
                    "Value": event['firstname']
                },
                {
                    "Name": "family_name",
                    "Value": event['lastname']
                },
                {
                    "Name": "email_verified",
                    "Value": 'true'
                }
            ]
        )
        
        # First time test auth to retrieve session
        authresponse = client.admin_initiate_auth(
            UserPoolId = 'us-east-1_uYhGEnnzt',
            ClientId = Client_ID,
            AuthFlow = 'ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME' : event['email'],
                'PASSWORD': event['password'],
            }
        )
        
        logger.info('User {email} created, confirming password...'.format(email = event['email']))
        
        # Force the confirmation of existing user password by changing temp password into new password
        confirm_password_response = client.respond_to_auth_challenge(
                ClientId = Client_ID,
                ChallengeName = "NEW_PASSWORD_REQUIRED",
                ChallengeResponses = {
                    "USERNAME" : event['email'],
                    "NEW_PASSWORD" : event['password'],
                },
                Session = authresponse['Session']
            )
        logger.info('Confirmed password, returning new user')
        return {
            "isBase64Encoded": True,
            "statusCode" : 200,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body" : json.dumps(response['User']['Attributes'])
        }
    except Exception as e:
        logger.error(str(e))
        return{
            "isBase64Encoded": True,
            "statusCode" : 500,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body" : json.dumps({'error' : str(e)})
        }