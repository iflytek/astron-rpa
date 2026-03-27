<script setup lang="ts">
import {
  ArrowUpRight,
  Eye,
  FileCode2,
  FileImage,
  FileSpreadsheet,
  FileText,
  FolderOpen,
  Link2,
} from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'

import { utilsManager } from '@/platform'

import ArtifactPreviewSurface from './ArtifactPreviewSurface.vue'
import ModalShell from './ModalShell.vue'

import type {
  StudioArtifact,
  StudioArtifactPreviewPayload,
  StudioChatCard,
  StudioSessionDetail,
  StudioWorkspaceFile,
} from '../types'

type WorkspaceFilter = 'all' | 'file' | 'image' | 'code' | 'link'

interface WorkspaceEntry {
  id: string
  name: string
  kind: WorkspaceFilter
  meta: string
  artifactId?: string
}

const props = defineProps<{
  session: StudioSessionDetail
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'select-artifact', artifactId: string): void
}>()

const activeFilter = ref<WorkspaceFilter>('all')
const previewEntryId = ref('')

const baseFilters: Array<{ id: WorkspaceFilter, label: string }> = [
  { id: 'all', label: '全部' },
  { id: 'file', label: '文件' },
  { id: 'image', label: '图片' },
  { id: 'code', label: '代码文件' },
  { id: 'link', label: '外部链接' },
]

const workspaceRoot = computed(() => props.session.workspacePath || '~/Documents')

