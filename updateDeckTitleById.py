import boto3
import json
from botocore.exceptions import ClientError

sts_client = boto3.client('sts')

def lambda_handler(event, context):
    sts_response = sts_client.assume_role(RoleArn='arn:aws:iam::515092417918:role/kiaan_474', 
                                          RoleSessionName='test-session',
                                          DurationSeconds=900)
                                          
                                          
    aws2_dynamodb_client = boto3.client('dynamodb', region_name='us-east-1',
                                        aws_access_key_id=sts_response['Credentials']['AccessKeyId'],
                                        aws_secret_access_key=sts_response['Credentials']['SecretAccessKey'],
                                        aws_session_token=sts_response['Credentials']['SessionToken'])
                                        
    deckId = event['pathParameters']['id']
    
    try:
        response = aws2_dynamodb_client.update_item(
            TableName='decks',
            Key={'deckID': {'S': deckId}},
            UpdateExpression="SET Title = :v",
            ExpressionAttributeValues={":v": { "S": event['pathParameters']['newtitle'] }}
        )
        deck = aws2_dynamodb_client.get_item(TableName='decks', Key={'deckID': {'S': deckId}})
        
        return {
            "isBase64Encoded": True,
            "statusCode" : 200,
            "headers": {
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True 
            },
            "body" : json.dumps(deck)
        }
        
    except ClientError as err:
        return {
            "isBase64Encoded": True,
            "statusCode" : 500,
            "headers": {
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True 
            },
            "body" : "Couldn't update title of deck {id} due to: {code}: {message}".format(
                id = event['pathParameters']['id'],
                code = err.response['Error']['Code'], 
                message = err.response['Error']['Message']
            )
        }