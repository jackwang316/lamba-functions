import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

#For Reference on scanning the table
#https://dynobase.dev/dynamodb-python-with-boto3/#scan

sts_client = boto3.client('sts')

def lambda_handler(event, context):
    sts_response = sts_client.assume_role(RoleArn='arn:aws:iam::515092417918:role/eric_474', 
                                          RoleSessionName='test-session',
                                          DurationSeconds=900)
                                        
    aws2_dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1',
                                        aws_access_key_id=sts_response['Credentials']['AccessKeyId'],
                                        aws_secret_access_key=sts_response['Credentials']['SecretAccessKey'],
                                        aws_session_token=sts_response['Credentials']['SessionToken'])
                                        
    
    #Get decksTable
    decksTable = aws2_dynamodb_resource.Table('decks')
    givenUserId = str(event['pathParameters']['id'])
    
    #Scan the decks table for decks that have the given User ID 
    response = decksTable.scan(
        FilterExpression=Attr('userid').eq(givenUserId)
    )
    
    data = response['Items']
    
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])


    return {
        "isBase64Encoded": True,
        "statusCode" : 200,
        "headers": {
                    "Access-Control-Allow-Origin" : "*", 
                    "Access-Control-Allow-Credentials" : True 
        },
        "body" : json.dumps(data)
    }

