import json
import re

import boto3
from boto3.dynamodb.conditions import Key


# Custom exception used to return controlled HTTP error responses.
class InvalidResponse(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


# Query the user-notes table and return the authenticated user's notes.
# Notes are returned newest-first and limited to 10 results.
def query_user_notes(user_email):
    dynamo_db = boto3.resource('dynamodb')
    user_notes_table = dynamo_db.Table('user-notes')

    result = user_notes_table.query(
        KeyConditionExpression=Key('user').eq(user_email),
        ScanIndexForward=False,
        Limit=10
    )


    return result.get('Items', [])


# Look up the email address that belongs to the provided authentication token.
# If the token does not exist, return a 403 response.
def get_authenticated_user_email(token):
    dynamo_db = boto3.resource('dynamodb')
    tokens_table = dynamo_db.Table('token-email-lookup')

    response = tokens_table.get_item(
        Key={
            'token': token
        }
    )

    item = response.get('Item')

    if not item or 'email' not in item:
        raise InvalidResponse(403)

    return item['email']


# Validate the Authentication header and extract the token from "Bearer <TOKEN>".
def authenticate_user(headers):
    if not headers or 'Authentication' not in headers:
        raise InvalidResponse(400)

    authentication_header = headers['Authentication']

    if not isinstance(authentication_header, str):
        raise InvalidResponse(400)

    if not authentication_header.startswith('Bearer '):
        raise InvalidResponse(400)

    token = authentication_header[len('Bearer '):]

    if token == '':
        raise InvalidResponse(403)

    return get_authenticated_user_email(token)


# Build the HTTP response expected by API Gateway.
def build_response(status_code, body=None):
    result = {
        'statusCode': str(status_code),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
    }

    if body is not None:
        result['body'] = body

    return result


# Main Lambda handler.
# Authenticate the request, query the user's notes, and return them as JSON.
def handler(event: dict, context):
    try:
        user_email = authenticate_user(event.get('headers'))
        notes = query_user_notes(user_email)
    except InvalidResponse as e:
        return build_response(status_code=e.status_code)
    else:
        return build_response(
            status_code=200,
            body=json.dumps(notes)
        )


# Client / Frontend
#       |
#       | HTTP request
#       | Header: Authentication: Bearer token123
#       v
# API Gateway
#       |
#       v
# AWS Lambda handler()
#       |
#       | authenticate_user()
#       v
# DynamoDB: token-email-lookup
#       |
#       | token123 -> anselem@example.com
#       v
# query_user_notes()
#       |
#       v
# DynamoDB: user-notes
#       |
#       | latest 10 notes for anselem@example.com
#       v
# Lambda response
#       |
#       v
# API Gateway returns JSON to client



# What this code does
#
# This is an AWS Lambda function behind something like API Gateway.
#
# Its job is:
#
# Receive an HTTP request → check the user token → find the user email → query that user’s notes from DynamoDB → return the notes as JSON.
#
# What the code returns
#
# The Lambda always returns an API Gateway-style HTTP response like this:
#
# {
#     "statusCode": "200",
#     "headers": {
#         "Content-Type": "application/json",
#         "Access-Control-Allow-Origin": "*"
#     },
#     "body": "[...]"
# }
#
# Important: in your code, statusCode is returned as a string, not an integer:
#
# 'statusCode': str(status_code)
#
# So it returns:
#
# "statusCode": "200"
#
# not:
#
# "statusCode": 200
#
# Usually API Gateway accepts both in many cases, but the common pattern is to return it as an integer.
#
# Successful response
#
# If the request is valid and the token exists, it returns:
#
# return build_response(
#     status_code=200,
#     body=json.dumps(notes)
# )
#
# Example response:
#
# {
#   "statusCode": "200",
#   "headers": {
#     "Content-Type": "application/json",
#     "Access-Control-Allow-Origin": "*"
#   },
#   "body": "[{\"user\": \"anselem@example.com\", \"noteId\": \"note-3\", \"content\": \"Deploy OpenSearch\", \"createdAt\": \"2026-05-03T10:00:00Z\"}]"
# }
#
# The body is a JSON string containing the notes.
#
# Error responses
# 1. Missing headers
#
# If the event has no headers:
#
# event.get('headers')
#
# returns None.
#
# Then this fails:
#
# if not headers or 'Authentication' not in headers:
#     raise InvalidResponse(400)
#
# Response:
#
# {
#   "statusCode": "400",
#   "headers": {
#     "Content-Type": "application/json",
#     "Access-Control-Allow-Origin": "*"
#   }
# }
#
# No body is returned.
#
# 2. Missing Authentication header
#
# Expected header:
#
# Authentication: Bearer abc123
#
# If it is missing, the code returns:
#
# {
#   "statusCode": "400",
#   "headers": {
#     "Content-Type": "application/json",
#     "Access-Control-Allow-Origin": "*"
#   }
# }
# 3. Authentication header is not a string
#
# This part checks that:
#
# if not isinstance(authentication_header, str):
#     raise InvalidResponse(400)
#
# So this would fail:
#
# {
#     "Authentication": 12345
# }
#
# Response:
#
# {
#   "statusCode": "400",
#   "headers": {
#     "Content-Type": "application/json",
#     "Access-Control-Allow-Origin": "*"
#   }
# }
# 4. Header does not start with Bearer
#
# This is required:
#
# if not authentication_header.startswith('Bearer '):
#     raise InvalidResponse(400)
#
# Valid:
#
# Authentication: Bearer abc123
#
# Invalid:
#
# Authentication: abc123
#
# Invalid:
#
# Authentication: Token abc123
#
# Response:
#
# {
#   "statusCode": "400",
#   "headers": {
#     "Content-Type": "application/json",
#     "Access-Control-Allow-Origin": "*"
#   }
# }
# 5. Empty token
#
# This line extracts the token:
#
# token = authentication_header[len('Bearer '):]
#
# Example:
#
# authentication_header = "Bearer abc123"
# token = "abc123"
#
# But if the header is:
#
# Authentication: Bearer
#
# then:
#
# token = ""
#
# This triggers:
#
# if token == '':
#     raise InvalidResponse(403)
#
# Response:
#
# {
#   "statusCode": "403",
#   "headers": {
#     "Content-Type": "application/json",
#     "Access-Control-Allow-Origin": "*"
#   }
# }
# 6. Token does not exist in DynamoDB
#
# The code checks the table:
#
# tokens_table = dynamo_db.Table('token-email-lookup')
#
# Then:
#
# response = tokens_table.get_item(
#     Key={
#         'token': token
#     }
# )
#
# If no item is found, this returns no Item.
#
# Then:
#
# if not item or 'email' not in item:
#     raise InvalidResponse(403)
#
# Response:
#
# {
#   "statusCode": "403",
#   "headers": {
#     "Content-Type": "application/json",
#     "Access-Control-Allow-Origin": "*"
#   }
# }
# How it works step by step
# Step 1: Lambda starts here
# def handler(event: dict, context):
#
# AWS Lambda calls this function.
#
# Example incoming event:
#
# {
#     "headers": {
#         "Authentication": "Bearer abc123"
#     }
# }
# Step 2: It authenticates the user
# user_email = authenticate_user(event.get('headers'))
#
# This sends the request headers into:
#
# def authenticate_user(headers):
#
# The function checks:
#
# if not headers or 'Authentication' not in headers:
#     raise InvalidResponse(400)
#
# So the request must contain:
#
# Authentication: Bearer <TOKEN>
# Step 3: It extracts the token
# authentication_header = headers['Authentication']
#
# Example:
#
# authentication_header = "Bearer abc123"
#
# Then:
#
# token = authentication_header[len('Bearer '):]
#
# Result:
#
# token = "abc123"
# Step 4: It looks up the user email from DynamoDB
# return get_authenticated_user_email(token)
#
# This function queries the DynamoDB table:
#
# tokens_table = dynamo_db.Table('token-email-lookup')
#
# It looks for an item where the partition key is:
#
# token = "abc123"
#
# Example DynamoDB item:
#
# {
#   "token": "abc123",
#   "email": "anselem@example.com"
# }
#
# If found, it returns:
#
# return item['email']
#
# So now:
#
# user_email = "anselem@example.com"
# Step 5: It queries the user’s notes
# notes = query_user_notes(user_email)
#
# This uses another DynamoDB table:
#
# user_notes_table = dynamo_db.Table('user-notes')
#
# Then it queries:
#
# result = user_notes_table.query(
#     KeyConditionExpression=Key('user').eq(user_email),
#     ScanIndexForward=False,
#     Limit=10
# )
#
# This means:
#
# DynamoDB query option	Meaning
# Key('user').eq(user_email)	Get notes where partition key user equals the authenticated email
# ScanIndexForward=False	Return newest first, assuming the table has a sort key such as timestamp or note ID
# Limit=10	Return maximum 10 notes
#
# Then:
#
# return result.get('Items', [])
#
# If notes exist, it returns them.
#
# If no notes exist, it returns:
#
# []
# Example full successful flow
#
# Incoming request:
#
# {
#   "headers": {
#     "Authentication": "Bearer token123"
#   }
# }
#
# DynamoDB table token-email-lookup contains:
#
# {
#   "token": "token123",
#   "email": "anselem@example.com"
# }
#
# DynamoDB table user-notes contains:
#
# [
#   {
#     "user": "anselem@example.com",
#     "noteId": "003",
#     "content": "Check OpenSearch logs",
#     "createdAt": "2026-05-03T18:00:00Z"
#   },
#   {
#     "user": "anselem@example.com",
#     "noteId": "002",
#     "content": "Fix Prometheus alert",
#     "createdAt": "2026-05-03T17:00:00Z"
#   }
# ]
#
# Lambda returns:
#
# {
#   "statusCode": "200",
#   "headers": {
#     "Content-Type": "application/json",
#     "Access-Control-Allow-Origin": "*"
#   },
#   "body": "[{\"user\": \"anselem@example.com\", \"noteId\": \"003\", \"content\": \"Check OpenSearch logs\", \"createdAt\": \"2026-05-03T18:00:00Z\"}, {\"user\": \"anselem@example.com\", \"noteId\": \"002\", \"content\": \"Fix Prometheus alert\", \"createdAt\": \"2026-05-03T17:00:00Z\"}]"
# }
# Simple architecture
# Client / Frontend
#       |
#       | HTTP request
#       | Header: Authentication: Bearer token123
#       v
# API Gateway
#       |
#       v
# AWS Lambda handler()
#       |
#       | authenticate_user()
#       v
# DynamoDB: token-email-lookup
#       |
#       | token123 -> anselem@example.com
#       v
# query_user_notes()
#       |
#       v
# DynamoDB: user-notes
#       |
#       | latest 10 notes for anselem@example.com
#       v
# Lambda response
#       |
#       v
# API Gateway returns JSON to client
# Important issue in this code
#
# You imported these:
#
# import re
#
# But re is never used.
#
# So this line can be removed:
#
# import re
# Another important issue
#
# You are using the header name:
#
# Authentication
#
# But the standard HTTP header is usually:
#
# Authorization: Bearer <TOKEN>
#
# So this code expects:
#
# Authentication: Bearer abc123
#
# Not:
#
# Authorization: Bearer abc123
#
# If the frontend sends Authorization, this Lambda will return:
#
# {
#   "statusCode": "400"
# }
#
# because it is specifically checking:
#
# 'Authentication' not in headers
#
# For real APIs, this would usually be better:
#
# if not headers or 'Authorization' not in headers:
#     raise InvalidResponse(400)
#
# authorization_header = headers['Authorization']
# Another improvement
#
# Your build_response currently does:
#
# 'statusCode': str(status_code)
#
# Better:
#
# 'statusCode': status_code
#
# So instead of:
#
# "statusCode": "200"
#
# you return:
#
# "statusCode": 200
#
# Improved function:
#
# def build_response(status_code, body=None):
#     result = {
#         'statusCode': status_code,
#         'headers': {
#             'Content-Type': 'application/json',
#             'Access-Control-Allow-Origin': '*',
#         },
#     }
#
#     if body is not None:
#         result['body'] = body
#
#     return result