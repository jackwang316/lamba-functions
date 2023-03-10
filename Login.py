import boto3
import json

sts_client = boto3.client('sts')

JWT_SECRET = "KeyforJSONWebToken"
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
    
    
    if 'Item' not in user:
        return {
            "isBase64Encoded": True,
            "statusCode": 403,
            "headers": {
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True 
            },
            "body": json.dumps("Unable to authenticate, wrong email or passowrd")
        }
        
    item = user['Item']
    
    decrypted = decrypt(ENCODER_SECRET, item['password']['S'])
    
    
    if decrypted != event['password']:
        
        return {
            "isBase64Encoded": True,
            "statusCode": 403,
            "headers": {
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True 
            },
            "body": json.dumps("Unable to authenticate, wrong email or passowrd")
        }
        
    jwtUnencoded = item['email']['S'] + '_' + item['password']['S'] 
    jwtEncoded = encrypt(JWT_SECRET, jwtUnencoded)
        
    return {
        "isBase64Encoded": True,
        "statusCode" : 200,
        "headers": {
            "Access-Control-Allow-Origin" : "*", 
            "Access-Control-Allow-Credentials" : True 
        },
        "body" : json.dumps(jwtEncoded)
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

