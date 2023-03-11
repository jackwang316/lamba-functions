import boto3
import json

ENCODER_SECRET = 13

def lambda_handler(event, context):
    aws2_dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    
    
    user = aws2_dynamodb_client.get_item(TableName='CardifyDB', Key={'email': {'S': event['email']}})
    
    if 'Item' in user:
        return {
            "statusCode" : 409,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": "Resource already created"
        }
    
    uniqueId = str(hash(event['email']))[1:8]
    encrypted = encrypt(ENCODER_SECRET, event['password'])
    response = aws2_dynamodb_client.put_item(TableName="CardifyDB", 
        Item={
            'id': {'S': uniqueId}, 
            'email': {'S': event['email']}, 
            'password':{'S': encrypted}, 
            'firstname': {'S': event['firstname']},
            'lastname': {'S' : event['lastname']}
        })
    
    
    
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

