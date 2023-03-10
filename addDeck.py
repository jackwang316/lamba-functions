import boto3
import json
import uuid

sts_client = boto3.client('sts')
JWT_SECRET = "KeyforJSONWebToken"

def lambda_handler(event, context):
    sts_response = sts_client.assume_role(RoleArn='arn:aws:iam::515092417918:role/eric_474', 
                                          RoleSessionName='test-session',
                                          DurationSeconds=900)
                                          
                                          
    aws2_dynamodb_client = boto3.client('dynamodb', region_name='us-east-1',
                                        aws_access_key_id=sts_response['Credentials']['AccessKeyId'],
                                        aws_secret_access_key=sts_response['Credentials']['SecretAccessKey'],
                                        aws_session_token=sts_response['Credentials']['SessionToken'])
                                        
    
    #Get token / pass
    token = event['token']
    #Decrypt the token
    userInfo = decrypt(JWT_SECRET, token)
    
    #seperate the user info to just get the email
    parsedInfo = userInfo.split("_")
    
    user = aws2_dynamodb_client.get_item(TableName='CardifyDB', Key={'email': {'S': parsedInfo[0]}})
    userId = user['Item']['id']['S']
    if 'Item' not in user:
        return {
            "isBase64Encoded": True,
            "statusCode" : 404,
            "headers": {
                    "Access-Control-Allow-Origin" : "*", 
                    "Access-Control-Allow-Credentials" : True 
                },
            "body": "User does not exist"
        }
        
    uidForDeck = str(uuid.uuid4())
    
    response = aws2_dynamodb_client.put_item(TableName="decks", Item={'userid':{'S': userId}, 'deckID':{'S': uidForDeck}})    
    
    return {
        "isBase64Encoded": True,
        "statusCode" : 200,
        "headers": {
                    "Access-Control-Allow-Origin" : "*", 
                    "Access-Control-Allow-Credentials" : True 
        },
        "body" : json.dumps(response)
    }
    
def decrypt(key, encryped):
    msg = []
    for i, c in enumerate(encryped):
        key_c = ord(key[i % len(key)])
        enc_c = ord(c)
        msg.append(chr((enc_c - key_c) % 127))
    return ''.join(msg)
