import boto3
import json
import decimal
import logging
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:                                    
        aws2_dynamodb_resource = boto3.resource('dynamodb', region_name="us-east-1")
                                            
        #Get decksTable
        decksTable = aws2_dynamodb_resource.Table('decks')
        givenUserId = str(event['pathParameters']['id'])
        
        logger.info('Retrieving all decks associated to user {id}'.format(id=givenUserId))
        
        #Scan the decks table for decks that have the given User ID 
        response = decksTable.scan(
            FilterExpression=Attr('userid').eq(givenUserId)
        )
        
        data = response['Items']
        
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
    
        logger.info('Returning all decks associated to user {id}'.format(id=givenUserId))
        return {
            "isBase64Encoded": True,
            "statusCode" : 200,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body" : json.dumps(data, cls=DecimalEncoder)
        }
    except Exception as e:
        logger.error(str(e))
        return {
            "isBase64Encoded": True,
            "statusCode" : 500,
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin" : "*", 
                "Access-Control-Allow-Credentials" : True ,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps({'error' : str(e)})
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