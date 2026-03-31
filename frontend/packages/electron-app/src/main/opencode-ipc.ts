import { ipcMain, BrowserWindow } from 'electron'

import {
  IPC_OPENCODE_AWAIT_INITIALIZATION,
  IPC_OPENCODE_CREATE_SESSION,
  IPC_OPENCODE_DELETE_ASSISTANT,
  IPC_OPENCODE_DELETE_GROUP_ROOM,
  IPC_OPENCODE_DELETE_SKILL,
  IPC_OPENCODE_DELETE_SESSION,
  IPC_OPENCODE_GET_BOOTSTRAP,
  IPC_OPENCODE_GET_RUNTIME_STATUS,
  IPC_OPENCODE_GET_SESSION,
  IPC_OPENCODE_GET_SETTINGS,
  IPC_OPENCODE_LIST_ASSISTANTS,
  IPC_OPENCODE_LIST_GROUP_ROOMS,
  IPC_OPENCODE_LIST_SKILLS,
  IPC_OPENCODE_IMPORT_SKILL,
  IPC_OPENCODE_RUNTIME_EVENT,
  IPC_OPENCODE_SAVE_ASSISTANT,
  IPC_OPENCODE_SAVE_DEFAULT_MODEL,
  IPC_OPENCODE_SAVE_GROUP_ROOM,
  IPC_OPENCODE_SAVE_PROVIDER,
  IPC_OPENCODE_SEND_MESSAGE,
} from './opencode/constants'
import type { SidecarManager } from './opencode/sidecar'
import type { RuntimeApi } from './opencode/api'
import type { RuntimeEventStream } from './opencode/events'
import type { RuntimeSkillsService } from './opencode/skills'
import type { AssistantStore } from './store/assistant-store'
import type { SettingsStore } from './store/settings-store'
import type { SessionStore } from './store/session-store'
import {
  toStudioAssistantGroups,
  toStudioSessionDetail,
  resolveDefaultSessionId,
} from './opencode/adapter'
import { scanWorkspaceArtifacts } from './opencode/workspace-scan'
import { resolveSessionMessageContext, resolveSessionWorkspaceContext } from './opencode/workspace-context'
import type { DesktopRuntimeEvent } from '../shared/sessions'

type OpencodeIpcDeps = {
  sidecar: SidecarManager
  api: RuntimeApi
  eventStream: RuntimeEventStream
  skillsService: RuntimeSkillsService
  assistantStore: AssistantStore
  settingsStore: SettingsStore
  sessionStore: SessionStore
}

