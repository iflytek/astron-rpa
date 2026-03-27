import { access, cp, mkdir, stat } from 'node:fs/promises'
import { homedir } from 'node:os'
import path from 'node:path'
import { dialog } from 'electron'

import { createLogger } from './logging'
import type { OpencodeSkillRecord, RuntimeSkillDiscoveryState } from '../../shared/assistants'
import type { SidecarManager } from './sidecar'

type BundledSkillInfo = {
  name?: unknown
  description?: unknown
  location?: unknown
  content?: unknown
}

export type RuntimeSkillsService = {
  listSkills: () => Promise<RuntimeSkillDiscoveryState>
  getState: () => Promise<RuntimeSkillDiscoveryState>
  importSkillFromDialog: (input: { scope: 'global' | 'project'; projectRoot?: string | null }) => Promise<{
    importedName: string
    destinationPath: string
    scope: 'global' | 'project'
  }>
}

const logger = createLogger('runtime-skills')

export function createRuntimeSkillsService(runtime: Pick<SidecarManager, 'getConnection'>): RuntimeSkillsService {
  return {
    listSkills: getState,
    getState,
    importSkillFromDialog,
  }

  async function getState(): Promise<RuntimeSkillDiscoveryState> {
    try {
      const connection = await runtime.getConnection()
      const url = new URL('/skill', connection.baseUrl)
      const response = await fetch(url, {
        headers: { ...connection.headers, accept: 'application/json' },
        method: 'GET',
      })

      if (!response.ok) {
        throw new Error(`Bundled runtime skill discovery failed (${response.status} ${response.statusText})`)
      }

      const payload = (await response.json()) as unknown
      if (!Array.isArray(payload)) {
        throw new Error('Bundled runtime skill discovery returned an unexpected payload.')
      }

      return {
        skills: mapRuntimeSkills(payload),
        unavailable: false,
        error: null,
      }
    }
    catch (error) {
      logger.warn(
        'bundled runtime skill discovery unavailable; returning empty skill list',
        error instanceof Error ? error : String(error),
      )
      return {
        skills: [],
        unavailable: true,
        error: error instanceof Error ? error.message : String(error),
      }
    }
  }

  async function importSkillFromDialog(input: { scope: 'global' | 'project'; projectRoot?: string | null }) {
    const selection = await dialog.showOpenDialog({
      title: input.scope === 'global' ? '导入全局技能' : '导入项目技能',
      buttonLabel: '选择技能文件夹',
      properties: ['openDirectory'],
    })

    if (selection.canceled || selection.filePaths.length === 0) {
      throw new Error('技能导入已取消')
    }

    const sourcePath = selection.filePaths[0]!
    const importedName = path.basename(sourcePath)
    const destinationRoot = resolveSkillDestinationRoot(input)
    const destinationPath = path.join(destinationRoot, importedName)

    await assertSkillDirectory(sourcePath)
    await mkdir(destinationRoot, { recursive: true })
    await assertDestinationAvailable(destinationPath)
    await cp(sourcePath, destinationPath, { recursive: true, errorOnExist: true, force: false })

    logger.info('skill imported', { importedName, destinationPath, scope: input.scope })

    return { importedName, destinationPath, scope: input.scope }
  }
}

function mapRuntimeSkills(skills: BundledSkillInfo[]): OpencodeSkillRecord[] {
  return skills
    .map((skill) => normalizeRuntimeSkill(skill))
    .filter((skill): skill is OpencodeSkillRecord => Boolean(skill))
    .sort((left, right) => left.name.localeCompare(right.name))
}

function normalizeRuntimeSkill(skill: BundledSkillInfo): OpencodeSkillRecord | null {
  const name = normalizeText(skill.name)
  const description = normalizeText(skill.description)
  const location = normalizeText(skill.location)

  if (!name || !description || !location) {
    return null
  }

  return {
    id: `${name}::${location.replace(/\\/g, '/').trim().toLowerCase()}`,
    type: 'opencode_skill',
    name,
    description,
    source: inferSkillSource(location),
  }
}

function inferSkillSource(location: string): OpencodeSkillRecord['source'] {
  const normalizedLocation = location.replace(/\\/g, '/').toLowerCase()

  if (normalizedLocation.includes('/cache/skills/') || normalizedLocation.startsWith('cache/skills/')) {
    return 'remote'
  }

  if (/^[a-z]+:\/\//.test(normalizedLocation)) {
    return 'remote'
  }

  if (normalizedLocation.includes('/.claude/skills/') || normalizedLocation.includes('/.agents/skills/')) {
    return 'global'
  }

  return 'project'
}

function normalizeText(value: unknown) {
  return typeof value === 'string' && value.trim() ? value.trim() : null
}

function resolveSkillDestinationRoot(input: { scope: 'global' | 'project'; projectRoot?: string | null }) {
  if (input.scope === 'global') {
    return path.join(homedir(), '.agents', 'skills')
  }

  const projectRoot = normalizeText(input.projectRoot)
  if (!projectRoot) {
    throw new Error('当前没有可用的项目工作区，无法导入项目技能。')
  }

  return path.join(projectRoot, '.agents', 'skills')
}

async function assertSkillDirectory(sourcePath: string) {
  const sourceStat = await stat(sourcePath).catch(() => null)
  if (!sourceStat?.isDirectory()) {
    throw new Error('请选择一个包含 SKILL.md 的技能文件夹。')
  }

  const skillFilePath = path.join(sourcePath, 'SKILL.md')
  try {
    await access(skillFilePath)
  }
  catch {
    throw new Error('所选文件夹中没有找到 SKILL.md，无法导入为技能。')
  }
}

async function assertDestinationAvailable(destinationPath: string) {
  const existing = await stat(destinationPath).catch(() => null)
  if (existing) {
    throw new Error(`目标位置已经存在同名技能：${path.basename(destinationPath)}`)
  }
}
