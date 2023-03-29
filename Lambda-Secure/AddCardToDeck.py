import boto3
import json
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        client = boto3.client('cognito-idp')
        aws2_dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
        
        deck = aws2_dynamodb_client.get_item(TableName='decks', Key={'deckID': {'S': event['pathParameters']['id']}})
        
        # Parses token and fetches user
        token = event['headers']['Authorization'].split(' ')[1]
        
        user = client.get_user(
            AccessToken = token    
        )
        logger.info('Add card to deck {deckid} initiated by user {id}'.format(id = user['Username'], deckid = event['pathParameters']['id']))
        # Fixes JSON read in as string error with lambda proxy integration
        cardList = event['body']
        if isinstance(cardList, str):
            cardList = json.loads(cardList)
        
        card = cardList['card']
        
        # Will only update if user of the request matches the userid of the deck
        if user['Username'] == deck['Item']['userid']['S']:
            logger.info('User {id} authenticated for add card to deck {deckid}'.format(id = user['Username'], deckid=event['pathParameters']['id']))
            response = aws2_dynamodb_client.update_item(
            TableName='decks', 
            Key={'deckID': {'S': event['pathParameters']['id']}},
                UpdateExpression="SET Cards = list_append(if_not_exists(Cards, :empty_list), :v)",
                ExpressionAttributeValues={":v": {"L": [{"SS": card}]}, ":empty_list": {"L": []}}
            )
            
            logger.info('Card has been added to deck {deckid}'.format(deckid=event['pathParameters']['id']))

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
        logger.info('User {id} is not authorized to add card to deck {deckid}'.format(id = user['Username'], deckid=event['pathParameters']['id']))
        return{
            "isBase64Encoded": True,
                "statusCode": 403,
                "headers": {
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin" : "*", 
                    "Access-Control-Allow-Credentials" : True ,
                    "Access-Control-Allow-Methods": "OPTIONS,PATCH, POST,GET"
                },
                "body" : json.dumps("Couldn't add cards to deck {id} due to user not being the original creator.".format(id = event['pathParameters']['id']))
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
                "Access-Control-Allow-Methods": "OPTIONS,PATCH,POST,GET"
            },
            "body" : "Couldn't add card {card} to deck {id} due to: {code}: {message}".format(
                card = event['body']['card'],
                id = event['pathParameters']['id'],
                code = err.response['Error']['Code'], 
                message = err.response['Error']['Message']
            )
        }