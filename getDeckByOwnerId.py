import boto3
from boto3.dynamodb.conditions import Attr

sts_client = boto3.client('sts')

def lambda_handler(event, context):
    sts_response = sts_client.assume_role(RoleArn='arn:aws:iam::515092417918:role/eric_474', 
                                          RoleSessionName='test-session',
                                          DurationSeconds=900)
                                          
                                          
    aws2_dynamodb_client = boto3.client('dynamodb', region_name='us-east-1',
                                        aws_access_key_id=sts_response['Credentials']['AccessKeyId'],
                                        aws_secret_access_key=sts_response['Credentials']['SecretAccessKey'],
                                        aws_session_token=sts_response['Credentials']['SessionToken'])
                                        
    userId = str(event['pathParameters']['id'])

    
    response = aws2_dynamodb_client.scan(
        TableName="decks",
        FilterExpression=Attr('deckID').eq("2903928"),
    )

    return response

