### 特性

- 支持 Linux 和 Windows 的区分
- IPC 协议当前采用 Windows named pipe（`npipe`）
- 日志简洁统一，保留 `context.Context` 便于后续链路扩展
- 自动根据父进程（浏览器等）派生管道名，规则为：`ASTRON_<PROCESS_NAME>_PIPE`
- 不会被阻塞，有超时机制和覆盖机制（最多缓冲 5 条消息）
- 支持并发连接，但同一时刻仅处理单条请求（锁机制，避免标准 IO 竞争）

### 构建示例：

```text
set GOOS=windows
set GOARCH=amd64
set CGO_ENABLED=0
go build -ldflags="-s -w" -o astron_native_messaging.exe .
```

