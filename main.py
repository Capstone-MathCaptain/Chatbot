from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
from MCP_servers.mcp_response_generator import generate_response_from_mcp
import asyncio

app = FastAPI()


class ChatHistoryItem(BaseModel):
    user_id: int
    role: str
    message: str
    send_time: str

    class Config:
        allow_population_by_field_name = True
        alias_generator = lambda field: ''.join(
            word if i == 0 else word.capitalize() for i, word in enumerate(field.split('_'))
        )

class MCPPrompt(BaseModel):
    template: str
    inputs: Dict[str, str]
    history: Optional[List[ChatHistoryItem]] = []

class MCPRequest(BaseModel):
    prompt: MCPPrompt
    resources: Optional[Dict[str, List[str]]] = {}
    tools: Optional[List[dict]] = []


@app.post("/mcp/query")
# This endpoint supports both camelCase and snake_case formats in incoming JSON.
async def handle_mcp_query(mcp_request: MCPRequest):
    result = await asyncio.to_thread(generate_response_from_mcp, mcp_request.dict())
    return {
        "role": "assistant",
        "userId": mcp_request.prompt.inputs.get("user_id"),
        "message": result
    }