import type { Dirent } from 'node:fs'
import { readdir } from 'node:fs/promises'
import path from 'node:path'

import type { StudioArtifact, StudioWorkspaceFile } from './adapter'

const MAX_DEPTH = 6
const MAX_FILES = 200
const IGNORED_DIRECTORIES = new Set(['.git', 'node_modules'])

export async function scanWorkspaceArtifacts(workspaceRoot: string): Promise<{
  workspaceFiles: StudioWorkspaceFile[]
  artifacts: StudioArtifact[]
}> {
  const normalizedRoot = workspaceRoot.trim()
  if (!normalizedRoot) {
    return { workspaceFiles: [], artifacts: [] }
  }

  const filePaths: string[] = []
  await walkWorkspace(normalizedRoot, '', 0, filePaths)

  const workspaceFiles: StudioWorkspaceFile[] = filePaths.map((relativePath, index) => ({
    id: `workspace-file-${index}`,
    name: relativePath,
    type: 'file',
    indent: 0,
  }))

  const artifacts: StudioArtifact[] = filePaths.map((relativePath, index) => ({
    id: `workspace-artifact-${index}`,
    name: relativePath,
    summary: 'Workspace file',
    tag: '宸ヤ綔绌洪棿鏂囦欢',
    tagTone: 'neutral',
  }))

  return { workspaceFiles, artifacts }
}

async function walkWorkspace(
  workspaceRoot: string,
  relativeDirectory: string,
  depth: number,
  filePaths: string[],
): Promise<void> {
  if (depth > MAX_DEPTH || filePaths.length >= MAX_FILES) {
    return
  }

  const currentDirectory = relativeDirectory
    ? path.join(workspaceRoot, relativeDirectory)
    : workspaceRoot

  let entries: Dirent<string>[]
  try {
    entries = await readdir(currentDirectory, { withFileTypes: true, encoding: 'utf8' })
  }
  catch {
    return
  }

  entries.sort((left, right) => left.name.localeCompare(right.name))

  for (const entry of entries) {
    if (filePaths.length >= MAX_FILES) {
      return
    }

    const nextRelativePath = relativeDirectory
      ? path.join(relativeDirectory, entry.name)
      : entry.name

    if (entry.isDirectory()) {
      if (IGNORED_DIRECTORIES.has(entry.name)) {
        continue
      }
      await walkWorkspace(workspaceRoot, nextRelativePath, depth + 1, filePaths)
      continue
    }

    if (entry.isFile()) {
      filePaths.push(nextRelativePath.replace(/\\/g, '/'))
    }
  }
}
