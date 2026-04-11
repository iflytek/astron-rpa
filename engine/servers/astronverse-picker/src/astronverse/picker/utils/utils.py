import asyncio
import functools
import anyio


async def call(func, *args, **kwargs):
    """统一调用，支持同步和异步函数。同步函数在线程池中执行，避免阻塞事件循环。"""
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    if kwargs:
        func = functools.partial(func, **kwargs)
    return await anyio.to_thread.run_sync(func, *args)
