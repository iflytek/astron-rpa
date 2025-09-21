import os
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.lowlevel import Server
import mcp.types as types
from starlette.types import Receive, Scope, Send

from app.services.streamable_mcp import ToolsConfig
from app.dependencies import extract_api_key_from_request

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


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.ContentBlock]:
    ctx = app.request_context

    # 从URL参数获取API_KEY
    api_key = extract_api_key_from_request(ctx)
    user_id = await tools_config.get_uid_from_raw_key(api_key)
    if not user_id:
        await ctx.session.send_log_message(
            level="error",
            data=f"No user found for API key: {api_key}",
            logger="permission_check",
            related_request_id=ctx.request_id,
        )
        return [
            types.TextContent(
                type="text",
                text="Error: No user found for this API key",
            )
        ]

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
        
        return [
            types.TextContent(
                type="text",
                text=result["message"],
            )
        ]
    else:
        # 记录失败信息
        await ctx.session.send_log_message(
            level="warning",
            data=f"Failed to execute workflow: {result['error']}",
            logger="workflow_execution",
            related_request_id=ctx.request_id,
        )
        
        return [
            types.TextContent(
                type="text",
                text=result["error"],
            )
        ]

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    # 获取请求上下文信息
    ctx = app.request_context

    # 从URL参数获取API_KEY
    api_key = extract_api_key_from_request(ctx)
    if not api_key:
        return []

    user_id = await tools_config.get_uid_from_raw_key(api_key)
    if not user_id:
        # 记录权限检查失败
        if hasattr(ctx, 'session'):
            await ctx.session.send_log_message(
                level="warning",
                data=f"No user found for API key: {api_key}",
                logger="permission_check",
                related_request_id=ctx.request_id,
            )
        return []

    # 获取用户可用的工具
    allowed_tools = await tools_config.get_tools_for_user(user_id)

    # 记录权限检查成功
    if hasattr(ctx, 'session'):
        await ctx.session.send_log_message(
            level="info",
            data=f"User access: user_id={user_id}, allowed_tools={len(allowed_tools)}",
            logger="permission_check",
            related_request_id=ctx.request_id,
        )

    return allowed_tools


async def handle_streamable_http(
    scope: Scope, receive: Receive, send: Send
) -> None:
    await session_manager.handle_request(scope, receive, send)


