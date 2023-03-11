import boto3
import json
from botocore.exceptions import ClientError

def lambda_handler(event, context):

    aws2_dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    
    deckId = event['pathParameters']['id']
    cardId = event['pathParameters']['cardid']
    
    try:
        response = aws2_dynamodb_client.update_item(
            TableName='decks',
            Key={'deckID': {'S': deckId}},
            UpdateExpression='REMOVE Cards[' + cardId + ']'
        )
        deck = aws2_dynamodb_client.get_item(TableName='decks', Key={'deckID': {'S': deckId}})
        
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
    except ClientError as err:
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