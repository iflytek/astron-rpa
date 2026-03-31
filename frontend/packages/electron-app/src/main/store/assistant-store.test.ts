import { mkdtemp, rm } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'

import { afterEach, describe, expect, it } from 'vitest'

import { createAssistantStore } from './assistant-store'

const tempDirs: string[] = []

async function createTempDir(prefix: string) {
  const dir = await mkdtemp(path.join(os.tmpdir(), prefix))
  tempDirs.push(dir)
  return dir
}

afterEach(async () => {
  await Promise.all(tempDirs.splice(0).map(dir => rm(dir, { recursive: true, force: true })))
})

describe('createAssistantStore workspace paths', () => {
  it('auto-assigns a fixed workspace path for assistants and group rooms', async () => {
    const tempDir = await createTempDir('assistant-store-')
    const workspaceRoot = path.join(tempDir, 'workspaces')
    const store = createAssistantStore({
      storagePath: path.join(tempDir, 'assistants.json'),
      workspaceRoot,
      createId: (() => {
        const ids = ['assistant-001', 'group-001']
        return () => ids.shift() ?? 'unexpected-id'
      })(),
    })

    const assistant = await store.saveAssistant({ name: '财务助手' })
    const room = await store.saveGroupRoom({ name: '财务协作组' })

    expect((assistant as { workspacePath?: string }).workspacePath).toBe(
      path.join(workspaceRoot, 'assistants', '财务助手-assistant-001'),
    )
    expect((room as { workspacePath?: string }).workspacePath).toBe(
      path.join(workspaceRoot, 'groups', '财务协作组-group-001'),
    )
  })
})
