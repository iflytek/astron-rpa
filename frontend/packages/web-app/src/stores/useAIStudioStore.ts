import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { nanoid } from 'nanoid'

import { DEFAULT_AI_STUDIO_SESSION_ID } from '@/views/AIStudio/contracts'
import { createSessionDetailTemplate } from '@/views/AIStudio/mock'
import { mockAIStudioProvider } from '@/views/AIStudio/providers/mockProvider'
import { getOpencodeDesktopApi, opencodeAIStudioProvider } from '@/views/AIStudio/providers/opencodeProvider'

import type {
  AIStudioCardActionPayload,
  AIStudioChoiceSubmissionPayload,
  AIStudioParamSubmissionPayload,
  AIStudioSendMessagePayload,
  AIStudioSessionMutationResult,
} from '@/views/AIStudio/contracts'
import type {
  StudioAssistant,
  StudioAssistantGroup,
  StudioCollaborationMode,
  StudioSession,
  StudioSessionDetail,
} from '@/views/AIStudio/types'

const IS_MOCK_MODE = typeof window !== 'undefined' && !('opencodeApi' in window)
const provider = IS_MOCK_MODE ? mockAIStudioProvider : opencodeAIStudioProvider
const INITIAL_SESSION_ID = IS_MOCK_MODE ? DEFAULT_AI_STUDIO_SESSION_ID : ''

type PendingMutation = {
  sessionId: string
  kind: 'message' | 'choice' | 'param' | 'action'
  cardId?: string
  actionId?: string
} | null

type CreateSessionPayload = {
  workspacePath: string
  sessionTitle?: string
}

type CreateAssistantPayload = {
  name: string
  persona?: string
  capabilities?: string
  skills?: string[]
  templateKind?: 'assistant' | 'group'
  groupParticipantAssistantIds?: string[]
  groupCollaborationMode?: StudioCollaborationMode
}

function cloneGroups(groups: StudioAssistantGroup[]) {
  return groups.map(group => ({
    ...group,
    assistants: group.assistants.map(assistant => ({
      ...assistant,
      sessions: assistant.sessions.map(session => ({ ...session })),
    })),
  }))
}

function extractSessionIds(groups: StudioAssistantGroup[]) {
  return new Set(
    groups.flatMap(group =>
      group.assistants.flatMap(assistant => assistant.sessions.map(session => session.id)),
    ),
  )
}

function normalizeSessionDetail(detail: StudioSessionDetail): StudioSessionDetail {
  return {
    ...detail,
    selectedArtifactId: detail.selectedArtifactId || detail.artifacts[0]?.id,
  }
}

