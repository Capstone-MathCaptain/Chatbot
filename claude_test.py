import boto3
import json


import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")
boto3.setup_default_session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)
client = boto3.client("bedrock-runtime", region_name="us-east-1")

body = {
    "anthropic_version": "bedrock-2023-05-31",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "요즘 윗가슴 운동이 잘 안 먹히는 것 같아. 어떻게 하면 좋을까?"
                }
            ]
        }
    ],
    "max_tokens": 500
}

response = client.invoke_model(
    modelId="arn:aws:bedrock:us-east-1:160885280013:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    contentType="application/json",
    accept="application/json",
    body=json.dumps(body)
)

result = json.loads(response["body"].read())
print(result["content"][0]["text"])