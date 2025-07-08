# search_opensearch.py

import os
import json
from dotenv import load_dotenv
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests.auth import HTTPBasicAuth
import boto3

# 환경 변수 불러오기
load_dotenv(dotenv_path=".env")
boto3.setup_default_session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)
master_user = os.getenv("OS_MASTER_USER")
master_password = os.getenv("OS_MASTER_PASSWORD")
endpoint = "https://vpc-mydomain-finegrained-v6ajzzcray2hbe56qhfazwhqee.us-east-1.es.amazonaws.com"
INDEX_NAME = "document-index"
VECTOR_DIM = 1536

# OpenSearch 클라이언트 설정
auth = HTTPBasicAuth(master_user, master_password)
client = OpenSearch(
    hosts=[{"host": endpoint.replace("https://", ""), "port": 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Titan 임베딩 함수
def get_query_embedding(text, model_id="amazon.titan-embed-text-v1"):
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
    body = {
        "inputText": text
    }
    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
        accept="application/json",
        contentType="application/json"
    )
    result = json.loads(response["body"].read())
    return result["embedding"]

# 검색 함수
def search_similar_chunks(query: str, k=5):
    embedding = get_query_embedding(query)

    body = {
        "size": k,
        "query": {
            "knn": {
                "vector": {
                    "vector": embedding,
                    "k": k
                }
            }
        }
    }

    response = client.search(index=INDEX_NAME, body=body)
    hits = response["hits"]["hits"]
    return [hit["_source"] for hit in hits]

if __name__ == "__main__":
    query = input("🔍 질문을 입력하세요: ")
    results = search_similar_chunks(query)
    print("\n📄 유사한 청크:")
    for i, r in enumerate(results):
        print(f"\n--- Chunk {i+1} ---\n{r['text']}")