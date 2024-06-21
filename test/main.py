import json

def lambda_handler(event, context):
    name = event.get('name', 'World')
    return {
        'statusCode': 200,
        'body': f'Hello, {name}!'
    }

# For local development testing only (optional)
if __name__ == '__main__':
    with open('event.json', 'r') as f:
        event = json.load(f)
    response = lambda_handler(event, {})
    print(response)