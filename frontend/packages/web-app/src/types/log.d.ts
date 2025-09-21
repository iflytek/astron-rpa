declare namespace RPA {
  type LogLevel = 'error' | 'info' | 'warning' | 'debug'
  // 0 开始 1 成功 2 失败 3 失败跳过
  type LogStatus = 0 | 1 | 2 | 3

  // "code(代码执行位置)" "user(普通打印 用户打印)" "flow(流程角度 启动-关闭)"
  type LogType = 'code' | 'user' | 'flow'
  type LogFlowStatus = 'init' | 'init_success' | 'task_start' | 'task_end' | 'task_error'
  type LogCodeStatus = 'start' | 'res' | 'error' | 'skip' | 'debug_start'

  interface ServerLogItem {
    event_id: number
    log_level: LogLevel
    log_type: LogType
    line: number
    event_time: number
    msg_str: string
    process?: string
    process_id?: string
    line_id?: string
    status?: LogCodeStatus | LogFlowStatus
    atomic?: string
    error_str?: string
    error_traceback?: any
  }

  interface LogItem {
    id: string | number
    logLevel: LogLevel
    logLevelText: string
    timestamp: string
    content: string
    lineNum: number
    processName?: string
    processId?: string
  }
}
