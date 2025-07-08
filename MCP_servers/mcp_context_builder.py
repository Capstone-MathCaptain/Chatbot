from MCP_servers.db_retriever import get_user_activities
from MCP_servers.search_opensearch import search_similar_chunks

def build_context_from_mcp_request(prompt: dict, resources: dict) -> str:
    user_id = prompt["inputs"].get("user_id")
    question = prompt["inputs"].get("user_question")

    activity_logs = ""
    document_chunks = ""

    # 조건부 DB 조회 판단 (질문 내용 기반)
    if question and any(keyword in question for keyword in ["운동", "공부", "기록"]):
        # 활동 기록
        if resources.get("activity_logs"):
            activity_logs = "\n".join(resources["activity_logs"])
        elif user_id:
            activity_logs = "\n".join(get_user_activities(user_id))

        # 문서 검색
        if resources.get("document_chunks"):
            document_chunks = "\n".join(resources["document_chunks"])
        else:
            chunks = search_similar_chunks(question)
            document_chunks = "\n".join([c["text"] for c in chunks])

 

    context = f"""
[사용자 활동 기록]
{activity_logs}


[문서에서 검색된 내용]
{document_chunks}

[질문]
{question}
"""
    return context
