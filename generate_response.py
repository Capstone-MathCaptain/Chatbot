import boto3
import json
from MCP_servers.search_opensearch import search_similar_chunks
import os
from dotenv import load_dotenv
# Claude 3.5 Sonnet v2 - Bedrock에서 호출


load_dotenv(dotenv_path=".env")
boto3.setup_default_session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)

client = boto3.client("bedrock-runtime", region_name="us-east-1")



def generate_answer(question: str, context_chunks: list[str]) -> str:
    context_text = "\n\n".join(context_chunks)

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""아래 문서를 기반으로 질문에 답해줘. 답변은 한국어로 하고, 친절하고 구체적으로 설명해줘.
숫자는 표로 정리해주면 좋고, 인용 문구는 따옴표로 강조해줘.

[문서 내용]
{context_text}

[질문]
{question}
"""
                    }
                ]
            }
        ],
        "max_tokens": 800
    }

    response = client.invoke_model(
        modelId="arn:aws:bedrock:us-east-1:160885280013:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]

if __name__ == "__main__":
    question = input("❓ 사용자 질문: ")
    chunks = search_similar_chunks(question)
    chunk_texts = [c["text"] for c in chunks]
    answer = generate_answer(question, chunk_texts)
    print("\n🧠 Claude 응답:\n", answer)