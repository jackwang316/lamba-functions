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
        deckId = event['pathParameters']['id']
        cardId = event['pathParameters']['cardid']
        token = event['headers']['Authorization'].split(' ')[1]
        
        user = client.get_user(
            AccessToken = token    
        )
        logger.info('Attempting to delete card {cardid} in deck {id}'.format(id = deckId, cardid=cardId))
        deck = aws2_dynamodb_client.get_item(TableName='decks', Key={'deckID': {'S': deckId}})
        
        if user['Username'] == deck['Item']['userid']['S']:
            response = aws2_dynamodb_client.update_item(
                TableName='decks',
                Key={'deckID': {'S': deckId}},
                UpdateExpression='REMOVE Cards[' + cardId + ']'
            )
            deck = aws2_dynamodb_client.get_item(TableName='decks', Key={'deckID': {'S': deckId}})
            logger.info('Deleted card {cardid} in deck {id}'.format(id = deckId, cardid=cardId))
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
        logger.info('User is unauthorized to delete card {cardid} in deck {id}'.format(id = deckId, cardid=cardId))
        return{
            "isBase64Encoded": True,
                "statusCode": 403,
                "headers": {
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin" : "*", 
                    "Access-Control-Allow-Credentials" : True ,
                    "Access-Control-Allow-Methods": "OPTIONS,PATCH, POST,GET"
                },
                "body" : json.dumps("Couldn't delete card {cardid} in deck {id} due to user not being the original creator.".format(id = event['pathParameters']['id'], cardid  = cardId))
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
            "body" : "Couldn't delete card {cardId} in deck {id} due to: {code}: {message}".format(
                cardId = event['pathParameters']['cardid'], 
                id = event['pathParameters']['id'],
                code = err.response['Error']['Code'], 
                message = err.response['Error']['Message']
            )
        }