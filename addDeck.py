import boto3
import json
import uuid

JWT_SECRET = 12

def lambda_handler(event, context):
                                          
    aws2_dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
                                        
    
    #Get token / pass
    token = event['token']
    #Decrypt the token
    userInfo = decrypt(JWT_SECRET, token)
    
    #seperate the user info to just get the email
    parsedInfo = userInfo.split("_")
    
    user = aws2_dynamodb_client.get_item(TableName='CardifyDB', Key={'email': {'S': parsedInfo[0].lower()}})
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