export const useAIStudioStore = defineStore('aiStudio', () => {
  const assistantGroups = ref<StudioAssistantGroup[]>([])
  const sessionMap = ref<Record<string, StudioSessionDetail>>({})
  const activeSessionId = ref(INITIAL_SESSION_ID)
  const activeSurface = ref<'main' | 'automation' | 'settings'>('main')
  const workspaceOpen = ref(false)
  const invitedAssistants = ref<string[]>([])
  const showNewAssistant = ref(false)
  const assistantModalMode = ref<'create' | 'edit'>('create')
  const assistantTemplateKind = ref<'assistant' | 'group'>('assistant')
  const editingAssistantId = ref<string | null>(null)
  const showInviteAssistant = ref(false)
  const showNewSession = ref(false)
  const newSessionAssistantId = ref<string | null>(null)
  const initialized = ref(false)
  const loading = ref(false)
  const errorMessage = ref('')
  const pendingMutation = ref<PendingMutation>(null)
  const isAiTyping = ref(false)

  const activeSession = computed(() => {
    return sessionMap.value[activeSessionId.value]
      || (INITIAL_SESSION_ID ? sessionMap.value[INITIAL_SESSION_ID] : undefined)
      || Object.values(sessionMap.value)[0]
      || null
  })

  const newSessionAssistant = computed(() => {
    if (!newSessionAssistantId.value)
      return null
    for (const group of assistantGroups.value) {
      const assistant = group.assistants.find(item => item.id === newSessionAssistantId.value)
      if (assistant)
        return assistant
    }
    return null
  })
  const newSessionParticipantCandidates = computed(() => {
    const singleGroup = assistantGroups.value.find(group => group.id === 'single')
    return (singleGroup?.assistants || []).map(assistant => ({
      id: assistant.id,
      name: assistant.name,
      badge: assistant.badge,
    }))
  })

  const isActiveSessionPending = computed(() => pendingMutation.value?.sessionId === activeSessionId.value)
  const editingAssistant = computed(() => {
    if (!editingAssistantId.value)
      return null
    return findAssistantById(editingAssistantId.value)
  })

  function listAllSessions() {
    return assistantGroups.value.flatMap(group =>
      group.assistants.flatMap(assistant =>
        assistant.sessions.map(session => ({
          assistantId: assistant.id,
          sessionId: session.id,
          session,
        })),
      ),
    )
  }

  function findAssistantById(assistantId: string) {
    for (const group of assistantGroups.value) {
      const assistant = group.assistants.find(item => item.id === assistantId)
      if (assistant)
        return assistant
    }
    return null
  }

  function getAssistantSessionIds(assistantId: string) {
    return findAssistantById(assistantId)?.sessions.map(session => session.id) || []
  }

  function getFirstAvailableSessionId(preferredAssistantId?: string) {
    if (preferredAssistantId) {
      const preferredSessionId = getAssistantSessionIds(preferredAssistantId)[0]
      if (preferredSessionId)
        return preferredSessionId
    }

    return listAllSessions()[0]?.sessionId || ''
  }

  function updateSessionDetail(detail: StudioSessionDetail) {
    const previous = sessionMap.value[detail.id]
    const next = normalizeSessionDetail({
      ...detail,
      selectedArtifactId: detail.selectedArtifactId || previous?.selectedArtifactId,
    })
    sessionMap.value = {
      ...sessionMap.value,
      [next.id]: next,
    }
    return next
  }

  function mutateSessionDetail(sessionId: string, mapper: (session: StudioSessionDetail) => StudioSessionDetail) {
    const current = sessionMap.value[sessionId]
    if (!current)
      return
    updateSessionDetail(mapper(current))
  }

  function mutateAssistant(assistantId: string, mapper: (assistant: StudioAssistant) => StudioAssistant) {
    assistantGroups.value = assistantGroups.value.map(group => ({
      ...group,
      assistants: group.assistants.map(assistant => assistant.id === assistantId ? mapper(assistant) : assistant),
    }))
  }

  function markSessionActive(sessionId: string) {
    assistantGroups.value = assistantGroups.value.map(group => ({
      ...group,
      assistants: group.assistants.map(assistant => ({
        ...assistant,
        sessions: assistant.sessions.map(session => ({
          ...session,
          active: session.id === sessionId,
        })),
      })),
    }))
  }

  async function refreshBootstrap(preferredSessionId = activeSessionId.value) {
    const bootstrap = await provider.getBootstrap()
    const nextGroups = cloneGroups(bootstrap.assistantGroups)
    const availableSessionIds = extractSessionIds(nextGroups)
    const nextSessionId = preferredSessionId && availableSessionIds.has(preferredSessionId)
      ? preferredSessionId
      : bootstrap.defaultSessionId || [...availableSessionIds][0] || INITIAL_SESSION_ID

    assistantGroups.value = nextGroups
    activeSessionId.value = nextSessionId

    if (!nextSessionId) {
      sessionMap.value = {}
      return null
    }

    if (!sessionMap.value[nextSessionId])
      await loadSessionDetail(nextSessionId, { force: true })
    markSessionActive(nextSessionId)
    return nextSessionId
  }

  function touchSession(sessionId: string) {
    assistantGroups.value = assistantGroups.value.map(group => ({
      ...group,
      assistants: group.assistants.map(assistant => ({
        ...assistant,
        sessions: assistant.sessions.map(session => ({
          ...session,
          active: session.id === sessionId,
          time: session.id === sessionId ? '刚刚' : session.time,
        })),
      })),
    }))
  }

  async function loadSessionDetail(sessionId: string, options: { force?: boolean } = {}) {
    if (!options.force && sessionMap.value[sessionId])
      return sessionMap.value[sessionId]

    const detail = await provider.getSessionDetail(sessionId)
    return updateSessionDetail(detail)
  }

  async function runMutation(meta: NonNullable<PendingMutation>, task: () => Promise<AIStudioSessionMutationResult>) {
    pendingMutation.value = meta
    errorMessage.value = ''

    try {
      const result = await task()
      const session = updateSessionDetail(result.session)
      touchSession(session.id)
      markSessionActive(session.id)
      return session
    }
    catch (error) {
      errorMessage.value = error instanceof Error ? error.message : 'AI Studio 交互提交失败'
      throw error
    }
    finally {
      pendingMutation.value = null
    }
  }

  async function ensureInitialized(sessionId = INITIAL_SESSION_ID) {
    loading.value = true
    errorMessage.value = ''

    try {
      if (!initialized.value) {
        const bootstrap = await provider.getBootstrap()
        assistantGroups.value = cloneGroups(bootstrap.assistantGroups)
        activeSessionId.value = sessionId || bootstrap.defaultSessionId || INITIAL_SESSION_ID
        initialized.value = true
      }
      else {
        activeSessionId.value = sessionId || activeSessionId.value || INITIAL_SESSION_ID
      }

      if (activeSessionId.value) {
        await loadSessionDetail(activeSessionId.value)
        markSessionActive(activeSessionId.value)
      }
    }
    catch (error) {
      errorMessage.value = error instanceof Error ? error.message : 'AI Studio 数据初始化失败'
    }
    finally {
      loading.value = false
    }
  }

  async function setActiveSession(sessionId: string) {
    activeSessionId.value = sessionId || INITIAL_SESSION_ID
    workspaceOpen.value = false
    invitedAssistants.value = []
    isAiTyping.value = false
    if (!activeSessionId.value)
      return
    await loadSessionDetail(activeSessionId.value)
    markSessionActive(activeSessionId.value)
  }

  function openSurface(surface: 'main' | 'automation' | 'settings') {
    activeSurface.value = surface
  }

  function toggleWorkspace() {
    workspaceOpen.value = !workspaceOpen.value
  }

  function setWorkspaceOpen(value: boolean) {
    workspaceOpen.value = value
  }

  function openNewAssistant() {
    assistantModalMode.value = 'create'
    assistantTemplateKind.value = 'assistant'
    editingAssistantId.value = null
    showNewAssistant.value = true
  }

  function openNewGroupTemplate() {
    assistantModalMode.value = 'create'
    assistantTemplateKind.value = 'group'
    editingAssistantId.value = null
    showNewAssistant.value = true
  }

  function openEditAssistant(assistantId: string) {
    assistantModalMode.value = 'edit'
    editingAssistantId.value = assistantId
    assistantTemplateKind.value = findAssistantById(assistantId)?.status === '群聊' ? 'group' : 'assistant'
    showNewAssistant.value = true
  }

  function closeNewAssistant() {
    showNewAssistant.value = false
    assistantModalMode.value = 'create'
    assistantTemplateKind.value = 'assistant'
    editingAssistantId.value = null
  }

  function openInviteAssistant() {
    showInviteAssistant.value = true
  }

  function closeInviteAssistant() {
    showInviteAssistant.value = false
  }

  function openNewSession(assistantId: string) {
    newSessionAssistantId.value = assistantId
    showNewSession.value = true
  }

  function closeNewSession() {
    showNewSession.value = false
    newSessionAssistantId.value = null
  }

  function inviteAssistants(ids: string[]) {
    invitedAssistants.value = [...new Set([...invitedAssistants.value, ...ids])]
    showInviteAssistant.value = false
  }

  function deriveSessionTitleFromWorkspace(workspacePath: string, assistantName: string) {
    const normalized = workspacePath.trim().replace(/\\/g, '/').replace(/\/+$/, '')
    const segment = normalized.split('/').filter(Boolean).pop()
    if (!segment || segment === '~' || ['Documents', 'Desktop', 'Downloads'].includes(segment))
      return `${assistantName}新会话`
    return segment
  }

  function updateAssistantSessionDetails(
    assistantId: string,
    updater: (detail: StudioSessionDetail) => StudioSessionDetail,
  ) {
    const sessionIds = new Set(getAssistantSessionIds(assistantId))
    sessionMap.value = Object.fromEntries(
      Object.entries(sessionMap.value).map(([key, detail]) => [
        key,
        sessionIds.has(key) ? normalizeSessionDetail(updater(detail)) : detail,
      ]),
    )
  }

  async function createAssistant(payload: CreateAssistantPayload) {
    const name = payload.name.trim()
    const isGroupTemplate = payload.templateKind === 'group'
    if (!IS_MOCK_MODE) {
      const api = getOpencodeDesktopApi()
      if (isGroupTemplate) {
        const saved = await api.saveGroupRoom({
          name,
          description: payload.capabilities?.trim() || null,
          coordinatorPrompt: payload.persona?.trim() || null,
          memberAssistantIds: [...new Set((payload.groupParticipantAssistantIds || []).filter(Boolean))],
          collaborationMode: payload.groupCollaborationMode || 'auto',
        }) as { id: string }
        await refreshBootstrap()
        activeSurface.value = 'main'
        workspaceOpen.value = false
        closeNewAssistant()
        return { assistantId: saved.id }
      }

      const saved = await api.saveAssistant({
        name,
        description: payload.capabilities?.trim() || null,
        systemPrompt: payload.persona?.trim() || null,
        skillIds: payload.skills || [],
      }) as { id: string }
      await refreshBootstrap()
      activeSurface.value = 'main'
      workspaceOpen.value = false
      closeNewAssistant()
      return { assistantId: saved.id }
    }

    const assistantId = nanoid(8)
    const badge = name.slice(0, 1) || (payload.templateKind === 'group' ? '群' : '助')
    const normalizedGroupParticipants = isGroupTemplate
      ? [...new Set((payload.groupParticipantAssistantIds || []).filter(Boolean))]
      : undefined
    const assistant: StudioAssistant = {
      id: assistantId,
      name,
      badge,
      status: isGroupTemplate ? '群聊' : '待命',
      tag: isGroupTemplate ? '群聊' : undefined,
      persona: payload.persona?.trim() || undefined,
      capabilities: payload.capabilities?.trim() || undefined,
      skills: isGroupTemplate ? undefined : (payload.skills?.length ? [...payload.skills] : undefined),
      groupParticipantAssistantIds: normalizedGroupParticipants,
      groupCollaborationMode: isGroupTemplate ? (payload.groupCollaborationMode || 'auto') : undefined,
      sessions: [],
    }

    assistantGroups.value = assistantGroups.value.map((group) => {
      if (group.id !== (isGroupTemplate ? 'collaboration' : 'single'))
        return group
      return {
        ...group,
        assistants: [assistant, ...group.assistants],
      }
    })

    activeSurface.value = 'main'
    workspaceOpen.value = false
    showNewAssistant.value = false
    return { assistantId }
  }

  async function updateAssistant(assistantId: string, payload: CreateAssistantPayload) {
    const currentAssistant = findAssistantById(assistantId)
    if (!currentAssistant)
      return null

    const nextName = payload.name.trim()
    const nextBadge = nextName.slice(0, 1) || currentAssistant.badge
    const isGroupTemplate = currentAssistant.status === '群聊' || payload.templateKind === 'group'
    const normalizedGroupParticipants = isGroupTemplate
      ? [...new Set((payload.groupParticipantAssistantIds || currentAssistant.groupParticipantAssistantIds || []).filter(Boolean))]
      : undefined

    if (!IS_MOCK_MODE) {
      const api = getOpencodeDesktopApi()
      if (isGroupTemplate) {
        await api.saveGroupRoom({
          id: assistantId,
          name: nextName,
          description: payload.capabilities?.trim() || null,
          coordinatorPrompt: payload.persona?.trim() || null,
          memberAssistantIds: normalizedGroupParticipants,
          collaborationMode: payload.groupCollaborationMode || currentAssistant.groupCollaborationMode || 'auto',
        })
      }
      else {
        await api.saveAssistant({
          id: assistantId,
          name: nextName,
          description: payload.capabilities?.trim() || null,
          systemPrompt: payload.persona?.trim() || null,
          skillIds: payload.skills?.length ? [...payload.skills] : [],
        })
      }

      await refreshBootstrap(activeSessionId.value)
      closeNewAssistant()
      return assistantId
    }

    mutateAssistant(assistantId, assistant => ({
      ...assistant,
      name: nextName,
      badge: nextBadge,
      persona: payload.persona?.trim() || undefined,
      capabilities: payload.capabilities?.trim() || undefined,
      skills: isGroupTemplate ? undefined : (payload.skills?.length ? [...payload.skills] : undefined),
      groupParticipantAssistantIds: normalizedGroupParticipants,
      groupCollaborationMode: isGroupTemplate ? (payload.groupCollaborationMode || currentAssistant.groupCollaborationMode || 'auto') : undefined,
    }))

    updateAssistantSessionDetails(assistantId, detail => ({
      ...detail,
      assistantName: nextName,
      headerBadge: nextBadge,
      messages: detail.messages.map(message => message.assistantName
        ? { ...message, assistantName: nextName }
        : message),
      chatCards: detail.chatCards?.map(card => card.assistantId === assistantId
        ? { ...card, assistantName: nextName, assistantBadge: nextBadge }
        : card),
    }))

    closeNewAssistant()
    return assistantId
  }

  async function createSession(payload: CreateSessionPayload) {
    const targetAssistant = newSessionAssistant.value
    if (!targetAssistant)
      return null

    const workspacePath = payload.workspacePath.trim() || targetAssistant.workspacePath || '~/Documents'
    const isGroupSession = targetAssistant.status === '群聊'
    const customTitle = payload.sessionTitle?.trim()
    const title = customTitle || (isGroupSession ? `${targetAssistant.name}协作会话` : deriveSessionTitleFromWorkspace(workspacePath, targetAssistant.name))

    if (!IS_MOCK_MODE && provider.createSession) {
      const result = await provider.createSession({
        assistantId: isGroupSession ? '' : targetAssistant.id,
        title,
        workspacePath,
        agentId: isGroupSession ? targetAssistant.id : undefined,
      })
      const createdDetail = updateSessionDetail({
        ...result.session,
        workspacePath: result.session.workspacePath || workspacePath,
      })
      const createdSession: StudioSession = {
        id: createdDetail.id,
        title: createdDetail.headerTitle || title,
        time: '刚刚',
        active: true,
      }

      mutateAssistant(targetAssistant.id, assistant => ({
        ...assistant,
        sessions: [createdSession, ...assistant.sessions.map(item => ({ ...item, active: false }))],
      }))

      activeSurface.value = 'main'
      activeSessionId.value = createdDetail.id
      workspaceOpen.value = false
      closeNewSession()
      markSessionActive(createdDetail.id)
      return createdDetail.id
    }

    const sessionId = nanoid(10)
    const session: StudioSession = {
      id: sessionId,
      title,
      time: '刚刚',
      active: true,
    }

    mutateAssistant(targetAssistant.id, assistant => ({
      ...assistant,
      sessions: [session, ...assistant.sessions.map(item => ({ ...item, active: false }))],
    }))

    const participantAssistantIds = isGroupSession
      ? (targetAssistant.groupParticipantAssistantIds?.length
          ? [...targetAssistant.groupParticipantAssistantIds]
          : newSessionParticipantCandidates.value.slice(0, 2).map(item => item.id))
      : undefined
    const collaborationMode = isGroupSession
      ? (targetAssistant.groupCollaborationMode || 'auto')
      : undefined

    updateSessionDetail(createSessionDetailTemplate({
      sessionId,
      assistantId: targetAssistant.id,
      assistantName: targetAssistant.name,
      assistantBadge: targetAssistant.badge,
      sessionTitle: title,
      sessionTag: isGroupSession ? '群聊' : '运行中',
      workspacePath,
      mode: isGroupSession ? 'group' : 'regular',
      coordinatorAssistantId: isGroupSession ? 'coordinator' : undefined,
      collaborationMode,
      participantAssistantIds,
    }))

    activeSurface.value = 'main'
    activeSessionId.value = sessionId
    workspaceOpen.value = false
    closeNewSession()
    markSessionActive(sessionId)
    return sessionId
  }

  async function deleteSession(assistantId: string, sessionId: string) {
    if (!IS_MOCK_MODE) {
      await getOpencodeDesktopApi().deleteSession(sessionId)

      mutateAssistant(assistantId, assistant => ({
        ...assistant,
        sessions: assistant.sessions.filter(session => session.id !== sessionId),
      }))

      sessionMap.value = Object.fromEntries(
        Object.entries(sessionMap.value).filter(([key]) => key !== sessionId),
      )

      const nextSessionId = activeSessionId.value === sessionId
        ? getFirstAvailableSessionId(assistantId)
        : activeSessionId.value

      return refreshBootstrap(nextSessionId)
    }

    mutateAssistant(assistantId, assistant => ({
      ...assistant,
      sessions: assistant.sessions.filter(session => session.id !== sessionId),
    }))

    sessionMap.value = Object.fromEntries(
      Object.entries(sessionMap.value).filter(([key]) => key !== sessionId),
    )

    const nextSessionId = activeSessionId.value === sessionId
      ? getFirstAvailableSessionId(assistantId)
      : activeSessionId.value

    activeSessionId.value = nextSessionId

    if (!sessionMap.value[nextSessionId] && nextSessionId)
      void loadSessionDetail(nextSessionId)

    markSessionActive(nextSessionId)
    return nextSessionId || null
  }

  async function deleteAssistant(assistantId: string) {
    const removedSessionIds = new Set(getAssistantSessionIds(assistantId))

    if (!IS_MOCK_MODE) {
      const assistant = findAssistantById(assistantId)
      if (!assistant)
        return null

      if (assistant.status === '群聊')
        await getOpencodeDesktopApi().deleteGroupRoom(assistantId)
      else
        await getOpencodeDesktopApi().deleteAssistant(assistantId)

      invitedAssistants.value = invitedAssistants.value.filter(id => id !== assistantId)
      if (newSessionAssistantId.value === assistantId)
        closeNewSession()
      if (editingAssistantId.value === assistantId)
        closeNewAssistant()

      sessionMap.value = Object.fromEntries(
        Object.entries(sessionMap.value).filter(([key]) => !removedSessionIds.has(key)),
      )

      return refreshBootstrap(removedSessionIds.has(activeSessionId.value) ? '' : activeSessionId.value)
    }

    assistantGroups.value = assistantGroups.value.map(group => ({
      ...group,
      assistants: group.assistants.filter(assistant => assistant.id !== assistantId),
    }))

    invitedAssistants.value = invitedAssistants.value.filter(id => id !== assistantId)

    if (newSessionAssistantId.value === assistantId)
      closeNewSession()
    if (editingAssistantId.value === assistantId)
      closeNewAssistant()

    sessionMap.value = Object.fromEntries(
      Object.entries(sessionMap.value).filter(([key]) => !removedSessionIds.has(key)),
    )

    const nextSessionId = removedSessionIds.has(activeSessionId.value)
      ? getFirstAvailableSessionId()
      : activeSessionId.value

    activeSessionId.value = nextSessionId

    if (!sessionMap.value[nextSessionId] && nextSessionId)
      void loadSessionDetail(nextSessionId)

    markSessionActive(nextSessionId)
    return nextSessionId || null
  }

  function selectArtifact(artifactId: string) {
    if (!activeSessionId.value)
      return
    mutateSessionDetail(activeSessionId.value, session => ({
      ...session,
      selectedArtifactId: artifactId,
    }))
  }

  function isCardPending(cardId: string) {
    return pendingMutation.value?.sessionId === activeSessionId.value && pendingMutation.value?.cardId === cardId
  }

  function isActionPending(actionId: string) {
    return pendingMutation.value?.sessionId === activeSessionId.value && pendingMutation.value?.actionId === actionId
  }

  async function sendMessage(payload: Omit<AIStudioSendMessagePayload, 'sessionId'>) {
    if (!activeSessionId.value)
      return null
    return runMutation(
      {
        sessionId: activeSessionId.value,
        kind: 'message',
      },
      () => provider.sendMessage({
        sessionId: activeSessionId.value,
        ...payload,
      }),
    )
  }

  async function submitChoiceForm(payload: Omit<AIStudioChoiceSubmissionPayload, 'sessionId'>) {
    if (!activeSessionId.value)
      return null
    return runMutation(
      {
        sessionId: activeSessionId.value,
        kind: 'choice',
        cardId: payload.cardId,
      },
      () => provider.submitChoiceForm({
        sessionId: activeSessionId.value,
        ...payload,
      }),
    )
  }

  async function submitParamForm(payload: Omit<AIStudioParamSubmissionPayload, 'sessionId'>) {
    if (!activeSessionId.value)
      return null
    return runMutation(
      {
        sessionId: activeSessionId.value,
        kind: 'param',
        cardId: payload.cardId,
      },
      () => provider.submitParamForm({
        sessionId: activeSessionId.value,
        ...payload,
      }),
    )
  }

  async function submitCardAction(payload: Omit<AIStudioCardActionPayload, 'sessionId'>) {
    if (!activeSessionId.value)
      return null
    return runMutation(
      {
        sessionId: activeSessionId.value,
        kind: 'action',
        cardId: payload.cardId,
        actionId: payload.actionId,
      },
      () => provider.submitCardAction({
        sessionId: activeSessionId.value,
        ...payload,
      }),
    )
  }

  // Subscribe to opencode runtime events for real-time session updates.
  // This is the primary mechanism for receiving AI responses and message updates —
  // sendMessage only triggers async processing; results arrive via this event stream.
  if (!IS_MOCK_MODE && typeof window !== 'undefined' && 'opencodeApi' in window) {
    getOpencodeDesktopApi().onRuntimeEvent((rawEvent: unknown) => {
      const event = rawEvent as { type: string; properties: Record<string, unknown> }
      if (!event?.type) return

      // Extract the sessionID from whichever event shape carries it
      let eventSessionId: string | undefined
      if (event.type === 'session.idle' || event.type === 'session.status') {
        eventSessionId = event.properties.sessionID as string | undefined
      }
      else if (event.type === 'message.updated') {
        eventSessionId = (event.properties.info as { sessionID?: string } | undefined)?.sessionID
      }

      if (!eventSessionId || eventSessionId !== activeSessionId.value) return

      if (event.type === 'session.status') {
        const status = event.properties.status as { type: string } | undefined
        if (status?.type === 'busy') isAiTyping.value = true
      }
      else if (event.type === 'session.idle') {
        isAiTyping.value = false
        void loadSessionDetail(eventSessionId, { force: true })
      }
      else if (event.type === 'message.updated') {
        void loadSessionDetail(eventSessionId, { force: true })
      }
    })
  }

  return {
    activeSurface,
    activeSession,
    activeSessionId,
    assistantModalMode,
    assistantTemplateKind,
    assistantGroups,
    closeInviteAssistant,
    closeNewAssistant,
    closeNewSession,
    createAssistant,
    createSession,
    deleteAssistant,
    deleteSession,
    editingAssistant,
    ensureInitialized,
    errorMessage,
    initialized,
    inviteAssistants,
    invitedAssistants,
    isActionPending,
    isActiveSessionPending,
    isAiTyping,
    isCardPending,
    loading,
    newSessionAssistant,
    newSessionParticipantCandidates,
    newSessionAssistantId,
    openInviteAssistant,
    openEditAssistant,
    openNewAssistant,
    openNewGroupTemplate,
    openNewSession,
    openSurface,
    pendingMutation,
    selectArtifact,
    sendMessage,
    sessionMap,
    setActiveSession,
    setWorkspaceOpen,
    showInviteAssistant,
    showNewAssistant,
    showNewSession,
    submitCardAction,
    submitChoiceForm,
    submitParamForm,
    toggleWorkspace,
    updateAssistant,
    workspaceOpen,
  }
})
