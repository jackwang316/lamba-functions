import boto3

sts_client = boto3.client('sts')
ENCODER_SECRET = "This_is_my_awsome_secret_key"

def lambda_handler(event, context):
    sts_response = sts_client.assume_role(RoleArn='arn:aws:iam::515092417918:role/jack_474', 
                                          RoleSessionName='test-session',
                                          DurationSeconds=900)
                                          
                                          
    aws2_dynamodb_client = boto3.client('dynamodb', region_name='us-east-1',
                                        aws_access_key_id=sts_response['Credentials']['AccessKeyId'],
                                        aws_secret_access_key=sts_response['Credentials']['SecretAccessKey'],
                                        aws_session_token=sts_response['Credentials']['SessionToken'])
    
    user = aws2_dynamodb_client.get_item(TableName='CardifyDB', Key={'email': {'S': event['email']}})
    
    if 'Item' in user:
        return {
            "statusCode" : 409,
            "body": "Resource already created"
        }
    
    uniqueId = str(hash(event['email']))[1:8]
    encrypted = encrypt(ENCODER_SECRET, event['password'])
    response = aws2_dynamodb_client.put_item(TableName="CardifyDB", Item={'Id': {'S': uniqueId}, 'email': {'S': event['email']}, 'password':{'S': encrypted}})
    
    
    
    return {
        "statusCode" : 200,
        "body" : response
    }

def encrypt(key, msg):
    encryped = []
    for i, c in enumerate(msg):
        key_c = ord(key[i % len(key)])
        msg_c = ord(c)
        encryped.append(chr((msg_c + key_c) % 127))
    return ''.join(encryped)
