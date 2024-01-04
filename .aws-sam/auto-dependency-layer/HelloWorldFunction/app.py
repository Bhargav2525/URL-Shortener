import json
import random
import boto3
import uuid

dynamodb_client = boto3.client("dynamodb")

def lambda_handler(event, context):
    print(event)
    URL = json.loads(event["body"]).get("URL")
    print(URL)
    unique_id = uuid.uuid4()
    unique_id = str(unique_id).split("-")[0]
    print(unique_id)
    response = dynamodb_client.put_item(
        TableName = "URL-APP-URLTable-19JIOPUYZPPC0",
        Item = {
            "URL": {"S":unique_id},

            "longurl": {"S":URL} 
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "url": "https://1f9a2frts6.execute-api.us-east-1.amazonaws.com/Prod/redirect/?short=" + unique_id
        }),
    }

def redirect_handler(event,context):
    try:
        shorturl = event["queryStringParameters"]["short"]
        response = dynamodb_client.get_item(
            TableName = "URL-APP-URLTable-19JIOPUYZPPC0",
            Key = {
                "URL" : {"S": shorturl}
            }
        )
        print(response)
        if "Item" in response:
            long_url = response['Item']["longurl"]["S"]
            return {
                'statusCode': 301,
                'headers': {'Location': long_url}
            }
        else:
            return {
                "statusCode": 404,
                "headers" : {},
                "body" : "Not Found"
            }
    except:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request'})
        }



