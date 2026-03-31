import { describe, expect, it } from 'vitest'

import { toStudioAssistantGroups, toStudioSessionDetail } from './adapter'

describe('toStudioAssistantGroups', () => {
  it('exposes persisted workspace paths for assistants and group rooms', () => {
    const groups = toStudioAssistantGroups(
      [
        {
          id: 'assistant-1',
          name: '代码助手',
          description: null,
          avatar: null,
          color: null,
          systemPrompt: null,
          defaultModel: null,
          skillIds: [],
          toolIds: [],
          toolPolicy: 'allow_assigned',
          workspacePath: 'D:/Workspaces/assistants/code',
          createdAt: '2026-04-01T00:00:00.000Z',
          updatedAt: '2026-04-01T00:00:00.000Z',
        } as any,
      ],
      [
        {
          id: 'group-1',
          name: '评审群聊',
          description: null,
          memberAssistantIds: ['assistant-1'],
          coordinatorPrompt: null,
          collaborationMode: 'auto',
          workspacePath: 'D:/Workspaces/groups/review',
          createdAt: '2026-04-01T00:00:00.000Z',
          updatedAt: '2026-04-01T00:00:00.000Z',
        } as any,
      ],
      new Map(),
      new Map(),
      [],
    )

    expect(groups[0]?.assistants[0]?.workspacePath).toBe('D:/Workspaces/assistants/code')
    expect(groups[1]?.assistants[0]?.workspacePath).toBe('D:/Workspaces/groups/review')
  })

  it('uses the assigned workspace path and scanned files in session detail', () => {
    const detail = toStudioSessionDetail(
      {
        id: 'session-1',
        slug: 'quiet-harbor',
        projectID: 'project-1',
        directory: 'D:/Runtime/Cwd',
        title: 'Workspace Test',
        version: '1.2.27',
        time: { created: 1, updated: 2 },
      } as any,
      [],
      'Code Assistant',
      'C',
      {
        workspacePath: 'D:/Workspaces/assistants/code',
        workspaceFiles: [
          { id: 'file-1', name: 'summary.md', type: 'file', indent: 0 },
        ],
        artifacts: [
          { id: 'artifact-1', name: 'summary.md', summary: 'Generated summary', tag: '宸ヤ綔绌洪棿鏂囦欢', tagTone: 'neutral' },
        ],
      },
    )

    expect(detail.workspacePath).toBe('D:/Workspaces/assistants/code')
    expect(detail.workspaceFiles).toEqual([
      { id: 'file-1', name: 'summary.md', type: 'file', indent: 0 },
    ])
    expect(detail.artifacts).toEqual([
      { id: 'artifact-1', name: 'summary.md', summary: 'Generated summary', tag: '宸ヤ綔绌洪棿鏂囦欢', tagTone: 'neutral' },
    ])
  })
})
