# embed_chunks.py

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
# 임베딩 생성 함수
def get_embeddings(text: str, model_id="amazon.titan-embed-text-v1"):
    bedrock = boto3.client("bedrock-runtime")

    body = {
        "inputText": text  # 단일 문자열만 허용됨
    }

    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
        accept="application/json",
        contentType="application/json"
    )

    result = json.loads(response["body"].read())
    return result["embedding"]

# chunks.json 불러오기
with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# 모든 청크 임베딩 생성
embedded_chunks = []
for i, chunk in enumerate(chunks):
    print(f"{i+1}/{len(chunks)}: Embedding chunk...")
    try:
        embedding = get_embeddings(chunk["text"])
    except Exception as e:
        print(f"Error embedding chunk {i+1}: {e}")
        continue
    embedded_chunks.append({
        **chunk,
        "embedding": embedding
    })

# 저장
with open("embedded_chunks.json", "w", encoding="utf-8") as f:
    json.dump(embedded_chunks, f, ensure_ascii=False, indent=2)