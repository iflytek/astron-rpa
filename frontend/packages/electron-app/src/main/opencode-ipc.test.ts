import { mkdtemp, rm, writeFile } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import {
  IPC_OPENCODE_DELETE_ASSISTANT,
  IPC_OPENCODE_DELETE_GROUP_ROOM,
  IPC_OPENCODE_GET_SESSION,
  IPC_OPENCODE_SAVE_ASSISTANT,
  IPC_OPENCODE_SAVE_DEFAULT_MODEL,
  IPC_OPENCODE_SAVE_GROUP_ROOM,
  IPC_OPENCODE_SAVE_PROVIDER,
  IPC_OPENCODE_SEND_MESSAGE,
} from './opencode/constants'
import { registerOpencodeIpc } from './opencode-ipc'

const { ipcHandle, ipcRemoveHandler } = vi.hoisted(() => ({
  ipcHandle: vi.fn(),
  ipcRemoveHandler: vi.fn(),
}))

vi.mock('electron', () => ({
  BrowserWindow: {
    getAllWindows: () => [],
  },
  ipcMain: {
    handle: ipcHandle,
    removeHandler: ipcRemoveHandler,
  },
}))

const tempDirs: string[] = []

async function createTempDir(prefix: string) {
  const dir = await mkdtemp(path.join(os.tmpdir(), prefix))
  tempDirs.push(dir)
  return dir
}

