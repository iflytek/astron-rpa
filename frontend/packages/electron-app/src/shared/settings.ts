import { isProviderId } from './provider-registry'

export const SETTINGS_SCHEMA_URL = "https://opencode.ai/config.json"

export type ProviderId = string

export type ModelSelection = {
  providerId: ProviderId
  model: string
}

export type PersistedProviderSettings = {
  apiKey: string
  baseUrl: string | null
  model: string | null
  displayName: string | null
}

export type PersistedDefaultModel = ModelSelection

export type SessionModelOverrideRecord = ModelSelection & {
  sessionID: string
  updatedAt: string
}

export type PersistedAppSettings = {
  version: 1
  providers: Record<ProviderId, PersistedProviderSettings>
  defaultModel: PersistedDefaultModel | null
}

export type ProviderSummary = {
  providerId: ProviderId
  label: string
  configured: boolean
  apiKeyHint: string | null
  baseUrl: string | null
  hasBaseUrl: boolean
  model: string | null
  displayName: string | null
}

export type DesktopSettings = {
  providers: ProviderSummary[]
  defaultModel: {
    providerId: ProviderId | null
    model: string
    configured: boolean
  }
}

export type SaveProviderInput = {
  providerId: ProviderId
  apiKey?: string | null
  model?: string | null
  baseUrl?: string | null
  displayName?: string | null
  clear?: boolean
}

export type SaveDefaultModelInput = ModelSelection

export { isProviderId }
