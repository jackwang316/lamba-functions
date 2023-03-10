import boto3

sts_client = boto3.client('sts')

def lambda_handler(event, context):
    sts_response = sts_client.assume_role(RoleArn='arn:aws:iam::515092417918:role/jack_474', 
                                          RoleSessionName='test-session',
                                          DurationSeconds=900)
                                          
                                          
    aws2_dynamodb_client = boto3.client('dynamodb', region_name='us-east-1',
                                        aws_access_key_id=sts_response['Credentials']['AccessKeyId'],
                                        aws_secret_access_key=sts_response['Credentials']['SecretAccessKey'],
                                        aws_session_token=sts_response['Credentials']['SessionToken'])
                                        
    deck = aws2_dynamodb_client.get_item(TableName='decks', Key={'deckID': {'N': event['pathParameters']['id']}})
    
    if 'Item' not in deck:
        return{
            "statusCode" : 404,
            "body" : "No deck with such ID has been found"
        }
    
    return{
        "statusCode" : 200,
        "body" : deck
    }
