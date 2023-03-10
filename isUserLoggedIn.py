import boto3
import json

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
    
    parsedToken = decrypt(JWT_SECRET, event['token']).split("_")
    
    user = aws2_dynamodb_client.get_item(TableName='CardifyDB', Key={'email': {'S': parsedToken[0]}})
    
    if 'Item' not in user: 
        return{
            "isBase64Encoded": True,
            "statusCode" : 403,
            "headers": {
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True 
            },
            "body" : json.dumps("Invalid JWT token provided, can't access or modify the specified resource")
        }
        
    userItem = user['Item']
    
    return{
        "isBase64Encoded": True,
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin" : "*", 
            "Access-Control-Allow-Credentials" : True 
        },
        "body": json.dumps({
            "isLoggedIn" : "true",
            "user": {
                "_id" : userItem['id']['S'],
                "firstname" : userItem['firstname']['S'],
                "lastname" : userItem['lastname']['S'],
                "email" : userItem['email']['S'],
                "iat" : "Do we need this?"
            }
        })
    }
    
    return parsedToken
    
    
def decrypt(key, encryped):
    msg = []
    for i, c in enumerate(encryped):
        key_c = ord(key[i % len(key)])
        enc_c = ord(c)
        msg.append(chr((enc_c - key_c) % 127))
    return ''.join(msg)