function classifyName(name: string): WorkspaceFilter {
  const lower = name.toLowerCase()
  if (/^https?:\/\//.test(lower) || lower.endsWith('.url') || lower.endsWith('.link'))
    return 'link'
  if (/\.(png|jpg|jpeg|gif|webp|svg)$/i.test(lower))
    return 'image'
  if (/\.(ts|tsx|js|jsx|vue|json|py|java|go|rs|md)$/i.test(lower))
    return 'code'
  return 'file'
}

function resolveArtifactMeta(artifact: StudioArtifact, kind: WorkspaceFilter) {
  if (kind === 'link')
    return '外部链接'
  return artifact.tag || '工作空间文件'
}

function resolveFileMeta(file: StudioWorkspaceFile, kind: WorkspaceFilter) {
  if (kind === 'link')
    return '外部链接'
  return file.status || '工作空间文件'
}

const workspaceEntries = computed<WorkspaceEntry[]>(() => {
  const artifactByName = new Map(
    props.session.artifacts.map(artifact => [artifact.name, artifact]),
  )

  const entries: WorkspaceEntry[] = props.session.workspaceFiles
    .filter(file => file.type === 'file')
    .map((file) => {
      const kind = classifyName(file.name)
      const artifact = artifactByName.get(file.name)
      return {
        id: artifact ? `artifact-${artifact.id}` : `file-${file.id}`,
        name: file.name,
        kind,
        meta: artifact ? resolveArtifactMeta(artifact, kind) : resolveFileMeta(file, kind),
        artifactId: artifact?.id,
      }
    })

  props.session.artifacts.forEach((artifact) => {
    if (entries.some(entry => entry.name === artifact.name))
      return

    const kind = classifyName(artifact.name)
    entries.push({
      id: `artifact-${artifact.id}`,
      name: artifact.name,
      kind,
      meta: resolveArtifactMeta(artifact, kind),
      artifactId: artifact.id,
    })
  })

  return entries
})

const filters = computed(() => {
  const kinds = new Set(workspaceEntries.value.map(entry => entry.kind))
  return baseFilters.filter(filter => filter.id === 'all' || kinds.has(filter.id))
})

watch(filters, (value) => {
  if (!value.some(filter => filter.id === activeFilter.value))
    activeFilter.value = 'all'
}, { immediate: true })

watch(() => props.session.id, () => {
  activeFilter.value = 'all'
  previewEntryId.value = ''
})

const filteredEntries = computed(() => {
  if (activeFilter.value === 'all')
    return workspaceEntries.value
  return workspaceEntries.value.filter(entry => entry.kind === activeFilter.value)
})

function findArtifact(entry: WorkspaceEntry) {
  if (!entry.artifactId)
    return null
  return props.session.artifacts.find(artifact => artifact.id === entry.artifactId) || null
}

function previewFromArtifact(artifact: StudioArtifact | null): StudioArtifactPreviewPayload | null {
  if (!artifact)
    return null

  if (artifact.preview)
    return artifact.preview

  if (props.session.workspacePreview?.fileName === artifact.name)
    return props.session.workspacePreview

  for (const card of props.session.chatCards || []) {
    if (card.type === 'artifact-preview' && card.preview?.fileName === artifact.name)
      return card.preview

    if (card.type === 'code' && card.fileName === artifact.name) {
      return {
        kind: 'code',
        fileName: card.fileName,
        status: card.tag || artifact.tag,
        title: card.fileName,
        language: card.language,
        code: card.code,
      }
    }

    if (card.type === 'draft-review' && artifact.name.endsWith('.eml'))
      return previewFromDraftCard(card, artifact)
  }

  return null
}

function previewFromDraftCard(card: Extract<StudioChatCard, { type: 'draft-review' }>, artifact: StudioArtifact): StudioArtifactPreviewPayload {
  return {
    kind: 'summary',
    fileName: artifact.name,
    status: artifact.tag,
    title: card.title,
    description: card.subject || '工作空间预览',
    items: [
      { label: '收件对象', value: card.recipients?.join('、') || '待补充', tone: 'default' },
      { label: '当前状态', value: artifact.tag, tone: artifact.tag.includes('已') ? 'success' : 'default' },
      { label: '下一步', value: '确认内容后继续发送，或同步到后续任务。', tone: 'default' },
    ],
  }
}

function resolvePreview(entry: WorkspaceEntry) {
  return previewFromArtifact(findArtifact(entry))
}

const previewEntry = computed(() => workspaceEntries.value.find(entry => entry.id === previewEntryId.value) || null)
const previewPayload = computed(() => previewEntry.value ? resolvePreview(previewEntry.value) : null)

function hasPreview(entry: WorkspaceEntry) {
  return !!resolvePreview(entry)
}

function entryIcon(entry: WorkspaceEntry) {
  if (entry.kind === 'image')
    return FileImage
  if (entry.kind === 'code')
    return FileCode2
  if (entry.kind === 'link')
    return Link2
  if (/\.(xlsx|csv)$/i.test(entry.name))
    return FileSpreadsheet
  return FileText
}

function entryIconTone(entry: WorkspaceEntry) {
  if (entry.kind === 'image')
    return 'bg-[#EEF2FF] text-[#5B67D6]'
  if (entry.kind === 'code')
    return 'bg-[#EEF4FF] text-[#2563EB]'
  if (entry.kind === 'link')
    return 'bg-[#F5F7FA] text-black/56'
  if (/\.(xlsx|csv)$/i.test(entry.name))
    return 'bg-[#ECFDF3] text-[#15803D]'
  return 'bg-[#F4F4F5] text-black/56'
}

async function openWorkspaceDirectory() {
  await utilsManager.shellopen(workspaceRoot.value)
}

async function openEntryLocation(entry: WorkspaceEntry, event: MouseEvent) {
  event.stopPropagation()

  if (entry.kind === 'link' && /^https?:\/\//.test(entry.name)) {
    await utilsManager.shellopen(entry.name)
    return
  }

  const targetPath = await utilsManager.pathJoin([workspaceRoot.value, entry.name])
  await utilsManager.shellopen(targetPath)
}

function selectEntry(entry: WorkspaceEntry) {
  if (entry.artifactId)
    emit('select-artifact', entry.artifactId)
  emit('close')
}

function openPreview(entry: WorkspaceEntry, event: MouseEvent) {
  event.stopPropagation()
  previewEntryId.value = entry.id
}

function closePreview() {
  previewEntryId.value = ''
}
</script>

<template>
  <ModalShell
    title="此任务中的所有档案"
    width-class="w-full max-w-[1040px]"
    close-label="关闭工作空间"
    overlay-class="z-30"
    panel-class="rounded-[24px]"
    header-class="px-6 py-4.5"
    body-class="px-6 pb-6 pt-3"
    panel-test-id="workspace-modal"
    overlay-test-id="workspace-overlay-shell"
    @close="emit('close')"
  >
    <template #icon>
      <FolderOpen class="h-4 w-4" />
    </template>

    <div class="space-y-4">
      <div
        data-testid="workspace-root-bar"
        class="flex items-center justify-between gap-4 rounded-[18px] bg-[var(--ai-surface-soft)] px-4 py-3 shadow-[inset_0_0_0_1px_rgba(228,234,245,0.92)]"
      >
        <div class="min-w-0">
          <div class="text-[11px] font-medium leading-4 text-black/38">当前工作目录</div>
          <div
            data-testid="workspace-root-path"
            class="mt-1 truncate font-mono text-[12px] leading-5 text-[#2A2A2A]"
          >
            {{ workspaceRoot }}
          </div>
        </div>

        <button
          data-testid="workspace-root-open"
          type="button"
          class="shrink-0 rounded-full bg-white px-3 py-1.5 text-[11px] leading-4 text-black/56 shadow-[inset_0_0_0_1px_rgba(228,234,245,0.96)] transition-colors hover:bg-[var(--ai-surface-soft)] hover:text-black/72"
          @click="openWorkspaceDirectory"
        >
          <span class="inline-flex items-center gap-1.5">
            <ArrowUpRight class="h-3.5 w-3.5" />
            打开目录
          </span>
        </button>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <button
          v-for="filter in filters"
          :key="filter.id"
          :data-testid="`workspace-filter-${filter.id}`"
          type="button"
          class="rounded-full px-3.5 py-1.5 text-[11px] leading-4 transition-colors"
          :class="activeFilter === filter.id
            ? 'bg-[#1F1F1F] text-white shadow-[0_6px_14px_rgba(31,31,31,0.12)]'
            : 'bg-[var(--ai-surface-soft)] text-black/52 shadow-[inset_0_0_0_1px_rgba(228,234,245,0.9)] hover:bg-white hover:text-black/68'"
          @click="activeFilter = filter.id"
        >
          {{ filter.label }}
        </button>
      </div>

      <div class="text-[11px] leading-4 text-black/36">
        当前会话产物
      </div>

      <div v-if="filteredEntries.length" class="space-y-1">
        <button
          v-for="entry in filteredEntries"
          :key="entry.id"
          :data-testid="`workspace-file-item-${entry.id}`"
          type="button"
          class="flex w-full items-center gap-3 rounded-[16px] px-3.5 py-3 text-left transition-colors hover:bg-[#F7F8FA]"
          @click="selectEntry(entry)"
        >
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-[12px]" :class="entryIconTone(entry)">
            <component :is="entryIcon(entry)" class="h-4.5 w-4.5" />
          </div>

          <div class="min-w-0 flex-1">
            <div class="truncate text-[14px] font-medium leading-5 text-[#2A2A2A]">{{ entry.name }}</div>
            <div class="truncate text-[11px] leading-4 text-black/42">{{ entry.meta }}</div>
          </div>

          <div class="flex shrink-0 items-center gap-2">
            <button
              v-if="hasPreview(entry)"
              :data-testid="`workspace-preview-trigger-${entry.id}`"
              type="button"
              class="rounded-full bg-white px-2.5 py-1 text-[11px] leading-4 text-black/54 shadow-[inset_0_0_0_1px_rgba(228,234,245,0.96)] transition-colors hover:bg-[var(--ai-surface-soft)] hover:text-black/68"
              @click="openPreview(entry, $event)"
            >
              <span class="inline-flex items-center gap-1">
                <Eye class="h-3 w-3" />
                预览
              </span>
            </button>

            <button
              :data-testid="`workspace-open-location-${entry.id}`"
              type="button"
              class="rounded-full bg-white px-2.5 py-1 text-[11px] leading-4 text-black/54 shadow-[inset_0_0_0_1px_rgba(228,234,245,0.96)] transition-colors hover:bg-[var(--ai-surface-soft)] hover:text-black/68"
              @click="openEntryLocation(entry, $event)"
            >
              <span class="inline-flex items-center gap-1">
                <ArrowUpRight class="h-3 w-3" />
                {{ entry.kind === 'link' ? '打开链接' : '打开位置' }}
              </span>
            </button>
          </div>
        </button>
      </div>

      <div
        v-else
        class="flex min-h-[220px] items-center justify-center rounded-[18px] bg-[var(--ai-surface-soft)] text-[13px] text-black/42 shadow-[inset_0_0_0_1px_rgba(228,234,245,0.9)]"
      >
        当前分类下暂无文件
      </div>
    </div>
  </ModalShell>

  <ModalShell
    v-if="previewPayload && previewEntry"
    :title="previewEntry.name"
    description="工作空间预览"
    width-class="w-full max-w-[720px]"
    close-label="关闭预览"
    overlay-class="z-40 bg-[rgba(15,23,42,0.16)] backdrop-blur-[2px]"
    panel-class="rounded-[22px]"
    header-class="px-5 py-3.5"
    body-class="px-0 pb-0 pt-0"
    panel-test-id="workspace-preview-dialog"
    @close="closePreview"
  >
    <template #icon>
      <component :is="entryIcon(previewEntry)" class="h-4 w-4" />
    </template>

    <ArtifactPreviewSurface :preview="previewPayload" compact />
  </ModalShell>
</template>
