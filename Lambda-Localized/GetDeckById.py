import boto3
import json

sts_client = boto3.client('sts')

def lambda_handler(event, context):
    aws2_dynamodb_client = boto3.resource('dynamodb', region_name="us-east-1")
    table = aws2_dynamodb_client.Table('decks')
    deck = table.get_item(Key={'deckID':event['pathParameters']['id']})
    
    if 'Item' not in deck:
        return{
            "isBase64Encoded": True,
            "statusCode" : 404,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body" : json.dumps("No deck with such ID has been found")
        }
    
    return{
        "isBase64Encoded": True,
        "statusCode" : 200,
        "headers": {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin" : "*", 
            "Access-Control-Allow-Credentials" : True ,
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        "body" : json.dumps(deck['Item'], cls=DecimalEncoder)
    }

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return list(o)
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
