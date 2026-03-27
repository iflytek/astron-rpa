import type { AssistantRecord, GroupRoomRecord } from '../../shared/assistants'
import { getProviderDefinition } from '../../shared/provider-registry'
import { SETTINGS_SCHEMA_URL, type PersistedAppSettings } from '../../shared/settings'

type NativeRuntimeProviderConfig = {
  options: {
    apiKey: string
    baseURL?: string
  }
}

type OpenAiCompatibleRuntimeProviderConfig = {
  npm: "@ai-sdk/openai-compatible"
  name: string
  options: {
    apiKey: string
    baseURL: string
  }
  models: Record<string, { name: string }>
}

type RuntimeProviderConfig = NativeRuntimeProviderConfig | OpenAiCompatibleRuntimeProviderConfig

export function buildRuntimeConfigContent(
  settings: PersistedAppSettings,
  assistants: AssistantRecord[] = [],
  groupRooms: GroupRoomRecord[] = [],
) {
  const provider = Object.entries(settings.providers).reduce<Record<string, RuntimeProviderConfig>>(
    (result, [providerId, providerSettings]) => {
      if (!providerSettings?.apiKey) {
        return result
      }

      const definition = getProviderDefinition(providerId)
      if (!definition || definition.status !== 'ready') {
        return result
      }

      if (definition.adapter === 'openai-compatible') {
        if (!providerSettings.baseUrl || !providerSettings.model) {
          return result
        }

        result[providerId] = {
          npm: '@ai-sdk/openai-compatible',
          name: providerSettings.displayName || definition.name,
          options: {
            apiKey: providerSettings.apiKey,
            baseURL: providerSettings.baseUrl,
          },
          models: {
            [providerSettings.model]: { name: providerSettings.model },
          },
        }
        return result
      }

      result[providerId] = {
        options: {
          apiKey: providerSettings.apiKey,
          ...(providerSettings.baseUrl ? { baseURL: providerSettings.baseUrl } : {}),
        },
      }
      return result
    },
    {},
  )

  const assistantsById = new Map(assistants.map((assistant) => [assistant.id, assistant]))
  const agent = {
    ...assistants.reduce<Record<string, Record<string, unknown>>>((result, assistant) => {
      const shared = buildAssistantAgentBase(assistant)
      result[buildAssistantDirectAgentName(assistant.id)] = {
        ...shared,
        mode: 'all',
        hidden: true,
      }
      result[buildAssistantWorkerAgentName(assistant.id)] = {
        ...shared,
        mode: 'subagent',
        hidden: true,
      }
      return result
    }, {}),
    ...groupRooms.reduce<Record<string, Record<string, unknown>>>((result, room) => {
      result[buildRoomCoordinatorAgentName(room.id)] = buildRoomCoordinatorAgent(room, assistantsById)
      return result
    }, {}),
  }

  const config = {
    $schema: SETTINGS_SCHEMA_URL,
    ...(settings.defaultModel
      ? { model: `${settings.defaultModel.providerId}/${settings.defaultModel.model}` }
      : {}),
    ...(Object.keys(provider).length > 0 ? { provider } : {}),
    ...(Object.keys(agent).length > 0 ? { agent } : {}),
  }

  return JSON.stringify(config)
}

export function buildAssistantDirectAgentName(assistantId: string) {
  return `assistant-direct-${assistantId}`
}

export function buildAssistantWorkerAgentName(assistantId: string) {
  return `assistant-worker-${assistantId}`
}

export function buildRoomCoordinatorAgentName(roomId: string) {
  return `room-coordinator-${roomId}`
}

function buildAssistantAgentBase(assistant: AssistantRecord) {
  return {
    ...(assistant.description ? { description: assistant.description } : {}),
    ...(assistant.systemPrompt ? { prompt: assistant.systemPrompt } : {}),
    ...(assistant.defaultModel
      ? { model: `${assistant.defaultModel.providerId}/${assistant.defaultModel.model}` }
      : {}),
    permission: {
      skill: buildAssistantSkillPermission(assistant.skillIds),
    },
  }
}

function buildRoomCoordinatorAgent(room: GroupRoomRecord, assistantsById: Map<string, AssistantRecord>) {
  const members = room.memberAssistantIds
    .map((assistantId) => assistantsById.get(assistantId))
    .filter((assistant): assistant is AssistantRecord => Boolean(assistant))

  return {
    ...(room.description ? { description: room.description } : {}),
    mode: 'all',
    hidden: true,
    prompt: buildRoomCoordinatorPrompt(room, members),
    permission: {
      task: Object.fromEntries(
        members.map((assistant) => [buildAssistantWorkerAgentName(assistant.id), 'allow' as const]),
      ),
    },
  }
}

function buildRoomCoordinatorPrompt(room: GroupRoomRecord, members: AssistantRecord[]) {
  const lines = [`You coordinate a collaborative room named ${room.name}.`]

  if (room.description) {
    lines.push(`Room objective: ${room.description}`)
  }

  if (members.length > 0) {
    lines.push('Available members:')
    for (const assistant of members) {
      lines.push(`- ${assistant.name}: ${assistant.description ?? 'Specialized assistant.'}`)
    }
  }

  if (room.coordinatorPrompt) {
    lines.push(room.coordinatorPrompt)
  }

  lines.push('Delegate only when helpful. Prefer the fewest useful assistants.')
  lines.push('When delegating, use the task tool with these subagent types:')
  for (const assistant of members) {
    lines.push(`- ${buildAssistantWorkerAgentName(assistant.id)}`)
  }
  lines.push('Always synthesize delegated results into one clear reply for the user.')

  return lines.join('\n')
}

function buildAssistantSkillPermission(skillIds: string[]) {
  const permission: Record<string, 'allow' | 'deny'> = { '*': 'deny' }

  for (const skillName of skillIds.map(extractSkillName).filter((value): value is string => Boolean(value))) {
    permission[skillName] = 'allow'
  }

  return permission
}

function extractSkillName(skillId: string) {
  const [skillName] = skillId.split('::', 1)
  const normalized = skillName?.trim()
  return normalized || null
}
