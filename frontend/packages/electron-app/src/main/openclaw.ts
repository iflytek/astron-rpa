import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { homedir } from 'node:os'
import logger from './log'

export interface OpenClawConfig {
  gateway?: {
    port?: number
    auth?: {
      mode?: string
      token?: string
    }
  }
}

/**
 * 读取 OpenClaw 配置文件
 * 默认路径: ~/.openclaw/openclaw.json
 */
export function readOpenClawConfig(): OpenClawConfig | null {
  try {
    const configPath = join(homedir(), '.openclaw', 'openclaw.json')
    const content = readFileSync(configPath, 'utf-8')
    const config = JSON.parse(content) as OpenClawConfig
    logger.info('OpenClaw config loaded successfully')
    return config
  } catch (error: any) {
    logger.warn(`Failed to read OpenClaw config: ${error?.message || 'unknown error'}`)
    return null
  }
}

/**
 * 从配置中提取 gateway token
 */
export function getOpenClawToken(): string | undefined {
  const config = readOpenClawConfig()
  return config?.gateway?.auth?.token
}
