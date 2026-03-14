export type AstronAssistantFeishuConfig = {
  enabled: boolean
  botName: string
  appId: string
  appSecret: string
  domain: 'feishu' | 'lark'
  connectionMode: 'websocket' | 'webhook'
  verificationToken: string
  encryptKey: string
  webhookHost: string
  webhookPort: number
  webhookPath: string
}

export const DEFAULT_FEISHU_CONFIG: AstronAssistantFeishuConfig = {
  enabled: false,
  botName: 'Astron助手',
  appId: '',
  appSecret: '',
  domain: 'feishu',
  connectionMode: 'websocket',
  verificationToken: '',
  encryptKey: '',
  webhookHost: '127.0.0.1',
  webhookPort: 3000,
  webhookPath: '/feishu/events',
}

type UserSettingLike = Record<string, any>

export function readFeishuConfigFromSetting(setting: UserSettingLike | null | undefined): AstronAssistantFeishuConfig {
  const raw = setting?.astronAssistant?.feishu ?? {}
  return {
    ...DEFAULT_FEISHU_CONFIG,
    ...raw,
  }
}

export function mergeFeishuConfigIntoSetting(
  setting: UserSettingLike | null | undefined,
  feishu: AstronAssistantFeishuConfig,
): UserSettingLike {
  return {
    ...(setting ?? {}),
    astronAssistant: {
      ...((setting as UserSettingLike | undefined)?.astronAssistant ?? {}),
      feishu,
    },
  }
}

export function buildOpenClawFeishuConfig(feishu: AstronAssistantFeishuConfig) {
  const account = {
    appId: feishu.appId,
    appSecret: feishu.appSecret,
    botName: feishu.botName,
    domain: feishu.domain,
  } as Record<string, any>

  if (feishu.connectionMode === 'webhook') {
    account.verificationToken = feishu.verificationToken
    account.encryptKey = feishu.encryptKey
    account.webhookHost = feishu.webhookHost
    account.webhookPort = feishu.webhookPort
    account.webhookPath = feishu.webhookPath
  }

  return {
    channels: {
      feishu: {
        enabled: feishu.enabled,
        connectionMode: feishu.connectionMode,
        domain: feishu.domain,
        accounts: {
          main: account,
        },
      },
    },
  }
}