export function registerOpencodeIpc(deps: OpencodeIpcDeps) {
  const { sidecar, api, eventStream, skillsService, assistantStore, settingsStore, sessionStore } = deps

  eventStream.subscribe((event: DesktopRuntimeEvent) => {
    sessionStore.applyEvent(event)
    broadcastToAllWindows(IPC_OPENCODE_RUNTIME_EVENT, event)
  })

  ipcMain.handle(IPC_OPENCODE_GET_RUNTIME_STATUS, () => {
    return sidecar.getStatus()
  })

  ipcMain.handle(IPC_OPENCODE_AWAIT_INITIALIZATION, async () => {
    return sidecar.awaitInitialization()
  })

  ipcMain.handle(IPC_OPENCODE_GET_BOOTSTRAP, async () => {
    const [assistants, groupRooms, sessions] = await Promise.all([
      assistantStore.listAssistants(),
      assistantStore.listGroupRooms(),
      api.listSessions().catch(() => []),
    ])

    const rootSessions = sessions.filter((s) => !s.parentID && !s.time.archived)
    const liveRuntimeSessionIds = rootSessions.map((s) => s.id)
    await Promise.all([
      assistantStore.cleanupMissingRuntimeSessions(liveRuntimeSessionIds),
      assistantStore.cleanupMissingGroupRoomSessions(liveRuntimeSessionIds),
    ])

    const [assistantSessions, groupRoomSessions] = await Promise.all([
      assistantStore.listAssistantSessions(),
      assistantStore.listGroupRoomSessions(),
    ])

    const assignedRuntimeSessionIds = new Set([
      ...assistantSessions.map((s) => s.runtimeSessionId),
      ...groupRoomSessions.map((s) => s.runtimeSessionId),
    ])

    const sessionsByAssistantId = new Map<string, typeof rootSessions>()
    for (const sess of assistantSessions) {
      const runtimeSession = rootSessions.find((s) => s.id === sess.runtimeSessionId)
      if (!runtimeSession) continue
      const list = sessionsByAssistantId.get(sess.assistantId) ?? []
      list.push(runtimeSession)
      sessionsByAssistantId.set(sess.assistantId, list)
    }

    const sessionsByGroupRoomId = new Map<string, typeof rootSessions>()
    for (const sess of groupRoomSessions) {
      const runtimeSession = rootSessions.find((s) => s.id === sess.runtimeSessionId)
      if (!runtimeSession) continue
      const list = sessionsByGroupRoomId.get(sess.groupRoomId) ?? []
      list.push(runtimeSession)
      sessionsByGroupRoomId.set(sess.groupRoomId, list)
    }

    const unassignedSessions = rootSessions.filter((s) => !assignedRuntimeSessionIds.has(s.id))

    const assistantGroups = toStudioAssistantGroups(
      assistants,
      groupRooms,
      sessionsByAssistantId,
      sessionsByGroupRoomId,
      unassignedSessions,
    )

    const defaultSessionId = resolveDefaultSessionId(rootSessions)

    return { assistantGroups, defaultSessionId }
  })

  ipcMain.handle(IPC_OPENCODE_GET_SESSION, async (_event, sessionId: string) => {
    const [session, messages, assistants, groupRooms, assistantSessions, groupRoomSessions] = await Promise.all([
      api.getSession(sessionId),
      api.getSessionMessages(sessionId),
      assistantStore.listAssistants(),
      assistantStore.listGroupRooms(),
      assistantStore.listAssistantSessions(),
      assistantStore.listGroupRoomSessions(),
    ])

    const workspaceContext = resolveSessionWorkspaceContext(
      sessionId,
      assistants,
      groupRooms,
      assistantSessions,
      groupRoomSessions,
    )
    const workspacePath = workspaceContext.workspacePath?.trim() || session.directory
    const workspaceSnapshot = workspacePath
      ? await scanWorkspaceArtifacts(workspacePath)
      : { workspaceFiles: [], artifacts: [] }

    return toStudioSessionDetail(session, messages, undefined, undefined, {
      workspacePath,
      workspaceFiles: workspaceSnapshot.workspaceFiles,
      artifacts: workspaceSnapshot.artifacts,
    })
  })

  ipcMain.handle(
    IPC_OPENCODE_CREATE_SESSION,
    async (_event, payload: { title?: string | null; assistantId?: string | null; groupRoomId?: string | null }) => {
      const session = await api.createSession({ title: payload?.title ?? null })
      if (payload?.groupRoomId) {
        await assistantStore.attachGroupRoomSession(payload.groupRoomId, session.id, session.title ?? payload?.title ?? null)
      }
      else if (payload?.assistantId) {
        await assistantStore.attachRuntimeSession(payload.assistantId, session.id, session.title ?? payload?.title ?? null)
      }
      return session
    },
  )

  ipcMain.handle(IPC_OPENCODE_DELETE_SESSION, async (_event, sessionId: string) => {
    await api.deleteSession(sessionId)
    const liveSessions = await api.listSessions().catch(() => [])
    const liveRuntimeSessionIds = liveSessions
      .filter((s) => !s.parentID && !s.time.archived)
      .map((s) => s.id)
    await Promise.all([
      assistantStore.cleanupMissingRuntimeSessions(liveRuntimeSessionIds),
      assistantStore.cleanupMissingGroupRoomSessions(liveRuntimeSessionIds),
    ])
    return { success: true }
  })

  ipcMain.handle(
    IPC_OPENCODE_SEND_MESSAGE,
    async (
      _event,
      payload: {
        sessionID: string
        text: string
        attachments?: Array<{
          id: string
          name: string
          mime: string
          url: string
        }>
        model?: string | null
        providerId?: string | null
      },
    ) => {
      const [assistants, groupRooms, assistantSessions, groupRoomSessions] = await Promise.all([
        assistantStore.listAssistants(),
        assistantStore.listGroupRooms(),
        assistantStore.listAssistantSessions(),
        assistantStore.listGroupRoomSessions(),
      ])
      const context = resolveSessionMessageContext(
        payload.sessionID,
        assistants,
        groupRooms,
        assistantSessions,
        groupRoomSessions,
      )
      await api.sendMessage({
        sessionID: payload.sessionID,
        text: payload.text,
        attachments: payload.attachments,
        model: payload.model ?? null,
        providerId: payload.providerId ?? null,
        agent: context.agent ?? null,
        system: context.system ?? null,
      })
      return { success: true }
    },
  )

  ipcMain.handle(IPC_OPENCODE_GET_SETTINGS, async () => {
    return settingsStore.getSettings()
  })

  ipcMain.handle(IPC_OPENCODE_SAVE_PROVIDER, async (_event, input: Parameters<SettingsStore['saveProvider']>[0]) => {
    const result = await settingsStore.saveProvider(input)
    await sidecar.restart()
    return result
  })

  ipcMain.handle(IPC_OPENCODE_SAVE_DEFAULT_MODEL, async (_event, input: Parameters<SettingsStore['saveDefaultModel']>[0]) => {
    const result = await settingsStore.saveDefaultModel(input)
    await sidecar.restart()
    return result
  })

  ipcMain.handle(IPC_OPENCODE_LIST_ASSISTANTS, async () => {
    return assistantStore.listAssistants()
  })

  ipcMain.handle(IPC_OPENCODE_SAVE_ASSISTANT, async (_event, input: Parameters<AssistantStore['saveAssistant']>[0]) => {
    const result = await assistantStore.saveAssistant(input)
    await sidecar.restart()
    return result
  })

  ipcMain.handle(IPC_OPENCODE_DELETE_ASSISTANT, async (_event, id: string) => {
    const result = await assistantStore.deleteAssistant(id)
    await sidecar.restart()
    return result
  })

  ipcMain.handle(IPC_OPENCODE_LIST_GROUP_ROOMS, async () => {
    return assistantStore.listGroupRooms()
  })

  ipcMain.handle(IPC_OPENCODE_SAVE_GROUP_ROOM, async (_event, input: Parameters<AssistantStore['saveGroupRoom']>[0]) => {
    const result = await assistantStore.saveGroupRoom(input)
    await sidecar.restart()
    return result
  })

  ipcMain.handle(IPC_OPENCODE_DELETE_GROUP_ROOM, async (_event, id: string) => {
    const result = await assistantStore.deleteGroupRoom(id)
    await sidecar.restart()
    return result
  })

  ipcMain.handle(IPC_OPENCODE_LIST_SKILLS, async () => {
    return skillsService.getState()
  })

  ipcMain.handle(IPC_OPENCODE_IMPORT_SKILL, async () => {
    return skillsService.importSkillFromDialog()
  })

  ipcMain.handle(IPC_OPENCODE_DELETE_SKILL, async (_event, skillId: string) => {
    return skillsService.deleteSkill(skillId)
  })

  return {
    cleanup: () => {
      ipcMain.removeHandler(IPC_OPENCODE_GET_RUNTIME_STATUS)
      ipcMain.removeHandler(IPC_OPENCODE_AWAIT_INITIALIZATION)
      ipcMain.removeHandler(IPC_OPENCODE_GET_BOOTSTRAP)
      ipcMain.removeHandler(IPC_OPENCODE_GET_SESSION)
      ipcMain.removeHandler(IPC_OPENCODE_CREATE_SESSION)
      ipcMain.removeHandler(IPC_OPENCODE_DELETE_SESSION)
      ipcMain.removeHandler(IPC_OPENCODE_SEND_MESSAGE)
      ipcMain.removeHandler(IPC_OPENCODE_GET_SETTINGS)
      ipcMain.removeHandler(IPC_OPENCODE_SAVE_PROVIDER)
      ipcMain.removeHandler(IPC_OPENCODE_SAVE_DEFAULT_MODEL)
      ipcMain.removeHandler(IPC_OPENCODE_LIST_ASSISTANTS)
      ipcMain.removeHandler(IPC_OPENCODE_SAVE_ASSISTANT)
      ipcMain.removeHandler(IPC_OPENCODE_DELETE_ASSISTANT)
      ipcMain.removeHandler(IPC_OPENCODE_LIST_GROUP_ROOMS)
      ipcMain.removeHandler(IPC_OPENCODE_SAVE_GROUP_ROOM)
      ipcMain.removeHandler(IPC_OPENCODE_DELETE_GROUP_ROOM)
      ipcMain.removeHandler(IPC_OPENCODE_LIST_SKILLS)
      ipcMain.removeHandler(IPC_OPENCODE_IMPORT_SKILL)
      ipcMain.removeHandler(IPC_OPENCODE_DELETE_SKILL)
    },
  }
}

function broadcastToAllWindows(channel: string, payload: unknown) {
  for (const win of BrowserWindow.getAllWindows()) {
    if (!win.isDestroyed()) {
      win.webContents.send(channel, payload)
    }
  }
}
