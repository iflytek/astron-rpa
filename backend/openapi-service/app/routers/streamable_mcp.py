import json

from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.types import Receive, Scope, Send

from app.config import get_settings
from app.logger import get_logger
from app.security.mcp_auth import MCPAPIKeyAuthMiddleware
from app.services.streamable_mcp import ToolsConfig

logger = get_logger(__name__)

app = Server("iflyrpa-mcp")

global tools_config
tools_config = ToolsConfig()

# 创建 session_manager 实例
session_manager = StreamableHTTPSessionManager(
    app=app,
    event_store=None,
    json_response=False,
    stateless=True,
)


def get_authenticated_user_id(ctx) -> str:
    """Read the user identity established by the HTTP authentication boundary."""
    if ctx.request is None:
        raise RuntimeError("MCP request context is unavailable")

    user_id = getattr(ctx.request.state, "mcp_user_id", None)
    if not user_id:
        raise RuntimeError("MCP request is missing its authenticated user")
    return str(user_id)


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.ContentBlock]:
    ctx = app.request_context
    user_id = get_authenticated_user_id(ctx)
    logger.info(f"[call_tool] user_id: {user_id}")

    # 使用 ToolsConfig 执行工作流
    result = await tools_config.execute_workflow_by_name(name, user_id, arguments)

    if result["success"]:
        # 记录成功执行
        await ctx.session.send_log_message(
            level="info",
            data=f"Started workflow execution: execution_id={result['execution_id']}, project_id={result['project_id']}",
            logger="workflow_execution",
            related_request_id=ctx.request_id,
        )

        if result["message"]["code"] == "0000":
            return [types.TextContent(type="text", text=json.dumps(result["message"], indent=2, ensure_ascii=False))]
        else:
            raise Exception(f"客户端运行失败：{result['message']['msg']}")
    else:
        # 记录失败信息
        await ctx.session.send_log_message(
            level="warning",
            data=f"Failed to execute workflow: {result['error']}",
            logger="workflow_execution",
            related_request_id=ctx.request_id,
        )

        raise Exception(f"服务端运行失败：{result['error']}")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    # 获取请求上下文信息
    ctx = app.request_context
    user_id = get_authenticated_user_id(ctx)

    # 获取用户可用的工具
    allowed_tools = await tools_config.get_tools_for_user(user_id)

    # 记录权限检查成功
    if hasattr(ctx, "session"):
        await ctx.session.send_log_message(
            level="info",
            data=f"User access: user_id={user_id}, allowed_tools={len(allowed_tools)}",
            logger="permission_check",
            related_request_id=ctx.request_id,
        )

    return allowed_tools


mcp_auth_app = MCPAPIKeyAuthMiddleware(
    session_manager.handle_request,
    tools_config.get_uid_from_raw_key,
    allow_query_api_key=get_settings().MCP_ALLOW_QUERY_API_KEY,
)


async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
    await mcp_auth_app(scope, receive, send)
