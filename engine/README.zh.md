简体中文 | [English](README.md)
# 自动构建与更新 meta 配置说明  

本项目通过 `meta_json.py` 脚本实现组件 meta 配置的自动构建、合并与上传。以下为使用说明：

## 功能简介

- 自动执行各组件目录下的 `meta.py`，生成/更新本地 `meta.json`
- 合并所有组件的 `meta.json` 为一个总配置
- 拉取远程服务器上的 meta 配置，与本地合并，避免丢失远程已有内容
- 支持将合并后的配置上传到服务器

## 环境准备

1. 安装依赖
  ```bash
  pip install requests python-dotenv
  ```
2. 在项目根目录下创建 `.env` 文件，配置以下环境变量：
  ```
  COMPONENTS_META_UPLOAD_URL=你的meta上传接口地址
  REMOTE_META_URL=你的远程meta获取接口地址
  ```

## 使用方法

1. 进入 `engine` 目录：
  ```bash
  cd engine
  ```
2. 运行脚本：
  ```bash
  python meta_json.py
  ```
3. 按提示操作，确认是否上传合并后的 meta 配置到服务器。

## 工作流程

1. **执行组件 meta.py**  
  自动遍历 `components` 目录，跳过 `astronverse-database`，执行每个组件下的 `meta.py`，生成/更新对应的 `meta.json`。

2. **合并本地 meta.json**  
  汇总所有组件的 `meta.json`，生成临时文件 `temp_local.json`。

3. **获取远程 meta 配置**  
  通过接口获取服务器上的 meta 配置，保存为 `temp_remote.json`。

4. **合并本地与远程 meta**  
  将本地新增或更新的配置合并到远程 meta 列表，生成 `temp_update.json`。

5. **上传更新后的 meta**  
  根据用户输入，决定是否将合并后的 meta 配置上传到服务器。

## 注意事项

- 请确保 `.env` 文件中接口地址正确可用，参考 `.env.example`。
- 合并逻辑以本地为主，远程未包含的内容会被补充。
- 上传操作不可逆，请谨慎确认。

如有问题请联系项目维护者。