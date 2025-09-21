#!/usr/bin/env python3
"""
AI Service 启动脚本
支持通过参数指定环境配置文件

使用方法:
    python run.py          # 使用默认配置
    python run.py dev      # 使用 .env.dev 配置
    python run.py prod     # 使用 .env.prod 配置
    python run.py test     # 使用 .env.test 配置

环境变量:
    ENV=dev               # 通过环境变量指定环境
"""

import sys
import os
import uvicorn
from dotenv import load_dotenv

def load_environment_config(env_name=None):
    """根据环境名称加载对应的配置文件"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if env_name:
        env_file = f".env.{env_name}"
        env_path = os.path.join(base_dir, env_file)
        
        if os.path.exists(env_path):
            print(f"Loading environment from: {env_file}")
            load_dotenv(env_path, override=True)
        else:
            print(f"Warning: Environment file {env_file} not found, using default configuration")
            # 加载默认配置
            load_dotenv(os.path.join(base_dir, ".env.default"))
            load_dotenv(os.path.join(base_dir, ".env"), override=True)
    else:
        print("Using default environment configuration")
        # 加载默认配置
        load_dotenv(os.path.join(base_dir, ".env.default"))
        load_dotenv(os.path.join(base_dir, ".env"), override=True)

def main():
    # 获取环境参数，优先从环境变量获取，其次从命令行参数获取
    env_name = os.getenv('ENV') or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not env_name:
        env_name = "local"
    
    # 加载环境配置
    load_environment_config(env_name)
    
    print(f"Starting AI Service with environment: {env_name or 'default'}")
    
    # 启动应用
    uvicorn.run(
        "app.main:app",  # 在Docker容器中，从/app目录启动，所以是app.main:app
        host="0.0.0.0",
        port=6688,
        proxy_headers=True,
        workers=4,
        reload=True if env_name == "dev" else False,  # 开发环境启用热重载
    )

if __name__ == "__main__":
    main() 