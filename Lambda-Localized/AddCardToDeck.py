import boto3
import json
from botocore.exceptions import ClientError

def lambda_handler(event, context):
                                          
    aws2_dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
                                        
    deck = aws2_dynamodb_client.get_item(TableName='decks', Key={'deckID': {'S': event['pathParameters']['id']}})
        
    try:
        cardList = event['body']
        if isinstance(cardList, str):
            cardList = json.loads(cardList)
        
        card = cardList['card']
        
        response = aws2_dynamodb_client.update_item(
        TableName='decks', 
        Key={'deckID': {'S': event['pathParameters']['id']}},
        UpdateExpression="SET Cards = list_append(if_not_exists(Cards, :empty_list), :v)",
        ExpressionAttributeValues={":v": {"L": [{"SS": card}]}, ":empty_list": {"L": []}}
        )
        

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
    except ClientError as err:
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