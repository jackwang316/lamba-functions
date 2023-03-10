import boto3
import json

JWT_SECRET = 12

def lambda_handler(event, context):
    aws2_dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    
    parsedToken = decrypt(JWT_SECRET, event['token']).split("_")
    
    user = aws2_dynamodb_client.get_item(TableName='CardifyDB', Key={'email': {'S': parsedToken[0].lower()}})
    
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
    
    
def get_cipherletter(new_key, letter):
    #still need alpha to find letters
    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    if letter in alpha:
        return alpha[new_key]
    else:
        return letter

def decrypt(key, message):
    message = message.upper()
    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""

    for letter in message:
        new_key = (alpha.find(letter) - key) % len(alpha)
        result = result + get_cipherletter(new_key, letter)

    return result
