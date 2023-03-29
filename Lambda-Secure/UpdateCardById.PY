import boto3
import json
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    aws2_dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    
    try:
        client = boto3.client('cognito-idp')
        
        token = event['headers']['Authorization'].split(' ')[1]
        
        user = client.get_user(
            AccessToken = token    
        )
        
        
        
        deck = aws2_dynamodb_client.get_item(TableName='decks', Key={'deckID': {'S': event['pathParameters']['id']}})
    
        cardId = event['pathParameters']['cardid']
    
        cardList = event['body']
    
        if isinstance(cardList, str):
            cardList = json.loads(cardList)
        
        card = cardList['card']
        
        if user['Username'] == deck['Item']['userid']['S']:
            response = aws2_dynamodb_client.update_item(
                TableName='decks', 
                Key={'deckID': {'S': event['pathParameters']['id']}},
                UpdateExpression='SET Cards[' + cardId + '] = :v',
                ExpressionAttributeValues={":v": {"SS": card}}
            )
            logger.info('Updated card {cardid} in deck {deckid}'.format(cardid=cardId, deckid = event['pathParameters']['id']))
            return{
                "isBase64Encoded": True,
                "statusCode" : 200,
                "headers": {
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin" : "*", 
                    "Access-Control-Allow-Credentials" : True ,
                    "Access-Control-Allow-Methods": "OPTIONS,PATCH, POST,GET"
                },
                "body" : json.dumps(response)
            }
        logger.warning('Unauthorized update to card {cardId} in deck {deckid}'.format(cardid=cardId, deckid = event['pathParameters']['id']))
        return{
            "isBase64Encoded": True,
            "statusCode": 403,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,PATCH, POST,GET"
            },
            "body" : json.dumps("Couldn't update cards {cardid} in deck {id} due to user not being the original creator.".format(id = event['pathParameters']['id'], cardid = cardId))
        }
    
    except ClientError as err:
        logger.error(str(err))
        return {
            "isBase64Encoded": True,
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,PATCH, POST,GET"
            },
            "body" : "Couldn't update card {cardId} of deck {id} due to: {code}: {message}".format(
                cardId = event['pathParameters']['cardid'],
                id = event['pathParameters']['id'],
                code = err.response['Error']['Code'], 
                message = err.response['Error']['Message']
            )
        }