describe('registerOpencodeIpc send message workspace context', () => {
  beforeEach(() => {
    ipcHandle.mockReset()
    ipcRemoveHandler.mockReset()
  })

  afterEach(async () => {
    await Promise.all(tempDirs.splice(0).map(dir => rm(dir, { recursive: true, force: true })))
  })

  it('routes assistant sessions through the configured agent and workspace system prompt', async () => {
    const sendMessage = vi.fn().mockResolvedValue(undefined)

    registerOpencodeIpc({
      sidecar: {
        getStatus: vi.fn(),
        awaitInitialization: vi.fn(),
      } as any,
      api: {
        sendMessage,
      } as any,
      eventStream: {
        subscribe: vi.fn(),
      } as any,
      skillsService: {} as any,
      assistantStore: {
        listAssistants: vi.fn().mockResolvedValue([
          {
            id: 'assistant-1',
            name: 'Code Assistant',
            description: null,
            avatar: null,
            color: null,
            systemPrompt: 'You are careful and pragmatic.',
            defaultModel: null,
            skillIds: [],
            toolIds: [],
            toolPolicy: 'allow_assigned',
            workspacePath: 'D:/Workspaces/assistants/code',
            createdAt: '2026-04-01T00:00:00.000Z',
            updatedAt: '2026-04-01T00:00:00.000Z',
          },
        ]),
        listGroupRooms: vi.fn().mockResolvedValue([]),
        listAssistantSessions: vi.fn().mockResolvedValue([
          {
            id: 'mapping-1',
            assistantId: 'assistant-1',
            runtimeSessionId: 'session-1',
            title: null,
            createdAt: '2026-04-01T00:00:00.000Z',
            updatedAt: '2026-04-01T00:00:00.000Z',
          },
        ]),
        listGroupRoomSessions: vi.fn().mockResolvedValue([]),
      } as any,
      settingsStore: {} as any,
      sessionStore: {
        applyEvent: vi.fn(),
      } as any,
    })

    const sendHandler = ipcHandle.mock.calls.find(([channel]) => channel === IPC_OPENCODE_SEND_MESSAGE)?.[1]
    expect(sendHandler).toBeTypeOf('function')

    await sendHandler({}, {
      sessionID: 'session-1',
      text: 'Create a review plan',
      model: null,
      providerId: null,
    })

    expect(sendMessage).toHaveBeenCalledWith(expect.objectContaining({
      sessionID: 'session-1',
      text: 'Create a review plan',
      agent: 'assistant-direct-assistant-1',
      system: expect.stringContaining('Workspace root: D:/Workspaces/assistants/code'),
    }))
  })

  it('restarts the sidecar after assistant, group, and settings mutations', async () => {
    const restart = vi.fn().mockResolvedValue(undefined)
    const saveProvider = vi.fn().mockResolvedValue({ ok: true })
    const saveDefaultModel = vi.fn().mockResolvedValue({ ok: true })
    const saveAssistant = vi.fn().mockResolvedValue({ id: 'assistant-1' })
    const deleteAssistant = vi.fn().mockResolvedValue({ id: 'assistant-1' })
    const saveGroupRoom = vi.fn().mockResolvedValue({ id: 'group-1' })
    const deleteGroupRoom = vi.fn().mockResolvedValue({ id: 'group-1' })

    registerOpencodeIpc({
      sidecar: {
        restart,
        getStatus: vi.fn(),
        awaitInitialization: vi.fn(),
      } as any,
      api: {} as any,
      eventStream: {
        subscribe: vi.fn(),
      } as any,
      skillsService: {} as any,
      assistantStore: {
        saveAssistant,
        deleteAssistant,
        saveGroupRoom,
        deleteGroupRoom,
      } as any,
      settingsStore: {
        saveProvider,
        saveDefaultModel,
      } as any,
      sessionStore: {
        applyEvent: vi.fn(),
      } as any,
    })

    const saveProviderHandler = ipcHandle.mock.calls.find(([channel]) => channel === IPC_OPENCODE_SAVE_PROVIDER)?.[1]
    const saveDefaultModelHandler = ipcHandle.mock.calls.find(([channel]) => channel === IPC_OPENCODE_SAVE_DEFAULT_MODEL)?.[1]
    const saveAssistantHandler = ipcHandle.mock.calls.find(([channel]) => channel === IPC_OPENCODE_SAVE_ASSISTANT)?.[1]
    const deleteAssistantHandler = ipcHandle.mock.calls.find(([channel]) => channel === IPC_OPENCODE_DELETE_ASSISTANT)?.[1]
    const saveGroupRoomHandler = ipcHandle.mock.calls.find(([channel]) => channel === IPC_OPENCODE_SAVE_GROUP_ROOM)?.[1]
    const deleteGroupRoomHandler = ipcHandle.mock.calls.find(([channel]) => channel === IPC_OPENCODE_DELETE_GROUP_ROOM)?.[1]

    await saveProviderHandler({}, { providerId: 'openai' })
    await saveDefaultModelHandler({}, { providerId: 'openai', model: 'gpt-4.1' })
    await saveAssistantHandler({}, { name: 'Code Assistant' })
    await deleteAssistantHandler({}, 'assistant-1')
    await saveGroupRoomHandler({}, { name: 'Review Room' })
    await deleteGroupRoomHandler({}, 'group-1')

    expect(restart).toHaveBeenCalledTimes(6)
  })

  it('loads workspace files from the assigned assistant workspace root instead of the runtime cwd', async () => {
    const tempDir = await createTempDir('ipc-workspace-')
    await writeFile(path.join(tempDir, 'summary.md'), '# Summary', 'utf8')

    registerOpencodeIpc({
      sidecar: {
        getStatus: vi.fn(),
        awaitInitialization: vi.fn(),
      } as any,
      api: {
        getSession: vi.fn().mockResolvedValue({
          id: 'session-1',
          slug: 'quiet-harbor',
          projectID: 'project-1',
          directory: 'D:/Runtime/Cwd',
          title: 'Workspace Test',
          version: '1.2.27',
          time: { created: 1, updated: 2 },
        }),
        getSessionMessages: vi.fn().mockResolvedValue([]),
      } as any,
      eventStream: {
        subscribe: vi.fn(),
      } as any,
      skillsService: {} as any,
      assistantStore: {
        listAssistants: vi.fn().mockResolvedValue([
          {
            id: 'assistant-1',
            name: 'Code Assistant',
            description: null,
            avatar: null,
            color: null,
            systemPrompt: null,
            defaultModel: null,
            skillIds: [],
            toolIds: [],
            toolPolicy: 'allow_assigned',
            workspacePath: tempDir,
            createdAt: '2026-04-01T00:00:00.000Z',
            updatedAt: '2026-04-01T00:00:00.000Z',
          },
        ]),
        listGroupRooms: vi.fn().mockResolvedValue([]),
        listAssistantSessions: vi.fn().mockResolvedValue([
          {
            id: 'mapping-1',
            assistantId: 'assistant-1',
            runtimeSessionId: 'session-1',
            title: null,
            createdAt: '2026-04-01T00:00:00.000Z',
            updatedAt: '2026-04-01T00:00:00.000Z',
          },
        ]),
        listGroupRoomSessions: vi.fn().mockResolvedValue([]),
      } as any,
      settingsStore: {} as any,
      sessionStore: {
        applyEvent: vi.fn(),
      } as any,
    })

    const getSessionHandler = ipcHandle.mock.calls.find(([channel]) => channel === IPC_OPENCODE_GET_SESSION)?.[1]
    expect(getSessionHandler).toBeTypeOf('function')

    const detail = await getSessionHandler({}, 'session-1')

    expect(detail.workspacePath).toBe(tempDir)
    expect(detail.workspaceFiles).toEqual([
      { id: 'workspace-file-0', name: 'summary.md', type: 'file', indent: 0 },
    ])
    expect(detail.artifacts).toEqual([
      { id: 'workspace-artifact-0', name: 'summary.md', summary: 'Workspace file', tag: '宸ヤ綔绌洪棿鏂囦欢', tagTone: 'neutral' },
    ])
  })
})
