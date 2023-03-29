import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('cognito-idp')

def lambda_handler(event, context):
    try:
        # Retrieves token
        token = event['headers']['Authorization'].split(' ')[1]
        # Fetches user based on token and retrieves required attributes
        logger.info('Retrieving user..')
        user = client.get_user(
            AccessToken = token,
        )
        
        response = user['UserAttributes']
        
        _id = response[0]['Value']
        firstname = response[2]['Value']
        lastname = response[3]['Value']
        email = response[4]['Value']
        
        logger.info('Returning user information...')
        return{
            "isBase64Encoded": True,
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps({
                "isLoggedIn" : "true",
                "user": {
                    "_id" : _id,
                    "firstname" : firstname,
                    "lastname" : lastname,
                    "email" : email,
                    "iat" : "Do we need this?"
                }
            })
        }
        
    except Exception as e:
        logger.error(str(e))
        return{
            "isBase64Encoded": True,
            "statusCode" : 403,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body" : json.dumps({'error' : str(e)})
        }