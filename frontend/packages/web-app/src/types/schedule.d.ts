/** @format */

type TaskType = 'schedule' | 'mail' | 'file' | 'hotKey' | 'manual'
type FrequencyType = 'days' | 'weeks' | 'months' | 'hours' | 'minutes' | 'regular' | 'advance'
type FileEvents = 'create' | 'delete' | 'update' | 'renamed'
type MailFlag = 'qq' | '163' | '126' | 'iflytek' | 'advance'
type FixedLengthArray = [0, 1, 2, 3, 4, 5, 6]

export interface Schedule {
  end_time?: string
  frequency_flag: FrequencyType
  minutes?: number
  hours?: number
  weeks?: number[]
  months?: number
  time_expression?: string
  cron_expression?: string
  end_time_checked?: boolean
}
export interface Mail {
  user_mail: string
  user_authorization: string
  mail_flag: MailFlag
  end_time: string
  interval_time: number
  condition: string
  sender_text: string
  receiver_text: string
  theme_text: string
  content_text: string
  attachment: boolean
  custom_mail_server: string
  custom_mail_port: string
}
export interface File {
  directory: string
  relative_sub_path: boolean
  events: FileEvents[]
  files_or_type: string
}
interface HotKey {
  key: string
  shortcuts: string[]
}
export interface Manual {}

export interface Task {
  /**
   * 是否启用 1 启用 ；0 不启用
   */
  enable?: number
  /**
   * 报错如何处理：跳过 jump、中止 stop
   */
  exceptional?: 'jump' | 'stop'
  /**
   * 触发器计划任务名称
   */
  name: string
  /**
   * 机器人执行序列
   */
  robotInfoList?: RobotInfo[]
  /**
   * 构建计划任务的灵活参数
   */
  taskJson?: any
  /**
   * 任务类型：schedule、mail、file、hotKey、manual
   */
  taskType: TaskType
  /**
   * 超时时间
   */
  timeout?: number
  [property: string]: any
  mail?: Mail
  schedule?: Schedule
  file?: File
  hotkey?: HotKey
  manual?: Manual
  taskEnable?: boolean
}

/**
 * com.iflytek.rpa.task.entity.dto.RobotInfo
 *
 * RobotInfo
 */
export interface RobotInfo {
  paramJson?: string
  robotId: string
  [property: string]: any
}

export interface TaskTrigger {
  task_type?: TaskType
  enable?: boolean
  callback_project_ids?: string[]
  queue_enable?: boolean

  end_time?: string
  frequency_flag?: FrequencyType
  minutes?: number
  hours?: number
  weeks?: number[]
  months?: number[]
  time_expression?: string
  cron_expression?: string
  timeout?: number

  directory?: string
  relative_sub_path?: boolean // 是否监听子目录
  events?: string[]
  files_or_type?: string[]

  shortcuts?: string[]

  interval_time?: number
  condition?: string
  sender_text?: string
  receiver_text?: string
  theme_text?: string
  content_text?: string
  attachment?: boolean
  mail_flag?: string
  custom_mail_server?: string
  custom_mail_port?: string
  user_mail?: string
  user_authorization?: string
}
