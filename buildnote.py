import boto3
import json
import os
from datetime import datetime
from boto3.dynamodb.conditions import Key


client = boto3.resource('dynamodb', region_name = 'us-east-1')

def createNote(event,context):
    try:
        body=json.loads(event['body'])
        current_time = datetime.now().isoformat()
        if body['noteid'] == "":
            return {
                'statusCode': 400,
                'body': json.dumps({'Message': 'You cannot pass an empty noteid.'})
            }
        params={
            'noteid':body['noteid'],
            'title':body['title'],
            'content':body['content'],
            'createdAt': current_time,
            'updatedAt': current_time,
        
        }
        
        table = client.Table('notesdata')
        res = table.put_item(Item=params)
        
        return{
            'statusCode':200,
            'body': json.dumps({'Message':'note created Successfully.'})
        }
    except Exception as error:
        return{
            'statusCode':501,
            'body': json.dumps(f'Error while create note{error}')
        }


def listNotes(event,context):
    try:
        table = client.Table('notesdata')
        response = table.scan()
        data = response['Items']

        while 'LastEvaluateKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluateKey'])
            data.extend(response['Items'])
        
        return{
            'statusCode':200,
            'body': json.dumps(data)
        }
    except Exception as error:
        print(error)
        return{
            'statusCode':501,
            'body': json.dumps(f'Error while scan operation{error}')
        }
    
def getNote(event,context):
    noteid=event['queryStringParameters']['noteid']
    try:
        table=client.Table('notesdata')
        response = table.get_item(Key={
            'noteid':noteid
        }).get('Item')
        
        return{
            'statusCode':200,
            'body': json.dumps(response)
        }
    except Exception as error:
        return{
            'statusCode':501,
            'body': json.dumps(f'Error while get note{error}')
        }
        
def updateNote(event,context):
    try:
        body = json.loads(event['body'])
        table = client.Table('notesdata')
        current_time = datetime.now().isoformat()
        if body['noteid'] == "":
            return {
                'statusCode': 400,
                'body': json.dumps({'Message': 'You cannot pass an empty noteid.'})
            }
        existing_note = table.get_item(Key={'noteid': body['noteid']}).get('Item')

        if not existing_note:
            return {
                'statusCode': 404,
                'body': json.dumps({'Message': 'Note with the provided noteid not found.'})
            } 
        update_params = {
        'Key': {
            'noteid': body['noteid'] 
        },
        'UpdateExpression': 'SET title = :title, content = :content,updatedAt = :updatedAt',
        'ExpressionAttributeValues': {
            ':title': body['title'],
            ':content': body['content'],
            ':updatedAt': current_time,
        },
        'ReturnValues': 'ALL_NEW'  
        }
        response = table.update_item(**update_params)
        updated_attributes = {
            'content': response.get('Attributes', {}).get('content'),
            'noteid': response.get('Attributes', {}).get('noteid'),
            'title': response.get('Attributes', {}).get('title'),
        }
        return{
            'statusCode':200,
            'body': json.dumps(updated_attributes)
        }
    
    except Exception as error:
        return{
            'statusCode':501,
            'body': json.dumps(f'Error while Update note{error}')
        }

def sortingNote(event,context):
    try:
        body = json.loads(event['body'])
        table = client.Table('notesdata')
        response = None
        while True:
            if response is None:
                response = table.query(
                    IndexName='note_content',  
                    KeyConditionExpression=Key('content').eq(body['content'])
                )
            elif 'LastEvaluatedKey' in response:
                last_key = response['LastEvaluatedKey']
                response = table.query(
                    IndexName='note_content',
                    KeyConditionExpression=Key('content').eq(body['content']),
                    ExclusiveStartKey=last_key
                )
            else:
                break
            
        return{
            'statusCode':200,
            'body': json.dumps(response['Items'])
        }
            
    except Exception as error:
        print(error, "=========") 
        return{
            'statusCode':501,
            'body': json.dumps({'messages':'error while sorting Note.'}) 
        }

     
def deleteNote(event,context):
    body = json.loads(event['body'])
    try:
        table = client.Table('notesdata')
        response = table.get_item(Key={
                'noteid': body['noteid']
            })
        
        item = response.get('Item')
        if not item:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Note not found.'})
            }

        response = table.delete_item(Key={
            'noteid': body['noteid']
        })
        if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Note deleted successfully'})
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Note not found.'})
            }
        
    except Exception as error:
        return{
            'statusCode':501,
            'body': json.dumps({'messages':'error while delete Note.'}) 
        }
        
    
    
    
    
    

