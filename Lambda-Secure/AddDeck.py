import boto3
import json
import uuid
import logging

client = boto3.client('cognito-idp')
aws2_dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
                                        
    try:
        #Get token
        token = event['headers']['Authorization'].split(' ')[1]
        
        # Handles json being loaded as string instead of JSON object issues with lambda proxy integration
        body = event['body']
        if isinstance(body, str):
            body = json.loads(body)
      
        # Retrieves user attributes 
        user = client.get_user(
            AccessToken = token
        )

        _id = user['Username']
        
        uidForDeck = str(uuid.uuid4())
        
        # Creates new deck in dynamodb
        result = aws2_dynamodb_client.put_item(TableName="decks", Item={'userid':{'S': _id}, 'deckID':{'S': uidForDeck}, 'Title': {'S' : body['title']}})   
        logger.info('Created new deck {id} for user {uid}'.format(id = uidForDeck, uid = _id))
        response = {
            "insertResult": result,
            "deck": {
                "userid": _id,
                "deckID": uidForDeck,
                "Title": body['title']
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
        
    except Exception as e:
        logger.error(str(e))
        return {
            "isBase64Encoded": True,
            "statusCode" : 404,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps({'error' : str(e)})
        }

        
   
    