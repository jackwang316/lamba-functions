import boto3
import json

sts_client = boto3.client('sts')

def lambda_handler(event, context):
    aws2_dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    
    try:
        response = aws2_dynamodb_client.delete_item(TableName='decks', Key={'deckID': {'S': event['pathParameters']['id']}})
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
    except Exception as err:
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
    