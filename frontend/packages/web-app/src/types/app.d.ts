declare namespace RPA {
  type Theme = 'light' | 'dark' | 'auto'

  interface UserSetting {
    commonSetting: { // 常规设置
      startupSettings: boolean // 启动项设置 - 引擎接口获取存储，true 开启自启动，false-关闭开机自启动
      closeMainPage: boolean // true-最小化托盘  false-退出应用
      hideLogWindow: boolean // 运行时的右下角日志窗口 true-开启隐藏  false-关闭隐藏
      hideDetailLogWindow: boolean // 运行完的详细日志窗口 true-开启隐藏  false-关闭隐藏
      autoSave: boolean // 自动保存 true-开启  false-关闭
      theme?: Theme // 主题 可选值：light、dark、system
    }
    shortcutConfig: Record<string, any> // 快捷键设置
    videoForm: VideoFormMap // 录屏设置
    msgNotifyForm: MessageFormMap // 消息通知设置
  }

  interface EmailFormMap {
    is_enable?: boolean // 是否启用
    receiver?: string // 收件人
    is_default?: boolean // 默认不起用其他邮箱
    mail_server?: string // 发件服务器
    mail_port?: string // 端口
    sender_mail?: string // 邮件账号
    password?: string // 邮件密码(需要使用密钥，存储的也是密钥名称)
    use_ssl?: boolean // 是否SSL
    cc?: string // 抄送
  }

  interface PhoneFormMap {
    is_enable?: boolean // 是否启用
    receiver?: string // 收件人手机号
    phone_msg_url?: string
  }

  interface MessageFormMap {
    email?: EmailFormMap
    phone_msg?: PhoneFormMap
  }

  interface VideoFormMap {
    cutTime: number | string
    enable: boolean
    // maxRecordingTime: number | string
    saveType: boolean
    fileClearTime: number | string
    filePath: string
    scene: string
  }
}
