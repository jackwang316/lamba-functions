import boto3
import json
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    aws2_dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    client = boto3.client('cognito-idp')                  
    
    try:
        token = event['headers']['Authorization'].split(' ')[1]
        deckId = event['pathParameters']['id']
        
        deck = aws2_dynamodb_client.get_item(TableName='decks', Key={'deckID': {'S': deckId}})
         
        user = client.get_user(
            AccessToken = token    
        )
        
        if user['Username'] == deck['Item']['userid']['S']:
            response = aws2_dynamodb_client.update_item(
                TableName='decks',
                Key={'deckID': {'S': deckId}},
                UpdateExpression="SET Title = :v",
                ExpressionAttributeValues={":v": { "S": event['pathParameters']['newtitle'] }}
            )
            deck = aws2_dynamodb_client.get_item(TableName='decks', Key={'deckID': {'S': deckId}})
            logger.info('Deck {id} has been updated with title {title}'.format(id=deckID, title=event['pathParameters']['newtitle']))
            return {
                "isBase64Encoded": True,
                "statusCode" : 200,
                "headers": {
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin" : "*", 
                    "Access-Control-Allow-Credentials" : True ,
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
                },
                "body" : json.dumps(deck)
            }
        logger.info('Authorized attempted to update deck title by user {uid}'.format(uid=user['Username']))
        return{
            "isBase64Encoded": True,
                "statusCode": 403,
                "headers": {
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin" : "*", 
                    "Access-Control-Allow-Credentials" : True ,
                    "Access-Control-Allow-Methods": "OPTIONS,PATCH, POST,GET"
                },
                "body" : json.dumps("Couldn't update title of deck {id} due to user not being the original creator.".format(id = deckId))
        }
    except ClientError as err:
        logger.error(str(err))
        return {
            "isBase64Encoded": True,
            "statusCode" : 500,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body" : "Couldn't update title of deck {id} due to: {code}: {message}".format(
                id = event['pathParameters']['id'],
                code = err.response['Error']['Code'], 
                message = err.response['Error']['Message']
            )
        }