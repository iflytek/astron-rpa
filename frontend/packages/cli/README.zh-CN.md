# @rpa/cli

Astron RPA 开发的命令行工具。

## 安装

您可以全局安装此包，也可以在项目中本地安装。

```bash
# 全局安装
npm install -g @rpa/cli
# 或
pnpm add -g @rpa/cli

# 本地安装
npm install @rpa/cli --save-dev
# 或
pnpm add @rpa/cli -D
```

## 使用方法

### 命令

#### `rpa dev`

启动开发服务器。

```bash
rpa dev
```

#### `rpa build`

构建生产环境库。

**选项:**
- `-w, --watch`: 开启监听模式，监听文件变化并重新构建。

```bash
rpa build
# 带监听模式构建
rpa build --watch
```

#### `rpa create`

创建一个新的插件模版。

**选项:**
- `-n, --name [name]`: 插件名称。
- `-t, --target [dir]`: 生成的目标目录。

如果未提供选项，将启动交互式提示引导您完成操作。

```bash
rpa create
# 或指定参数
rpa create --name my-plugin --target ./packages/my-plugin
```

### 全局选项

- `--debug [feat]`: 显示调试日志。
- `--help`: 显示帮助信息。
- `--version`: 显示版本号。

## 开发

如果您正在开发此 CLI 包本身：

```bash
# 安装依赖
pnpm install

# 构建 CLI
pnpm build

# 运行类型检查
pnpm typecheck

# 开发监听模式
pnpm dev
```

## 许可

ISC
