import json
from moto import mock_dynamodb
import pytest
from hello_world import app 
from hello_world.app import lambda_handler,redirect_handler
import os
import boto3

@pytest.fixture()
def apigw_event():
    """ Generates API GW Event"""

    return {
        "body": '{ "test": "body"}',
        "resource": "/{proxy+}",
        "requestContext": {
            "resourceId": "123456",
            "apiId": "1234567890",
            "resourcePath": "/{proxy+}",
            "httpMethod": "POST",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "accountId": "123456789012",
            "identity": {
                "apiKey": "",
                "userArn": "",
                "cognitoAuthenticationType": "",
                "caller": "",
                "userAgent": "Custom User Agent String",
                "user": "",
                "cognitoIdentityPoolId": "",
                "cognitoIdentityId": "",
                "cognitoAuthenticationProvider": "",
                "sourceIp": "127.0.0.1",
                "accountId": "",
            },
            "stage": "prod",
        },
        "queryStringParameters": {"foo": "bar"},
        "headers": {
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "Accept-Language": "en-US,en;q=0.8",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Mobile-Viewer": "false",
            "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
            "CloudFront-Viewer-Country": "US",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-Port": "443",
            "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
            "X-Forwarded-Proto": "https",
            "X-Amz-Cf-Id": "aaaaaaaaaae3VYQb9jd-nvCd-de396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "CloudFront-Is-Tablet-Viewer": "false",
            "Cache-Control": "max-age=0",
            "User-Agent": "Custom User Agent String",
            "CloudFront-Forwarded-Proto": "https",
            "Accept-Encoding": "gzip, deflate, sdch",
        },
        "pathParameters": {"proxy": "/examplepath"},
        "httpMethod": "POST",
        "stageVariables": {"baz": "qux"},
        "path": "/examplepath",
    }

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"

@pytest.fixture
def dynamodb(aws_credentials):
    with mock_dynamodb():
        yield boto3.client("dynamodb", region_name="us-east-1")

@pytest.fixture
def create_table(dynamodb):
    table_name = "URL-APP-URLTable-19JIOPUYZPPC0"
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "URL", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "URL", "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    return table_name



def test_lambda_handler(dynamodb, create_table):
    event = {
        "body" : json.dumps({"URL":"https://youtube.com/"})
    }
    context = {}
    response = lambda_handler(event,context)
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'url' in body
    items = dynamodb.scan(TableName = "URL-APP-URLTable-19JIOPUYZPPC0")
    item = items["Items"]
    print(item)

    # ret = app.lambda_handler(apigw_event, "")
    # data = json.loads(ret["body"])

    # assert ret["statusCode"] == 200
    # assert "message" in ret["body"]
    # assert data["message"] == "hello world"

def test_redirect_handler(dynamodb,create_table):
    test_url = "http://localhost:8000/"
    short_url = "abcdef"

    putdata = dynamodb.put_item(
        TableName =  "URL-APP-URLTable-19JIOPUYZPPC0",
        Item = {
        "URL" : {"S":short_url},
        "longurl" : {"S": test_url}
    })

    event =  {"queryStringParameters" : {"short" : short_url }}

    response = redirect_handler(event,{})
    assert response["statusCode"] == 301
    assert response["headers"]["Location"] == test_url

