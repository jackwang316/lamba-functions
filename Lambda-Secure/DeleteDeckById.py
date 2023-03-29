import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
sts_client = boto3.client('sts')
client = boto3.client('cognito-idp')

def lambda_handler(event, context):
    aws2_dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    
    try:
        token = event['headers']['Authorization'].split(' ')[1]
        
        user = client.get_user(
            AccessToken = token
        )
        
        logger.info('Attempting to delete deck {id}'.format(id = event['pathParameters']['id']))
        # Verifies that the user who authorized the delete is the same user that created the deck.
        deck_to_delete = aws2_dynamodb_client.get_item(TableName='decks', Key={'deckID': {'S': event['pathParameters']['id']}})
        
        if user['Username'] == deck_to_delete['Item']['userid']['S']:
            response = aws2_dynamodb_client.delete_item(TableName='decks', Key={'deckID': {'S': event['pathParameters']['id']}})
            logger.info('Deleted deck {id}'.format(id = event['pathParameters']['id']))
            return{
                "isBase64Encoded": True,
                "statusCode" : 200,
                "headers": {
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin" : "*", 
                    "Access-Control-Allow-Credentials" : True ,
                    "Access-Control-Allow-Methods": "OPTIONS,PATCH, POST,GET"
                },
                "body": json.dumps(response)
            }
        logger.info('Authorized attempt to delete deck {id}'.format(id = event['pathParameters']['id']))
        return{
            "isBase64Encoded": True,
                "statusCode": 403,
                "headers": {
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin" : "*", 
                    "Access-Control-Allow-Credentials" : True ,
                    "Access-Control-Allow-Methods": "OPTIONS,PATCH, POST,GET"
                },
                "body" : json.dumps("Couldn't delete deck {id} due to user not being the original creator.".format(id = event['pathParameters']['id']))
        }
    except Exception as err:
        logger.error(str(err))
        return{
            "isBase64Encoded": True,
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,PATCH, POST,GET"
            },
            "body" : json.dumps("Couldn't delete deck {id} due to: {code}: {message}".format(id = event['pathParameters']['id'],
            code = err.response['Error']['Code'], message = err.response['Error']['Message']))
        }
    