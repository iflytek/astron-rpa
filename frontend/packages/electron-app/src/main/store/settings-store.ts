import { mkdir, readFile, rename, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { app } from 'electron'

import { getProviderDefinition, PROVIDER_REGISTRY } from '../../shared/provider-registry'
import { isProviderId } from '../../shared/settings'
import type {
  DesktopSettings,
  PersistedAppSettings,
  PersistedProviderSettings,
  ProviderId,
  SaveDefaultModelInput,
  SaveProviderInput,
} from '../../shared/settings'
import { createLogger } from '../opencode/logging'

const SETTINGS_FILENAME = 'opencode-settings.json'
const logger = createLogger('settings-store')

export type SettingsStore = {
  getSettings: () => Promise<DesktopSettings>
  getStoredSettings: () => Promise<PersistedAppSettings>
  saveProvider: (input: SaveProviderInput) => Promise<DesktopSettings>
  saveDefaultModel: (input: SaveDefaultModelInput) => Promise<DesktopSettings>
}

export function createSettingsStore(): SettingsStore {
  let writeQueue = Promise.resolve()

  return {
    getSettings: async () => redactSettings(await readSettingsFile()),
    getStoredSettings: async () => readSettingsFile(),
    saveProvider: async (input) =>
      runSerialized(async () => {
        const settings = await readSettingsFile()
        const providerId = assertProviderId(input.providerId)
        const definition = requireProviderDefinition(providerId)

        if (input.clear) {
          delete settings.providers[providerId]
          if (settings.defaultModel?.providerId === providerId) {
            settings.defaultModel = null
          }

          await writeSettingsFile(settings)
          return redactSettings(settings)
        }

        if (definition.status !== 'ready') {
          throw new Error(`${definition.name} 需要更复杂的接入方式，当前版本暂未开放。`)
        }
        if (definition.authMode !== 'api_key') {
          throw new Error(`${definition.name} 当前不支持通过此界面直接配置。`)
        }

        const existing = settings.providers[providerId]
        const nextApiKey = normalizeOptionalText(input.apiKey) ?? existing?.apiKey
        const nextModel = definition.supportsModel ? normalizeOptionalText(input.model) ?? existing?.model : null
        const nextBaseUrl = definition.supportsBaseUrl
          ? normalizeOptionalText(input.baseUrl) ?? existing?.baseUrl ?? null
          : existing?.baseUrl ?? null
        const nextDisplayName = definition.supportsDisplayName
          ? normalizeOptionalText(input.displayName) ?? existing?.displayName ?? definition.name
          : existing?.displayName ?? null

        if (!nextApiKey) {
          throw new Error(`保存 ${definition.name} 前需要填写 API 密钥。`)
        }
        if (definition.supportsModel && !nextModel) {
          throw new Error(`保存 ${definition.name} 前需要填写模型 ID。`)
        }
        if (definition.requiresBaseUrl && !nextBaseUrl) {
          throw new Error(`保存 ${definition.name} 前需要填写 Base URL。`)
        }

        settings.providers[providerId] = {
          apiKey: nextApiKey,
          baseUrl: nextBaseUrl,
          model: nextModel,
          displayName: nextDisplayName,
        }

        if (settings.defaultModel?.providerId === providerId && nextModel) {
          settings.defaultModel = { providerId, model: nextModel }
        }

        await writeSettingsFile(settings)
        return redactSettings(settings)
      }),
    saveDefaultModel: async (input) =>
      runSerialized(async () => {
        const settings = await readSettingsFile()
        const providerId = assertProviderId(input.providerId)
        const definition = requireProviderDefinition(providerId)
        const model = normalizeRequiredText(input.model, '默认模型不能为空。')

        if (definition.status !== 'ready') {
          throw new Error(`${definition.name} 当前还不能作为默认模型来源。`)
        }
        if (!settings.providers[providerId]?.apiKey) {
          throw new Error(`请先配置 ${definition.name}，再将其设为默认模型服务商。`)
        }
        if (settings.providers[providerId]?.model !== model) {
          throw new Error(`${definition.name} 的默认模型必须与已保存的服务商模型一致。`)
        }

        settings.defaultModel = { providerId, model }

        await writeSettingsFile(settings)
        return redactSettings(settings)
      }),
  }

  function runSerialized<T>(task: () => Promise<T>) {
    const nextTask = writeQueue.then(task, task)
    writeQueue = nextTask.then(() => undefined, () => undefined)
    return nextTask
  }
}

function getSettingsFilePath() {
  return path.join(app.getPath('userData'), SETTINGS_FILENAME)
}

async function readSettingsFile() {
  const filepath = getSettingsFilePath()

  try {
    const raw = await readFile(filepath, 'utf8')
    return parsePersistedSettings(raw, filepath)
  }
  catch (error) {
    if (isFileNotFound(error)) {
      return cloneDefaultSettings()
    }

    logger.warn('failed to read persisted settings', error instanceof Error ? error : String(error))
    throw createSettingsReadError(filepath, error)
  }
}

async function writeSettingsFile(settings: PersistedAppSettings) {
  const filepath = getSettingsFilePath()
  const directory = path.dirname(filepath)
  const tempPath = `${filepath}.tmp`
  const normalized = normalizePersistedSettings(settings)

  await mkdir(directory, { recursive: true })
  await writeFile(tempPath, JSON.stringify(normalized, null, 2), 'utf8')
  await rename(tempPath, filepath)
}

function normalizePersistedSettings(input: unknown): PersistedAppSettings {
  if (!isRecord(input)) {
    return cloneDefaultSettings()
  }

  const providers = isRecord(input.providers)
    ? Object.entries(input.providers).reduce<Record<ProviderId, PersistedProviderSettings>>(
        (result, [providerId, providerSettings]) => {
          if (!isProviderId(providerId) || !isRecord(providerSettings)) {
            return result
          }

          const apiKey = normalizeOptionalText(providerSettings.apiKey)
          if (!apiKey) {
            return result
          }

          result[providerId] = {
            apiKey,
            baseUrl: normalizeOptionalText(providerSettings.baseUrl) ?? null,
            model: normalizeOptionalText(providerSettings.model) ?? null,
            displayName: normalizeOptionalText(providerSettings.displayName) ?? null,
          }
          return result
        },
        {},
      )
    : {}

  return {
    version: 1,
    providers,
    defaultModel: normalizeDefaultModel(input.defaultModel, providers),
  }
}

function parsePersistedSettings(raw: string, filepath: string) {
  let parsed: unknown
  try {
    parsed = JSON.parse(raw)
  }
  catch (error) {
    throw createSettingsReadError(filepath, error)
  }

  try {
    return validatePersistedSettings(parsed)
  }
  catch (error) {
    throw createSettingsReadError(filepath, error)
  }
}

function validatePersistedSettings(input: unknown): PersistedAppSettings {
  if (!isRecord(input)) {
    throw new Error('设置文件必须是一个 JSON 格式的对象。')
  }

  const providers = validateProviders(input.providers)
  const defaultModel = validateDefaultModel(input.defaultModel, providers)

  return { version: 1, providers, defaultModel }
}

function validateProviders(input: unknown): Record<ProviderId, PersistedProviderSettings> {
  if (typeof input === 'undefined') return {}
  if (!isRecord(input)) throw new Error('设置文件中的 providers 字段必须是一个对象。')

  return Object.entries(input).reduce<Record<ProviderId, PersistedProviderSettings>>((result, [providerId, value]) => {
    if (!isProviderId(providerId)) {
      throw new Error(`设置中包含不支持的服务商：${providerId}`)
    }
    if (!isRecord(value)) {
      throw new Error(`${providerId} 的服务商配置必须是一个对象。`)
    }

    const definition = requireProviderDefinition(providerId)
    const apiKey = normalizeOptionalText(value.apiKey)
    const model = normalizeOptionalText(value.model)
    const displayName = normalizeOptionalText(value.displayName)

    if (!apiKey) throw new Error(`服务商 ${providerId} 缺少已保存的 API 密钥。`)
    if (definition.supportsModel && !model) throw new Error(`服务商 ${providerId} 缺少已保存的模型 ID。`)
    if (definition.requiresBaseUrl && !normalizeOptionalText(value.baseUrl)) {
      throw new Error(`服务商 ${providerId} 缺少已保存的 Base URL。`)
    }

    result[providerId] = {
      apiKey,
      baseUrl: normalizeOptionalText(value.baseUrl) ?? null,
      model: model ?? null,
      displayName: displayName ?? null,
    }
    return result
  }, {})
}

function validateDefaultModel(
  input: unknown,
  providers: Record<ProviderId, PersistedProviderSettings>,
): PersistedAppSettings['defaultModel'] {
  if (typeof input === 'undefined' || input === null) return null
  if (!isRecord(input) || !isProviderId(String(input.providerId))) {
    throw new Error('默认模型必须包含受支持的服务商 ID。')
  }

  const providerId = input.providerId as ProviderId
  const model = normalizeOptionalText(input.model)
  if (!model) throw new Error('默认模型缺少模型 ID。')
  if (!providers[providerId]?.apiKey) throw new Error(`默认模型引用了尚未配置的服务商 ${providerId}。`)
  if (providers[providerId]?.model !== model) throw new Error(`${providerId} 的默认模型必须与已保存的服务商模型一致。`)

  return { providerId, model }
}

function normalizeDefaultModel(
  input: unknown,
  providers: Record<ProviderId, PersistedProviderSettings>,
): PersistedAppSettings['defaultModel'] {
  if (!isRecord(input) || !isProviderId(String(input.providerId))) return null
  const providerId = input.providerId as ProviderId
  const model = normalizeOptionalText(input.model)
  if (!model || !providers[providerId]?.apiKey) return null
  return { providerId, model }
}

function redactSettings(settings: PersistedAppSettings): DesktopSettings {
  return {
    providers: PROVIDER_REGISTRY.map((definition) => {
      const providerSettings = settings.providers[definition.id]
      return {
        providerId: definition.id,
        label: providerSettings?.displayName || definition.name,
        configured: Boolean(providerSettings?.apiKey),
        apiKeyHint: providerSettings?.apiKey ? maskApiKey(providerSettings.apiKey) : null,
        baseUrl: providerSettings?.baseUrl ?? null,
        hasBaseUrl: Boolean(providerSettings?.baseUrl),
        model: providerSettings?.model ?? null,
        displayName: providerSettings?.displayName ?? null,
      }
    }),
    defaultModel: {
      providerId: settings.defaultModel?.providerId ?? null,
      model: settings.defaultModel?.model ?? '',
      configured: Boolean(settings.defaultModel),
    },
  }
}

function cloneDefaultSettings(): PersistedAppSettings {
  return { version: 1, providers: {}, defaultModel: null }
}

function createSettingsReadError(filepath: string, cause: unknown) {
  return new Error(`无法安全读取已保存的设置文件：${filepath}。请先修复或删除该文件，再继续保存设置。`, {
    cause: cause instanceof Error ? cause : undefined,
  })
}

function maskApiKey(value: string) {
  const visible = value.slice(-4)
  return visible ? `已保存密钥，尾号 ${visible}` : '已保存密钥'
}

function assertProviderId(providerId: string): ProviderId {
  if (!isProviderId(providerId)) {
    throw new Error(`不支持的服务商：${providerId}`)
  }

  return providerId
}

function requireProviderDefinition(providerId: string) {
  const definition = getProviderDefinition(providerId)
  if (!definition) {
    throw new Error(`不支持的服务商：${providerId}`)
  }
  return definition
}

function normalizeOptionalText(value: unknown) {
  return typeof value === 'string' && value.trim() ? value.trim() : null
}

function normalizeRequiredText(value: unknown, message: string) {
  const normalized = normalizeOptionalText(value)
  if (!normalized) throw new Error(message)
  return normalized
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value)
}

function isFileNotFound(error: unknown) {
  return (
    typeof error === 'object' &&
    error !== null &&
    'code' in error &&
    typeof (error as { code?: unknown }).code === 'string' &&
    (error as { code?: string }).code === 'ENOENT'
  )
}
