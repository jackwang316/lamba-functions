import boto3
import json

sts_client = boto3.client('sts')
JWT_SECRET = 12

def lambda_handler(event, context):
                                          
    aws2_dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    
    jwtToken = decrypt(JWT_SECRET, event['jwtToken'])
    parsedInfo = jwtToken.split("_")
    
    user = aws2_dynamodb_client.get_item(TableName='CardifyDB', Key={'email': {'S': parsedInfo[0].lower()}})
    
    if 'Item' not in user:
        return{
            "isBase64Encoded": True,
            "statusCode" : 403,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": "Invalid JWT token provided, can't access or modify resource"
        }
        
    if user['Item']['password']['S'] != parsedInfo[1]:
        return{
            "isBase64Encoded": True,
            "statusCode" : 403,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": "Invalid JWT token provided, can't access or modify resource"
        }
        
    response = aws2_dynamodb_client.put_item(
        TableName="CardifyDB", 
        Item={
            'email': {'S' : parsedInfo[0].lower()},
            'id' : {'S' : user['Item']['id']['S']},
            'firstname' : {'S' : event['firstname']},
            'lastname' : {'S' : event['lastname']},
            'password': {'S': parsedInfo[1]},
        }
    )
    
    return {
        "isBase64Encoded": True,
        "statusCode" : 200,
        "headers": {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin" : "*", 
            "Access-Control-Allow-Credentials" : True ,
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        "body" : response
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
