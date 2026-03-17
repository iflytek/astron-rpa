import { getBaseURL } from './http/env'

export type OpenClawManagerProvider = {
  id: string
  auth_choice?: string
  api_key_flag?: string
  label: string
  api_key_label?: string | null
  requires_api_key: boolean
  supports_custom_model: boolean
}

export type OpenClawManagerCurrentConfig = {
  config_exists: boolean
  primary_model: string | null
  workspace: string
  providers: string[]
}

export type OpenClawManagerOptions = {
  docs_url: string
  providers: OpenClawManagerProvider[]
  current: OpenClawManagerCurrentConfig
}

export type OpenClawManagerOnboardPayload = {
  auth_choice: string
  api_key?: string
  custom_base_url?: string
  custom_model_id?: string
  custom_provider_id?: string
  custom_compatibility?: 'openai' | 'anthropic'
  secret_input_mode?: 'plaintext' | 'ref'
  restart_if_running?: boolean
}

export type OpenClawManagerOnboardResult = {
  configured: OpenClawManagerCurrentConfig
  restarted: boolean
  pid: number | null
  command: string[]
  stdout: string
  stderr: string
}

type OpenClawManagerResponse<T> = {
  code: number
  message: string
  data: T
}

export type OpenClawLaunchResult = {
  pid?: number | null
  args?: string[]
}

export function getOpenClawManagerBaseUrl() {
  return `${getBaseURL()}/openclaw`
}

async function requestOpenClawManager<T>(path: string, init?: RequestInit, acceptedCodes: number[] = [200]) {
  const response = await fetch(`${getOpenClawManagerBaseUrl()}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
  })

  let payload: OpenClawManagerResponse<T> | null = null

  try {
    payload = await response.json() as OpenClawManagerResponse<T>
  }
  catch {
    if (!response.ok)
      throw new Error(`请求失败 (${response.status})`)
  }

  if (!response.ok)
    throw new Error(payload?.message || `请求失败 (${response.status})`)

  if (!payload)
    throw new Error('OpenClaw 服务返回了空响应')

  if (!acceptedCodes.includes(payload.code))
    throw new Error(payload.message || 'OpenClaw 服务请求失败')

  return payload.data
}

export async function getOpenClawManagerOptions() {
  return await requestOpenClawManager<OpenClawManagerOptions>('/onboard/options', {
    method: 'GET',
  })
}

export async function getOpenClawManagerStatus() {
  return await requestOpenClawManager<{
    configured: OpenClawManagerCurrentConfig
    process_alive: boolean
    pid: number | null
  }>('/status', {
    method: 'GET',
  })
}

export async function submitOpenClawOnboard(payload: OpenClawManagerOnboardPayload) {
  return await requestOpenClawManager<OpenClawManagerOnboardResult>('/onboard', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function launchOpenClaw(args?: string[]) {
  return await requestOpenClawManager<OpenClawLaunchResult>('/launch', {
    method: 'POST',
    body: args ? JSON.stringify(args) : undefined,
  }, [200, 409])
}
