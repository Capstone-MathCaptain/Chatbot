import boto3
import json
from langchain.prompts import PromptTemplate
from langchain_aws import ChatBedrock
from langchain.schema.output_parser import StrOutputParser
from MCP_servers.search_opensearch import search_similar_chunks
from MCP_servers.db_retriever import get_user_activities
import os
from dotenv import load_dotenv
# Claude 3.5 Sonnet v2 - Bedrock에서 호출


load_dotenv(dotenv_path=".env")
boto3.setup_default_session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)

# Claude 설정
client = boto3.client("bedrock-runtime", region_name="us-east-1")
llm = ChatBedrock(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    client=client
)

# MCP 요청 기반 응답 생성
def generate_response_from_mcp(mcp_request):
    question = mcp_request.prompt.inputs["user_question"]
    user_id = mcp_request.prompt.inputs.get("user_id")

    # OpenSearch 문서 검색
    opensearch_chunks = search_similar_chunks(question)
    document_context = "\n".join([c["text"] for c in opensearch_chunks])

    # 사용자 활동 기록 로드 (없으면 DB에서 조회)
    if "activity_logs" in mcp_request.resources and mcp_request.resources["activity_logs"]:
        activity_logs = "\n".join(mcp_request.resources["activity_logs"])
    elif user_id:
        activity_logs = "\n".join(get_user_activities(user_id))
    else:
        activity_logs = ""

    # 대화 기록 (그대로)
    chat_history = "\n".join(mcp_request.resources.get("chat_history", []))

    # 통합 프롬프트 구성
    full_context = f"""
[사용자 활동 기록]
{activity_logs}

[과거 대화 내용]
{chat_history}

[문서에서 검색된 내용]
{document_context}

[질문]
{question}
"""

    prompt_template = PromptTemplate.from_template(
        mcp_request.prompt.template + "\n\n" + full_context
    )
    final_prompt = prompt_template.format(**mcp_request.prompt.inputs)

    chain = prompt_template | llm | StrOutputParser()
    return chain.invoke({})
