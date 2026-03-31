import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'

import { afterEach, describe, expect, it } from 'vitest'

import { scanWorkspaceArtifacts } from './workspace-scan'

const tempDirs: string[] = []

async function createTempDir(prefix: string) {
  const dir = await mkdtemp(path.join(os.tmpdir(), prefix))
  tempDirs.push(dir)
  return dir
}

afterEach(async () => {
  await Promise.all(tempDirs.splice(0).map(dir => rm(dir, { recursive: true, force: true })))
})

describe('scanWorkspaceArtifacts', () => {
  it('lists files under the assigned workspace root using relative paths', async () => {
    const tempDir = await createTempDir('workspace-scan-')
    await mkdir(path.join(tempDir, 'notes'), { recursive: true })
    await writeFile(path.join(tempDir, 'summary.md'), '# Summary', 'utf8')
    await writeFile(path.join(tempDir, 'notes', 'todo.txt'), 'todo', 'utf8')

    const result = await scanWorkspaceArtifacts(tempDir)

    expect(result.workspaceFiles.map(file => file.name)).toEqual([
      path.join('notes', 'todo.txt').replace(/\\/g, '/'),
      'summary.md',
    ])
    expect(result.artifacts.map(artifact => artifact.name)).toEqual([
      path.join('notes', 'todo.txt').replace(/\\/g, '/'),
      'summary.md',
    ])
  })
})
