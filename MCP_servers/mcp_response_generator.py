import boto3
import json
from langchain_aws import ChatBedrock
from MCP_servers.mcp_context_builder import build_context_from_mcp_request
import pprint
client = boto3.client("bedrock-runtime", region_name="us-east-1")

llm = ChatBedrock(
    client=client,
    model_id="arn:aws:bedrock:us-east-1:160885280013:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    provider="anthropic",
    model_kwargs={
        "temperature": 0,
        "max_tokens": 512
    }
)



def generate_response_from_mcp(mcp_request: dict) -> str:
    context = build_context_from_mcp_request(
        mcp_request["prompt"],
        mcp_request.get("resources", {})
    )

    messages = []

    # context를 system 메시지로 추가
    if context.strip():
        messages.append({"role": "system", "content": context})

    # 히스토리 추가
    for item in mcp_request["prompt"].get("history", []):
        messages.append({"role": item["role"].lower(), "content": item["message"]})

    # 현재 질문 추가
    messages.append({
        "role": "user",
        "content": mcp_request["prompt"]["inputs"]["user_question"]
    })

    print("\n🔍 Claude에게 전달되는 전체 메시지 목록:")
    pprint.pprint(messages)

    response = llm.invoke(messages)
    return response.content if hasattr(response, "content") else str(response)
