import { mkdir, readFile, rename, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { randomUUID } from 'node:crypto'

import type {
  AssistantModelOverride,
  AssistantRecord,
  AssistantSessionRecord,
  AssistantToolPolicy,
  GroupRoomCollaborationMode,
  GroupRoomRecord,
  GroupRoomSessionRecord,
} from '../../shared/assistants'

export type SaveAssistantInput = {
  id?: string
  name?: string
  description?: string | null
  avatar?: string | null
  color?: string | null
  systemPrompt?: string | null
  defaultModel?: AssistantModelOverride | null
  skillIds?: string[]
  toolIds?: string[]
  toolPolicy?: AssistantToolPolicy
}

export type AssistantSessionCleanupResult = {
  removed: AssistantSessionRecord[]
  unmappedRuntimeSessionIds: string[]
}

export type DeleteAssistantResult = {
  assistant: AssistantRecord
  removedSessions: AssistantSessionRecord[]
}

export type GroupRoomSessionCleanupResult = {
  removed: GroupRoomSessionRecord[]
  unmappedRuntimeSessionIds: string[]
}

export type SaveGroupRoomInput = {
  id?: string
  name?: string
  description?: string | null
  memberAssistantIds?: string[]
  coordinatorPrompt?: string | null
  collaborationMode?: GroupRoomCollaborationMode
}

export type AssistantStore = {
  listAssistants: () => Promise<AssistantRecord[]>
  getAssistant: (id: string) => Promise<AssistantRecord | null>
  saveAssistant: (input: SaveAssistantInput) => Promise<AssistantRecord>
  deleteAssistant: (id: string) => Promise<DeleteAssistantResult | null>
  listAssistantSessions: () => Promise<AssistantSessionRecord[]>
  attachRuntimeSession: (assistantId: string, runtimeSessionId: string, title?: string | null) => Promise<AssistantSessionRecord>
  cleanupMissingRuntimeSessions: (runtimeSessionIds: string[]) => Promise<AssistantSessionCleanupResult>
  listGroupRooms: () => Promise<GroupRoomRecord[]>
  getGroupRoom: (id: string) => Promise<GroupRoomRecord | null>
  saveGroupRoom: (input: SaveGroupRoomInput) => Promise<GroupRoomRecord>
  deleteGroupRoom: (id: string) => Promise<GroupRoomRecord | null>
  listGroupRoomSessions: () => Promise<GroupRoomSessionRecord[]>
  attachGroupRoomSession: (groupRoomId: string, runtimeSessionId: string, title?: string | null) => Promise<GroupRoomSessionRecord>
  cleanupMissingGroupRoomSessions: (runtimeSessionIds: string[]) => Promise<GroupRoomSessionCleanupResult>
}

type AssistantStoreOptions = {
  storagePath: string | (() => string)
  now?: () => number
  createId?: () => string
}

type PersistedAssistantStore = {
  version: 1
  assistants: AssistantRecord[]
  assistantSessions: AssistantSessionRecord[]
  groupRooms: GroupRoomRecord[]
  groupRoomSessions: GroupRoomSessionRecord[]
}

export function createAssistantStore(options: AssistantStoreOptions): AssistantStore {
  const now = options.now ?? Date.now
  const createId = options.createId ?? (() => randomUUID())
  let writeQueue = Promise.resolve()

  return {
    listAssistants: async () => {
      const state = await readStoreState(resolveStoragePath(options.storagePath))
      return cloneAssistants(state.assistants)
    },
    getAssistant: async (id) => {
      const state = await readStoreState(resolveStoragePath(options.storagePath))
      return cloneAssistant(state.assistants.find((a) => a.id === id) ?? null)
    },
    saveAssistant: async (input) =>
      runSerialized(async () => {
        const storagePath = resolveStoragePath(options.storagePath)
        const state = await readStoreState(storagePath)
        const hasExplicitId = typeof input.id !== 'undefined'
        const requestedId = hasExplicitId ? normalizeRequiredText(input.id) : null
        const existingIndex = requestedId ? state.assistants.findIndex((a) => a.id === requestedId) : -1
        const existing = existingIndex >= 0 ? state.assistants[existingIndex] : null

        if (hasExplicitId && !existing) {
          throw new Error(`Unknown assistant: ${requestedId}`)
        }

        const assistant = existing
          ? updateAssistant(existing, input, now)
          : createAssistant(input, createId(), now)

        if (existingIndex >= 0) {
          state.assistants[existingIndex] = assistant
        }
        else {
          state.assistants.push(assistant)
        }

        await writeStoreState(storagePath, state)
        return cloneAssistant(assistant)!
      }),
    deleteAssistant: async (id) =>
      runSerialized(async () => {
        const storagePath = resolveStoragePath(options.storagePath)
        const state = await readStoreState(storagePath)
        const assistantIndex = state.assistants.findIndex((a) => a.id === id)
        if (assistantIndex < 0) {
          return null
        }

        const [removed] = state.assistants.splice(assistantIndex, 1)
        const removedSessions = state.assistantSessions.filter((s) => s.assistantId === id)
        state.assistantSessions = state.assistantSessions.filter((s) => s.assistantId !== id)
        state.groupRooms = state.groupRooms.map((room) =>
          room.memberAssistantIds.includes(id)
            ? { ...room, memberAssistantIds: room.memberAssistantIds.filter((aid) => aid !== id), updatedAt: isoTimestamp(now()) }
            : room,
        )

        await writeStoreState(storagePath, state)
        return { assistant: cloneAssistant(removed)!, removedSessions: cloneAssistantSessions(removedSessions) }
      }),
    listAssistantSessions: async () => {
      const state = await readStoreState(resolveStoragePath(options.storagePath))
      return cloneAssistantSessions(state.assistantSessions)
    },
    listGroupRooms: async () => {
      const state = await readStoreState(resolveStoragePath(options.storagePath))
      return cloneGroupRooms(state.groupRooms)
    },
    getGroupRoom: async (id) => {
      const state = await readStoreState(resolveStoragePath(options.storagePath))
      return cloneGroupRoom(state.groupRooms.find((r) => r.id === id) ?? null)
    },
    saveGroupRoom: async (input) =>
      runSerialized(async () => {
        const storagePath = resolveStoragePath(options.storagePath)
        const state = await readStoreState(storagePath)
        const hasExplicitId = typeof input.id !== 'undefined'
        const requestedId = hasExplicitId ? normalizeRequiredText(input.id) : null
        const existingIndex = requestedId ? state.groupRooms.findIndex((r) => r.id === requestedId) : -1
        const existing = existingIndex >= 0 ? state.groupRooms[existingIndex] : null

        if (hasExplicitId && !existing) {
          throw new Error(`Unknown group room: ${requestedId}`)
        }

        const room = existing ? updateGroupRoom(existing, input, now) : createGroupRoom(input, createId(), now)

        if (existingIndex >= 0) {
          state.groupRooms[existingIndex] = room
        }
        else {
          state.groupRooms.push(room)
        }

        await writeStoreState(storagePath, state)
        return cloneGroupRoom(room)!
      }),
    deleteGroupRoom: async (id) =>
      runSerialized(async () => {
        const storagePath = resolveStoragePath(options.storagePath)
        const state = await readStoreState(storagePath)
        const roomIndex = state.groupRooms.findIndex((r) => r.id === id)
        if (roomIndex < 0) {
          return null
        }

        const [removed] = state.groupRooms.splice(roomIndex, 1)
        state.groupRoomSessions = state.groupRoomSessions.filter((s) => s.groupRoomId !== id)

        await writeStoreState(storagePath, state)
        return cloneGroupRoom(removed)
      }),
    attachRuntimeSession: async (assistantId, runtimeSessionId, title) =>
      runSerialized(async () => {
        const storagePath = resolveStoragePath(options.storagePath)
        const normalizedRuntimeSessionId = normalizeRequiredText(runtimeSessionId)
        const state = await readStoreState(storagePath)
        const assistantExists = state.assistants.some((a) => a.id === assistantId)
        if (!assistantExists) {
          throw new Error(`Unknown assistant: ${assistantId}`)
        }

        const timestamp = isoTimestamp(now())
        const existingIndex = state.assistantSessions.findIndex((s) => s.runtimeSessionId === normalizedRuntimeSessionId)
        const existing = existingIndex >= 0 ? state.assistantSessions[existingIndex] : null
        const session = existing
          ? { ...existing, assistantId, title: normalizeNullableText(title), updatedAt: timestamp }
          : { id: createId(), assistantId, runtimeSessionId: normalizedRuntimeSessionId, title: normalizeNullableText(title), createdAt: timestamp, updatedAt: timestamp }

        if (existingIndex >= 0) {
          state.assistantSessions[existingIndex] = session
        }
        else {
          state.assistantSessions.push(session)
        }

        await writeStoreState(storagePath, state)
        return cloneAssistantSession(session)!
      }),
    listGroupRoomSessions: async () => {
      const state = await readStoreState(resolveStoragePath(options.storagePath))
      return cloneGroupRoomSessions(state.groupRoomSessions)
    },
    attachGroupRoomSession: async (groupRoomId, runtimeSessionId, title) =>
      runSerialized(async () => {
        const storagePath = resolveStoragePath(options.storagePath)
        const normalizedRuntimeSessionId = normalizeRequiredText(runtimeSessionId)
        const state = await readStoreState(storagePath)
        const roomExists = state.groupRooms.some((r) => r.id === groupRoomId)
        if (!roomExists) {
          throw new Error(`Unknown group room: ${groupRoomId}`)
        }

        const timestamp = isoTimestamp(now())
        const existingIndex = state.groupRoomSessions.findIndex((s) => s.runtimeSessionId === normalizedRuntimeSessionId)
        const existing = existingIndex >= 0 ? state.groupRoomSessions[existingIndex] : null
        const session = existing
          ? { ...existing, groupRoomId, title: normalizeNullableText(title), updatedAt: timestamp }
          : { id: createId(), groupRoomId, runtimeSessionId: normalizedRuntimeSessionId, title: normalizeNullableText(title), createdAt: timestamp, updatedAt: timestamp }

        if (existingIndex >= 0) {
          state.groupRoomSessions[existingIndex] = session
        }
        else {
          state.groupRoomSessions.push(session)
        }

        await writeStoreState(storagePath, state)
        return cloneGroupRoomSession(session)!
      }),
    cleanupMissingRuntimeSessions: async (runtimeSessionIds) =>
      runSerialized(async () => {
        const storagePath = resolveStoragePath(options.storagePath)
        const state = await readStoreState(storagePath)
        const liveIds = new Set(runtimeSessionIds.map((v) => v.trim()).filter(Boolean))
        const mappedIds = new Set(state.assistantSessions.map((s) => s.runtimeSessionId))
        const removed = state.assistantSessions.filter((s) => !liveIds.has(s.runtimeSessionId))
        state.assistantSessions = state.assistantSessions.filter((s) => liveIds.has(s.runtimeSessionId))
        await writeStoreState(storagePath, state)
        return { removed: cloneAssistantSessions(removed), unmappedRuntimeSessionIds: [...liveIds].filter((id) => !mappedIds.has(id)) }
      }),
    cleanupMissingGroupRoomSessions: async (runtimeSessionIds) =>
      runSerialized(async () => {
        const storagePath = resolveStoragePath(options.storagePath)
        const state = await readStoreState(storagePath)
        const liveIds = new Set(runtimeSessionIds.map((v) => v.trim()).filter(Boolean))
        const mappedIds = new Set(state.groupRoomSessions.map((s) => s.runtimeSessionId))
        const removed = state.groupRoomSessions.filter((s) => !liveIds.has(s.runtimeSessionId))
        state.groupRoomSessions = state.groupRoomSessions.filter((s) => liveIds.has(s.runtimeSessionId))
        await writeStoreState(storagePath, state)
        return { removed: cloneGroupRoomSessions(removed), unmappedRuntimeSessionIds: [...liveIds].filter((id) => !mappedIds.has(id)) }
      }),
  }

  function runSerialized<T>(task: () => Promise<T>) {
    const nextTask = writeQueue.then(task, task)
    writeQueue = nextTask.then(() => undefined, () => undefined)
    return nextTask
  }
}

async function readStoreState(storagePath: string): Promise<PersistedAssistantStore> {
  try {
    const raw = await readFile(storagePath, 'utf8')
    return validatePersistedStore(JSON.parse(raw))
  }
  catch (error) {
    if (isFileNotFound(error)) {
      return createEmptyStore()
    }

    throw new Error(`Unable to read assistant store at ${storagePath}`, { cause: error instanceof Error ? error : undefined })
  }
}

async function writeStoreState(storagePath: string, state: PersistedAssistantStore) {
  const directory = path.dirname(storagePath)
  const tempPath = `${storagePath}.tmp`

  await mkdir(directory, { recursive: true })
  await writeFile(tempPath, JSON.stringify(state, null, 2), 'utf8')
  await rename(tempPath, storagePath)
}

function resolveStoragePath(storagePath: string | (() => string)) {
  return typeof storagePath === 'function' ? storagePath() : storagePath
}

function validatePersistedStore(input: unknown): PersistedAssistantStore {
  if (!isRecord(input)) {
    return createEmptyStore()
  }

  const assistants = Array.isArray(input.assistants)
    ? input.assistants.map(validateAssistantRecord).filter((v): v is AssistantRecord => Boolean(v))
    : []
  const validAssistantIds = new Set(assistants.map((a) => a.id))
  const groupRooms = Array.isArray(input.groupRooms)
    ? input.groupRooms.map((r) => validateGroupRoomRecord(r, validAssistantIds)).filter((v): v is GroupRoomRecord => Boolean(v))
    : []
  const validGroupRoomIds = new Set(groupRooms.map((r) => r.id))

  return {
    version: 1,
    assistants,
    assistantSessions: Array.isArray(input.assistantSessions)
      ? input.assistantSessions
          .map(validateAssistantSessionRecord)
          .filter((v): v is AssistantSessionRecord => Boolean(v))
          .filter((v) => validAssistantIds.has(v.assistantId))
      : [],
    groupRooms,
    groupRoomSessions: Array.isArray(input.groupRoomSessions)
      ? input.groupRoomSessions
          .map(validateGroupRoomSessionRecord)
          .filter((v): v is GroupRoomSessionRecord => Boolean(v))
          .filter((v) => validGroupRoomIds.has(v.groupRoomId))
      : [],
  }
}

function validateAssistantRecord(input: unknown): AssistantRecord | null {
  try {
    if (!isRecord(input)) return null
    return {
      id: normalizeRequiredText(input.id),
      name: normalizeRequiredText(input.name),
      description: normalizeNullableText(input.description),
      avatar: normalizeNullableText(input.avatar),
      color: normalizeNullableText(input.color),
      systemPrompt: normalizeNullableText(input.systemPrompt),
      defaultModel: validateDefaultModel(input.defaultModel),
      skillIds: normalizeStringArray(input.skillIds),
      toolIds: normalizeStringArray(input.toolIds),
      toolPolicy: validateToolPolicy(input.toolPolicy),
      createdAt: normalizeRequiredText(input.createdAt),
      updatedAt: normalizeRequiredText(input.updatedAt),
    }
  }
  catch { return null }
}

function validateAssistantSessionRecord(input: unknown): AssistantSessionRecord | null {
  try {
    if (!isRecord(input)) return null
    return {
      id: normalizeRequiredText(input.id),
      assistantId: normalizeRequiredText(input.assistantId),
      runtimeSessionId: normalizeRequiredText(input.runtimeSessionId),
      title: normalizeNullableText(input.title),
      createdAt: normalizeRequiredText(input.createdAt),
      updatedAt: normalizeRequiredText(input.updatedAt),
    }
  }
  catch { return null }
}

function validateGroupRoomRecord(input: unknown, validAssistantIds: Set<string>): GroupRoomRecord | null {
  try {
    if (!isRecord(input)) return null
    return {
      id: normalizeRequiredText(input.id),
      name: normalizeRequiredText(input.name),
      description: normalizeNullableText(input.description),
      memberAssistantIds: normalizeStringArray(input.memberAssistantIds).filter((id) => validAssistantIds.has(id)),
      coordinatorPrompt: normalizeNullableText(input.coordinatorPrompt),
      collaborationMode: validateCollaborationMode(input.collaborationMode),
      createdAt: normalizeRequiredText(input.createdAt),
      updatedAt: normalizeRequiredText(input.updatedAt),
    }
  }
  catch { return null }
}

function validateGroupRoomSessionRecord(input: unknown): GroupRoomSessionRecord | null {
  try {
    if (!isRecord(input)) return null
    return {
      id: normalizeRequiredText(input.id),
      groupRoomId: normalizeRequiredText(input.groupRoomId),
      runtimeSessionId: normalizeRequiredText(input.runtimeSessionId),
      title: normalizeNullableText(input.title),
      createdAt: normalizeRequiredText(input.createdAt),
      updatedAt: normalizeRequiredText(input.updatedAt),
    }
  }
  catch { return null }
}

function validateDefaultModel(input: unknown): AssistantModelOverride | null {
  if (!isRecord(input)) return null
  const providerId = normalizeNullableText(input.providerId)
  const model = normalizeNullableText(input.model)
  if (!providerId || !model) return null
  return { providerId, model }
}

function validateToolPolicy(input: unknown): AssistantToolPolicy {
  if (input === 'assigned_only' || input === 'allow_assigned' || input === 'no_tools') return input
  return 'allow_assigned'
}

function validateCollaborationMode(input: unknown): GroupRoomCollaborationMode {
  if (input === 'auto' || input === 'pipeline' || input === 'race' || input === 'debate') return input
  return 'auto'
}

function createEmptyStore(): PersistedAssistantStore {
  return { version: 1, assistants: [], assistantSessions: [], groupRooms: [], groupRoomSessions: [] }
}

function createAssistant(input: SaveAssistantInput, id: string, now: () => number): AssistantRecord {
  const timestamp = isoTimestamp(now())
  const name = normalizeRequiredText(input.name)
  if (!name) throw new Error('Assistant name is required')
  return {
    id,
    name,
    description: normalizeNullableText(input.description),
    avatar: normalizeNullableText(input.avatar),
    color: normalizeNullableText(input.color),
    systemPrompt: normalizeNullableText(input.systemPrompt),
    defaultModel: normalizeDefaultModelInput(input.defaultModel),
    skillIds: normalizeStringArray(input.skillIds),
    toolIds: normalizeStringArray(input.toolIds),
    toolPolicy: validateToolPolicy(input.toolPolicy),
    createdAt: timestamp,
    updatedAt: timestamp,
  }
}

function updateAssistant(existing: AssistantRecord, input: SaveAssistantInput, now: () => number): AssistantRecord {
  return {
    ...existing,
    name: normalizeNullableText(input.name) ?? existing.name,
    description: typeof input.description === 'undefined' ? existing.description : normalizeNullableText(input.description),
    avatar: typeof input.avatar === 'undefined' ? existing.avatar : normalizeNullableText(input.avatar),
    color: typeof input.color === 'undefined' ? existing.color : normalizeNullableText(input.color),
    systemPrompt: typeof input.systemPrompt === 'undefined' ? existing.systemPrompt : normalizeNullableText(input.systemPrompt),
    defaultModel: typeof input.defaultModel === 'undefined' ? existing.defaultModel : normalizeDefaultModelInput(input.defaultModel),
    skillIds: typeof input.skillIds === 'undefined' ? existing.skillIds : normalizeStringArray(input.skillIds),
    toolIds: typeof input.toolIds === 'undefined' ? existing.toolIds : normalizeStringArray(input.toolIds),
    toolPolicy: validateToolPolicy(input.toolPolicy ?? existing.toolPolicy),
    updatedAt: isoTimestamp(now()),
  }
}

function createGroupRoom(input: SaveGroupRoomInput, id: string, now: () => number): GroupRoomRecord {
  const timestamp = isoTimestamp(now())
  const name = normalizeRequiredText(input.name)
  if (!name) throw new Error('Group room name is required')
  return {
    id,
    name,
    description: normalizeNullableText(input.description),
    memberAssistantIds: normalizeStringArray(input.memberAssistantIds),
    coordinatorPrompt: normalizeNullableText(input.coordinatorPrompt),
    collaborationMode: validateCollaborationMode(input.collaborationMode),
    createdAt: timestamp,
    updatedAt: timestamp,
  }
}

function updateGroupRoom(existing: GroupRoomRecord, input: SaveGroupRoomInput, now: () => number): GroupRoomRecord {
  return {
    ...existing,
    name: normalizeNullableText(input.name) ?? existing.name,
    description: typeof input.description === 'undefined' ? existing.description : normalizeNullableText(input.description),
    memberAssistantIds: typeof input.memberAssistantIds === 'undefined' ? existing.memberAssistantIds : normalizeStringArray(input.memberAssistantIds),
    coordinatorPrompt: typeof input.coordinatorPrompt === 'undefined' ? existing.coordinatorPrompt : normalizeNullableText(input.coordinatorPrompt),
    collaborationMode: validateCollaborationMode(input.collaborationMode ?? existing.collaborationMode),
    updatedAt: isoTimestamp(now()),
  }
}

function normalizeDefaultModelInput(input: AssistantModelOverride | null | undefined): AssistantModelOverride | null {
  if (!input) return null
  const providerId = normalizeRequiredText(input.providerId)
  const model = normalizeRequiredText(input.model)
  return { providerId, model }
}

function cloneAssistants(input: AssistantRecord[]) {
  return input.map((a) => cloneAssistant(a)!).sort((l, r) => r.updatedAt.localeCompare(l.updatedAt) || l.name.localeCompare(r.name))
}

function cloneAssistant(input: AssistantRecord | null) {
  return input ? structuredClone(input) : null
}

function cloneAssistantSessions(input: AssistantSessionRecord[]) {
  return input.map((s) => cloneAssistantSession(s)!).sort((l, r) => r.updatedAt.localeCompare(l.updatedAt))
}

function cloneAssistantSession(input: AssistantSessionRecord | null) {
  return input ? structuredClone(input) : null
}

function cloneGroupRooms(input: GroupRoomRecord[]) {
  return input.map((r) => cloneGroupRoom(r)!).sort((l, r) => r.updatedAt.localeCompare(l.updatedAt) || l.name.localeCompare(r.name))
}

function cloneGroupRoom(input: GroupRoomRecord | null) {
  return input ? structuredClone(input) : null
}

function cloneGroupRoomSessions(input: GroupRoomSessionRecord[]) {
  return input.map((s) => cloneGroupRoomSession(s)!).sort((l, r) => r.updatedAt.localeCompare(l.updatedAt))
}

function cloneGroupRoomSession(input: GroupRoomSessionRecord | null) {
  return input ? structuredClone(input) : null
}

function normalizeStringArray(input: unknown) {
  if (!Array.isArray(input)) return []
  const values = input.map(normalizeNullableText).filter((v): v is string => Boolean(v))
  return [...new Set(values)]
}

function normalizeNullableText(value: unknown) {
  return typeof value === 'string' && value.trim() ? value.trim() : null
}

function normalizeRequiredText(value: unknown) {
  const normalized = normalizeNullableText(value)
  if (!normalized) throw new Error('Expected a non-empty string')
  return normalized
}

function isoTimestamp(epochMs: number) {
  return new Date(epochMs).toISOString()
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
