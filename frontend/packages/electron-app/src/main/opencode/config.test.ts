import { describe, expect, it } from 'vitest'

import { buildRuntimeConfigContent } from './config'

describe('buildRuntimeConfigContent workspace prompts', () => {
  it('injects workspace guidance into assistant and group agent prompts', () => {
    const content = buildRuntimeConfigContent(
      {
        version: 1,
        providers: {},
        defaultModel: null,
      },
      [
        {
          id: 'assistant-1',
          name: 'Code Assistant',
          description: 'Writes code',
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
      ],
      [
        {
          id: 'group-1',
          name: 'Review Room',
          description: 'Coordinate review work',
          memberAssistantIds: ['assistant-1'],
          coordinatorPrompt: 'Delegate only when needed.',
          collaborationMode: 'auto',
          workspacePath: 'D:/Workspaces/groups/review',
          createdAt: '2026-04-01T00:00:00.000Z',
          updatedAt: '2026-04-01T00:00:00.000Z',
        },
      ],
    )

    const parsed = JSON.parse(content) as {
      agent: Record<string, { prompt?: string }>
    }

    expect(parsed.agent['assistant-direct-assistant-1']?.prompt).toContain('Workspace root: D:/Workspaces/assistants/code')
    expect(parsed.agent['assistant-direct-assistant-1']?.prompt).toContain('soft application-level workspace constraint')
    expect(parsed.agent['room-coordinator-group-1']?.prompt).toContain('Workspace root: D:/Workspaces/groups/review')
    expect(parsed.agent['room-coordinator-group-1']?.prompt).toContain('Use this workspace root for shared room artifacts')
  })
})
