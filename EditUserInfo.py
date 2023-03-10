import boto3

sts_client = boto3.client('sts')
JWT_SECRET = "KeyforJSONWebToken"

def lambda_handler(event, context):
    sts_response = sts_client.assume_role(RoleArn='arn:aws:iam::515092417918:role/jack_474', 
                                          RoleSessionName='test-session',
                                          DurationSeconds=900)
                                          
                                          
    aws2_dynamodb_client = boto3.client('dynamodb', region_name='us-east-1',
                                        aws_access_key_id=sts_response['Credentials']['AccessKeyId'],
                                        aws_secret_access_key=sts_response['Credentials']['SecretAccessKey'],
                                        aws_session_token=sts_response['Credentials']['SessionToken'])
    jwtToken = decrypt(JWT_SECRET, event['jwtToken'])
    parsedInfo = jwtToken.split("_")
    
    user = aws2_dynamodb_client.get_item(TableName='CardifyDB', Key={'email': {'S': parsedInfo[0]}})
    
    if 'Item' not in user:
        return{
            "statusCode" : 403,
            "body": "Invalid JWT token provided, can't access or modify resource"
        }
        
    if user['Item']['password']['S'] != parsedInfo[1]:
        return{
            "statusCode" : 403,
            "body": "Invalid JWT token provided, can't access or modify resource"
        }
        
    response = aws2_dynamodb_client.put_item(
        TableName="CardifyDB", 
        Item={
            'email': {'S' : parsedInfo[0]},
            'id' : {'S' : user['Item']['Id']['S']},
            'firstname' : {'S' : event['firstname']},
            'lastname' : {'S' : event['lastname']},
            'password': {'S': parsedInfo[1]},
        }
    )
    
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

def decrypt(key, encryped):
    msg = []
    for i, c in enumerate(encryped):
        key_c = ord(key[i % len(key)])
        enc_c = ord(c)
        msg.append(chr((enc_c - key_c) % 127))
    return ''.join(msg)