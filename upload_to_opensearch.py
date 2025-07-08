import os
import json
from dotenv import load_dotenv
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests.auth import HTTPBasicAuth

# 환경변수 불러오기
load_dotenv()
master_user = os.getenv("OS_MASTER_USER")
master_password = os.getenv("OS_MASTER_PASSWORD")
endpoint = "https://vpc-mydomain-finegrained-v6ajzzcray2hbe56qhfazwhqee.us-east-1.es.amazonaws.com"  # ← 너의 도메인 주소로 변경

# OpenSearch 클라이언트 설정
auth = HTTPBasicAuth(master_user, master_password)
client = OpenSearch(
    hosts=[{"host": endpoint.replace("https://", ""), "port": 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# 벡터 인덱스 생성 (벡터 크기 확인!)
VECTOR_DIM = 1536
INDEX_NAME = "document-index"

index_body = {
    "settings": {
        "index": {
            "knn": True
        }
    },
    "mappings": {
        "properties": {
            "filename": {"type": "keyword"},
            "pdf_title": {"type": "text"},
            "chunk_id": {"type": "integer"},
            "text": {"type": "text"},
            "vector": {
                "type": "knn_vector",
                "dimension": VECTOR_DIM
            }
        }
    }
}

# 인덱스 생성
if not client.indices.exists(INDEX_NAME):
    client.indices.create(INDEX_NAME, body=index_body)
    print(f"✅ Index '{INDEX_NAME}' created.")
else:
    print(f"ℹ️ Index '{INDEX_NAME}' already exists.")

# 데이터 업로드
with open("embedded_chunks.json", "r") as f:
    chunks = json.load(f)

for i, chunk in enumerate(chunks):
    doc = {
        "filename": chunk["filename"],
        "pdf_title": chunk.get("pdf_title", ""),
        "chunk_id": chunk["chunk_id"],
        "text": chunk["text"],
        "vector": chunk["embedding"]
    }
    client.index(index=INDEX_NAME, body=doc)
    if i % 50 == 0:
        print(f"📤 Uploaded {i} chunks...")

print("🎉 All chunks uploaded to OpenSearch.")