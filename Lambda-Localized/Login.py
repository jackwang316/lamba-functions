import boto3
import json

JWT_SECRET = 12
ENCODER_SECRET = 13

def lambda_handler(event, context):
    aws2_dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
                                        
    user = aws2_dynamodb_client.get_item(TableName='CardifyDB', Key={'email': {'S': event['email']}})
    
    
    if 'Item' not in user:
        return {
            "isBase64Encoded": True,
            "statusCode": 403,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps("Unable to authenticate, wrong email or passowrd")
        }
        
    item = user['Item']
    
    encrypted = encrypt(ENCODER_SECRET, event['password'])
    
    
    if item['password']['S'] != encrypted:
        
        return {
            "isBase64Encoded": True,
            "statusCode": 403,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps("Unable to authenticate, wrong email or passowrd")
        }
        
    jwtUnencoded = item['email']['S'] + '_' + item['password']['S'] 
    jwtEncoded = encrypt(JWT_SECRET, jwtUnencoded)
    
    response = {
        "token" : jwtEncoded,
        "user": {
            "_id" : item['id']['S'],
            "firstname": item['firstname']['S'],
            "lastname": item['lastname']['S'],
            "email" : item['email']['S'],
            "iat": "What is this for"
        }
    }
    
    return {
        "isBase64Encoded": True,
        "statusCode" : 200,
        "headers": {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin" : "*", 
            "Access-Control-Allow-Credentials" : True ,
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        "body" : json.dumps(response)
    }
                 
def get_cipherletter(new_key, letter):
    #still need alpha to find letters
    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    if letter in alpha:
        return alpha[new_key]
    else:
        return letter

def encrypt(key, message):
    message = message.upper()
    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""

    for letter in message:
        new_key = (alpha.find(letter) + key) % len(alpha)
        result = result + get_cipherletter(new_key, letter)

    return result

def decrypt(key, message):
    message = message.upper()
    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""

    for letter in message:
        new_key = (alpha.find(letter) - key) % len(alpha)
        result = result + get_cipherletter(new_key, letter)

    return result
