import json

def common():    
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",  
            "Access-Control-Allow-Headers": "Content-Type", 
            "Access-Control-Allow-Methods": "OPTIONS, POST, GET" 
        },
        "body": json.dumps({"message": "CORS configuration successful"})
    }
    
    return response
