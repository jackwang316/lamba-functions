import boto3
import json
import logging

client = boto3.client('cognito-idp')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    
    try:
        #Parses token from header and retrieves IAM identity.
        token = event['headers']['Authorization'].split(' ')[1]
        user = client.get_user(
            AccessToken = token
        )
        
        #Handles if body is loaded as a string instead of JSON Object, happens when using lambda proxy integration
        body = event['body']
        if isinstance(body, str):
            body = json.loads(body)
        
        #Constructs new attributes object
        userId = user['Username']
        attributes = user['UserAttributes']
        attributes[2]['Value'] = body['firstname']
        attributes[3]['Value'] = body['lastname']
        # Id is removed prior to reassignment, Id is immutable, providng it will cause errors
        attributes.pop(0)
        
        logger.info('Attempting to update info for user {uid}'.format(uid = userId))
        
        response = client.admin_update_user_attributes(
            UserPoolId = "us-east-1_uYhGEnnzt",
            Username = userId,
            UserAttributes = attributes
        )
        
        logger.info('Updated info for user {uid}'.format(uid = userId))
        
        return {
            "isBase64Encoded": True,
            "statusCode" : 200,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body" : json.dumps(response)
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
            "body": json.dumps({'error' : str(e)})
        }