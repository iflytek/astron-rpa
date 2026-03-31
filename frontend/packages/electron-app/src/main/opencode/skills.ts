import { access, cp, mkdir, readFile, readdir, rm, stat } from 'node:fs/promises'
import path from 'node:path'
import { dialog } from 'electron'

import { createLogger } from './logging'
import type { OpencodeSkillRecord, RuntimeSkillDiscoveryState } from '../../shared/assistants'

export type RuntimeSkillsService = {
  listSkills: () => Promise<RuntimeSkillDiscoveryState>
  getState: () => Promise<RuntimeSkillDiscoveryState>
  importSkillFromDialog: () => Promise<{
    skillId: string
    importedName: string
    destinationPath: string
  }>
  deleteSkill: (skillId: string) => Promise<{ success: boolean }>
}

const logger = createLogger('runtime-skills')

export function createRuntimeSkillsService(options: { getManagedRoot: () => string }): RuntimeSkillsService {
  return {
    listSkills: getState,
    getState,
    importSkillFromDialog,
    deleteSkill,
  }

  async function getState(): Promise<RuntimeSkillDiscoveryState> {
    const storageRoot = resolveManagedSkillsRoot(options.getManagedRoot())
    try {
      const skills = await listManagedSkills(storageRoot)
      return {
        skills,
        unavailable: false,
        error: null,
        storageRoot,
      }
    }
    catch (error) {
      logger.warn(
        'managed skill discovery unavailable; returning empty skill list',
        error instanceof Error ? error : String(error),
      )
      return {
        skills: [],
        unavailable: true,
        error: error instanceof Error ? error.message : String(error),
        storageRoot,
      }
    }
  }

  async function importSkillFromDialog() {
    const selection = await dialog.showOpenDialog({
      title: '导入技能',
      buttonLabel: '选择技能文件夹',
      properties: ['openDirectory'],
    })

    if (selection.canceled || selection.filePaths.length === 0) {
      throw new Error('技能导入已取消')
    }

    const sourcePath = selection.filePaths[0]!
    await assertSkillDirectory(sourcePath)

    const metadata = await readSkillMetadata(sourcePath)
    const importedName = metadata.name || path.basename(sourcePath)
    const skillId = slugifySkillName(importedName)
    const destinationRoot = resolveManagedSkillsRoot(options.getManagedRoot())
    const destinationPath = path.join(destinationRoot, skillId)

    await mkdir(destinationRoot, { recursive: true })
    await assertSkillCanBeImported(destinationRoot, importedName, skillId)
    await cp(sourcePath, destinationPath, { recursive: true, errorOnExist: true, force: false })

    logger.info('skill imported', { importedName, destinationPath, skillId })

    return { importedName, destinationPath, skillId }
  }

  async function deleteSkill(skillId: string) {
    const normalizedId = normalizeText(skillId)
    if (!normalizedId) {
      throw new Error('技能 ID 不能为空')
    }

    const destinationRoot = resolveManagedSkillsRoot(options.getManagedRoot())
    const skillPath = path.join(destinationRoot, normalizedId)
    const existing = await stat(skillPath).catch(() => null)
    if (!existing?.isDirectory()) {
      throw new Error(`未找到技能：${normalizedId}`)
    }

    await rm(skillPath, { recursive: true, force: false })
    logger.info('skill deleted', { skillId: normalizedId, skillPath })
    return { success: true }
  }
}

export async function listManagedSkills(storageRoot: string): Promise<OpencodeSkillRecord[]> {
  await mkdir(storageRoot, { recursive: true })
  const entries = await readdir(storageRoot, { withFileTypes: true })
  const skills = await Promise.all(
    entries
      .filter(entry => entry.isDirectory())
      .map(async (entry) => {
        const directoryPath = path.join(storageRoot, entry.name)
        const metadata = await readSkillMetadata(directoryPath).catch(() => null)
        if (!metadata?.name) {
          return null
        }

        return {
          id: entry.name,
          type: 'opencode_skill' as const,
          name: metadata.name,
          description: metadata.description || 'No description provided.',
          source: 'global' as const,
        }
      }),
  )

  return skills
    .filter((skill): skill is OpencodeSkillRecord => Boolean(skill))
    .sort((left, right) => left.name.localeCompare(right.name))
}

function resolveManagedSkillsRoot(managedRoot: string) {
  return path.join(managedRoot, '.agents', 'skills')
}

async function readSkillMetadata(skillDirectoryPath: string) {
  const skillFilePath = path.join(skillDirectoryPath, 'SKILL.md')
  const raw = await readFile(skillFilePath, 'utf8')
  const frontmatter = raw.match(/^---\r?\n([\s\S]*?)\r?\n---/m)?.[1] || ''
  const heading = raw.match(/^#\s+(.+)$/m)?.[1] || ''

  const name = normalizeFrontmatterValue(frontmatter.match(/^name:\s*(.+)$/m)?.[1]) || normalizeText(heading) || path.basename(skillDirectoryPath)
  const description = normalizeFrontmatterValue(frontmatter.match(/^description:\s*(.+)$/m)?.[1]) || null

  return { name, description }
}

function normalizeText(value: unknown) {
  return typeof value === 'string' && value.trim() ? value.trim() : null
}

function normalizeFrontmatterValue(value: unknown) {
  const normalized = normalizeText(value)
  if (!normalized) return null
  return normalized.replace(/^['"]|['"]$/g, '').trim() || null
}

function normalizeSkillName(value: string) {
  return value.trim().replace(/\s+/g, ' ').toLocaleLowerCase()
}

function slugifySkillName(value: string) {
  const normalized = value
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-zA-Z0-9\u4E00-\u9FFF]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .toLocaleLowerCase()

  return normalized || 'skill'
}

async function assertSkillDirectory(sourcePath: string) {
  const sourceStat = await stat(sourcePath).catch(() => null)
  if (!sourceStat?.isDirectory()) {
    throw new Error('请选择包含 SKILL.md 的技能文件夹')
  }

  const skillFilePath = path.join(sourcePath, 'SKILL.md')
  try {
    await access(skillFilePath)
  }
  catch {
    throw new Error('所选文件夹中没有找到 SKILL.md，无法导入为技能')
  }
}

async function assertSkillCanBeImported(destinationRoot: string, skillName: string, skillId: string) {
  const existingSkills = await listManagedSkills(destinationRoot)
  const normalizedName = normalizeSkillName(skillName)
  if (existingSkills.some(skill => normalizeSkillName(skill.name) === normalizedName)) {
    throw new Error(`已存在同名技能：${skillName}`)
  }

  const destinationPath = path.join(destinationRoot, skillId)
  const existing = await stat(destinationPath).catch(() => null)
  if (existing) {
    throw new Error(`已存在同名技能目录：${skillId}`)
  }
}
