from astronverse.scheduler.apis.connector import datatable, executor, picker, terminal, tools, ws
from astronverse.scheduler.core.lsp.routes import router as lsp_router
from astronverse.scheduler.core.svc import get_svc
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware


def handler(app: FastAPI):
    # 添加全局中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 绑定tools路由
    app.include_router(tools.router, prefix="", tags=["tools"], dependencies=[Depends(get_svc)])

    # 绑定终端
    app.include_router(
        terminal.router,
        prefix="/terminal",
        tags=["terminal"],
        dependencies=[Depends(get_svc)],
    )

    # 绑定执行器路由
    app.include_router(
        executor.router,
        prefix="/executor",
        tags=["executor"],
        dependencies=[Depends(get_svc)],
    )

    # 绑定执行器路由
    app.include_router(
        picker.router,
        prefix="/picker",
        tags=["picker"],
        dependencies=[Depends(get_svc)],
    )

    # 绑定全局ws
    app.include_router(ws.router, prefix="/ws", tags=["ws"], dependencies=[Depends(get_svc)])

    # 绑定lsp路由
    app.include_router(lsp_router, prefix="/lsp", tags=["lsp"], dependencies=[Depends(get_svc)])

    # 绑定数据表格路由
    app.include_router(
        datatable.router,
        prefix="/datatable",
        tags=["datatable"],
        dependencies=[Depends(get_svc)],
    )
