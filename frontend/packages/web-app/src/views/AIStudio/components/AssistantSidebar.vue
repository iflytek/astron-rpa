<script setup lang="ts">
import { MoreHorizontal, Pencil, Plus, Search, Settings, Trash2, Users, Zap } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'

import type { StudioAssistant, StudioAssistantGroup, StudioSession } from '../types'

interface SidebarAssistantEntry extends StudioAssistant {
  groupId: string
  isCollaboration: boolean
}

interface VisibleSidebarAssistant {
  assistant: SidebarAssistantEntry
  sessions: StudioSession[]
  expanded: boolean
}

const props = defineProps<{
  groups: StudioAssistantGroup[]
  activeSessionId: string
  activeSurface?: 'main' | 'automation' | 'settings'
}>()

const emit = defineEmits<{
  (e: 'select-session', assistantId: string, sessionId: string): void
  (e: 'open-new-assistant'): void
  (e: 'open-new-group-template'): void
  (e: 'open-edit-assistant', assistantId: string): void
  (e: 'open-new-session', assistantId: string): void
  (e: 'delete-assistant', assistantId: string): void
  (e: 'delete-session', assistantId: string, sessionId: string): void
  (e: 'open-automation'): void
  (e: 'open-settings'): void
}>()

const searchQuery = ref('')
const focusedAssistantId = ref('')
const confirmingAssistantDeleteId = ref<string | null>(null)

const unifiedAssistants = computed<SidebarAssistantEntry[]>(() =>
  props.groups.flatMap(group =>
    group.assistants.map(assistant => ({
      ...assistant,
      groupId: group.id,
      isCollaboration: group.id === 'collaboration',
    })),
  ),
)

const normalizedSearchQuery = computed(() => searchQuery.value.trim().toLocaleLowerCase())
const hasCollaborationAssistant = computed(() =>
  unifiedAssistants.value.some(assistant => assistant.isCollaboration),
)

const visibleAssistants = computed<VisibleSidebarAssistant[]>(() => {
  const query = normalizedSearchQuery.value

  if (!query) {
    return unifiedAssistants.value.map(assistant => ({
      assistant,
      sessions: assistant.sessions,
      expanded: assistant.id === focusedAssistantId.value,
    }))
  }

  return unifiedAssistants.value.flatMap((assistant) => {
    const assistantMatches = assistant.name.toLocaleLowerCase().includes(query)
    const matchedSessions = assistant.sessions.filter(session =>
      session.title.toLocaleLowerCase().includes(query),
    )

    if (!assistantMatches && matchedSessions.length === 0)
      return []

    return [{
      assistant,
      sessions: assistantMatches ? assistant.sessions : matchedSessions,
      expanded: true,
    }]
  })
})

function resolveAssistantIdBySession(sessionId: string) {
  return unifiedAssistants.value.find(assistant =>
    assistant.sessions.some(session => session.id === sessionId),
  )?.id
}

function syncFocusedAssistant() {
  const assistants = unifiedAssistants.value

  if (!assistants.length) {
    focusedAssistantId.value = ''
    return
  }

  const activeAssistantId = resolveAssistantIdBySession(props.activeSessionId)
  if (activeAssistantId) {
    focusedAssistantId.value = activeAssistantId
    return
  }

  if (!assistants.some(assistant => assistant.id === focusedAssistantId.value))
    focusedAssistantId.value = assistants[0].id
}

watch(() => props.activeSessionId, syncFocusedAssistant, { immediate: true })
watch(unifiedAssistants, syncFocusedAssistant)

function canExpand(assistant: StudioAssistant) {
  return assistant.sessions.length > 0
}

function focusAssistant(assistantId: string) {
  focusedAssistantId.value = assistantId
  confirmingAssistantDeleteId.value = null
}

function isRunning(assistant: SidebarAssistantEntry) {
  return assistant.status === '运行中'
}

function assistantAvatarTone(assistantId: string) {
  if (assistantId === 'office')
    return 'bg-[linear-gradient(135deg,#EFF6FF,#DBEAFE)] text-[#1D4ED8] ring-[#1D4ED8]/10'
  if (assistantId === 'code')
    return 'bg-[linear-gradient(135deg,#F0FDF4,#DCFCE7)] text-[#16A34A] ring-[#16A34A]/10'
  if (assistantId === 'data')
    return 'bg-[linear-gradient(135deg,#FFF7ED,#FFEDD5)] text-[#EA580C] ring-[#EA580C]/10'
  return 'bg-[linear-gradient(135deg,#F3F1FF,#E8E5FF)] text-[#726FFF] ring-[#726FFF]/10'
}

function groupAvatarMembers(assistantId: string) {
  if (assistantId === 'audit-group')
    return ['finance', 'code']
  return []
}

function groupAvatarTone(memberId: string) {
  if (memberId === 'code')
    return 'bg-[#16A34A] text-white shadow-[0_0_0_2px_rgba(255,255,255,0.96)]'
  if (memberId === 'data')
    return 'bg-[#EA580C] text-white shadow-[0_0_0_2px_rgba(255,255,255,0.96)]'
  return 'bg-[#726FFF] text-white shadow-[0_0_0_2px_rgba(255,255,255,0.96)]'
}

function groupAvatarLabel(memberId: string) {
  if (memberId === 'code')
    return '代'
  if (memberId === 'data')
    return '数'
  return '财'
}

function handleAssistantMenuAction(action: 'edit' | 'delete', assistantId: string) {
  if (action !== 'delete')
    confirmingAssistantDeleteId.value = null
  if (action === 'edit') {
    emit('open-edit-assistant', assistantId)
    return
  }
  emit('delete-assistant', assistantId)
}

function showAssistantDeleteConfirm(assistantId: string) {
  confirmingAssistantDeleteId.value = assistantId
}

function cancelAssistantDeleteConfirm() {
  confirmingAssistantDeleteId.value = null
}
</script>

<template>
  <aside
    data-testid="ai-sidebar-shell"
    class="relative my-3 ml-3 mr-2.5 flex min-h-0 w-[clamp(276px,19.5vw,320px)] shrink-0 self-stretch flex-col overflow-hidden rounded-[24px] bg-[linear-gradient(180deg,rgba(255,255,255,0.74)_0%,rgba(252,252,255,0.9)_22%,rgba(255,255,255,0.94)_100%)] shadow-[0_14px_34px_rgba(15,23,42,0.028)] backdrop-blur-[16px]"
    style="font-family: var(--font-sans-ui);"
  >
    <div class="pointer-events-none absolute inset-x-0 top-0 h-24 bg-[radial-gradient(circle_at_top_left,rgba(114,111,255,0.10),transparent_62%)]" />

    <div class="relative px-4 pb-3 pt-4">
      <a-dropdown :trigger="['click']" placement="bottomLeft" :destroy-popup-on-hide="true" overlay-class-name="ai-sidebar-create-menu-overlay">
        <Button
          size="sm"
          data-testid="template-create-trigger"
          class="h-10 w-full justify-center gap-2 rounded-[15px] bg-[linear-gradient(135deg,#726FFF,#5D59FF)] text-[13px] font-semibold shadow-[0_10px_18px_rgba(114,111,255,0.16)] hover:translate-y-0"
        >
          <Plus class="h-4 w-4" />
          <span>新建模板</span>
        </Button>
        <template #overlay>
          <div class="w-[188px] rounded-[16px] bg-[rgba(255,255,255,0.98)] p-1.5 shadow-[0_18px_40px_rgba(15,23,42,0.12)] backdrop-blur-[18px]">
            <button
              data-testid="create-assistant-template"
              class="flex w-full items-center gap-2 rounded-[12px] px-3 py-2 text-left transition-colors hover:bg-[#F6F8FF]"
              @click="emit('open-new-assistant')"
            >
              <Plus class="h-3.5 w-3.5 text-black/52" />
              <span class="text-[12px] leading-4 text-black/74">新建助手模板</span>
            </button>
            <button
              v-if="hasCollaborationAssistant"
              data-testid="create-group-template"
              class="flex w-full items-center gap-2 rounded-[12px] px-3 py-2 text-left transition-colors hover:bg-[#F6F8FF]"
              @click="emit('open-new-group-template')"
            >
              <Users class="h-3.5 w-3.5 text-[#5E5AE8]" />
              <span class="text-[12px] leading-4 text-black/74">新建群聊模板</span>
            </button>
          </div>
        </template>
      </a-dropdown>
    </div>

    <div class="relative px-4 pb-2">
      <div class="relative">
        <Search class="pointer-events-none absolute left-3.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-black/28" />
        <Input
          v-model="searchQuery"
          data-testid="assistant-search-input"
          class="h-9 rounded-[14px] border-0 bg-white/88 pl-9 text-[13px] shadow-[inset_0_0_0_1px_rgba(215,224,239,0.72)] shadow-none focus:ring-[3px]"
          placeholder="搜索助手或会话..."
        />
      </div>
    </div>

    <ScrollArea class="relative min-h-0 flex-1 px-3 pb-4 pt-0.5">
      <div data-testid="assistant-list" class="space-y-1 rounded-[18px] bg-white/28 px-1.5 py-1.5 pb-4">
        <template v-if="visibleAssistants.length">
          <div
            v-for="{ assistant, sessions, expanded } in visibleAssistants"
            :key="assistant.id"
            class="space-y-0.5"
          >
            <div
              :data-testid="`assistant-shell-${assistant.id}`"
              class="group/assistant relative flex items-center gap-1.5 rounded-[14px] px-2.5 py-1.5 transition-all duration-200"
              :class="assistant.id === focusedAssistantId
                ? 'bg-[linear-gradient(180deg,rgba(255,255,255,0.82)_0%,rgba(245,244,255,0.92)_100%)] shadow-[0_10px_22px_rgba(114,111,255,0.08)]'
                : 'opacity-[0.88] hover:bg-white/42 hover:opacity-100'"
            >
              <span
                v-if="assistant.id === focusedAssistantId"
                :data-testid="`assistant-focus-indicator-${assistant.id}`"
                class="absolute left-0 top-1/2 h-7 w-[2px] -translate-y-1/2 rounded-full bg-[linear-gradient(180deg,rgba(114,111,255,0.18)_0%,rgba(114,111,255,0.72)_48%,rgba(114,111,255,0.22)_100%)] shadow-[0_0_0_4px_rgba(114,111,255,0.06)]"
              />
              <button
                :data-testid="`assistant-row-${assistant.id}`"
                class="flex min-w-0 flex-1 items-center gap-2 text-left"
                @click="focusAssistant(assistant.id)"
              >
                <div
                  v-if="!assistant.isCollaboration"
                  :data-testid="`assistant-avatar-${assistant.id}`"
                  :class="assistantAvatarTone(assistant.id)"
                  class="flex h-8 w-8 shrink-0 items-center justify-center rounded-[12px] ring-1"
                >
                  <span class="text-[11px] font-semibold">{{ assistant.badge }}</span>
                </div>
                <div
                  v-else
                  :data-testid="`assistant-avatar-${assistant.id}`"
                  class="relative h-8 w-9 shrink-0"
                >
                  <div
                    v-for="(memberId, index) in groupAvatarMembers(assistant.id)"
                    :key="memberId"
                    :class="groupAvatarTone(memberId)"
                    :style="{ left: `${index * 12}px`, top: index === 0 ? '1px' : '7px' }"
                    class="absolute flex h-6 w-6 items-center justify-center rounded-[9px] text-[9px] font-bold"
                  >
                    {{ groupAvatarLabel(memberId) }}
                  </div>
                </div>

                <div class="min-w-0 flex-1">
                  <div class="flex items-center gap-2">
                    <span
                      :data-testid="`assistant-title-${assistant.id}`"
                      class="truncate text-[12px] font-medium leading-[18px]"
                      :class="assistant.id === focusedAssistantId ? 'text-black/84' : 'text-black/68'"
                    >
                      {{ assistant.name }}
                    </span>
                    <span
                      v-if="isRunning(assistant)"
                      class="inline-flex shrink-0 items-center gap-1 rounded-full bg-[#F0FDF4] px-2 py-0.5 text-[10px] font-medium text-[#16A34A]"
                    >
                      <span class="h-1.5 w-1.5 rounded-full bg-[#2FCB64]" />
                      <span>运行中</span>
                    </span>
                  </div>
                </div>
              </button>

              <button
                :data-testid="`assistant-new-session-trigger-${assistant.id}`"
                class="flex h-7 w-7 shrink-0 items-center justify-center rounded-[10px] bg-[rgba(114,111,255,0.06)] text-[#716DF8] shadow-[0_4px_12px_rgba(114,111,255,0.06)] transition-all hover:bg-[rgba(114,111,255,0.10)] hover:text-[#5D59FF]"
                :class="assistant.id === focusedAssistantId ? 'opacity-100' : 'opacity-0 group-hover/assistant:opacity-100'"
                title="新建会话"
                @click.stop="emit('open-new-session', assistant.id)"
              >
                <Plus class="h-3.5 w-3.5" />
              </button>

              <a-dropdown :trigger="['click']" placement="bottomRight" :destroy-popup-on-hide="true" overlay-class-name="ai-sidebar-assistant-menu-overlay">
                <button
                  :data-testid="`assistant-more-trigger-${assistant.id}`"
                  class="flex h-7 w-7 shrink-0 items-center justify-center rounded-[10px] bg-white/70 text-black/42 shadow-[0_4px_12px_rgba(15,23,42,0.04)] transition-all hover:bg-white"
                  :class="assistant.id === focusedAssistantId ? 'opacity-100' : 'opacity-0 group-hover/assistant:opacity-100'"
                  title="更多操作"
                >
                  <MoreHorizontal class="h-3.5 w-3.5" />
                </button>
                <template #overlay>
                  <div
                    :data-testid="`assistant-actions-menu-${assistant.id}`"
                    class="w-[180px] rounded-[16px] bg-[rgba(255,255,255,0.98)] p-1.5 shadow-[0_18px_40px_rgba(15,23,42,0.12)] backdrop-blur-[18px]"
                  >
                    <button
                      data-testid="assistant-menu-edit"
                      class="flex w-full items-center gap-2 rounded-[12px] px-3 py-2 text-left transition-colors hover:bg-[#F6F8FF]"
                      @click.stop="handleAssistantMenuAction('edit', assistant.id)"
                    >
                      <Pencil class="h-3.5 w-3.5 shrink-0 text-black/46" />
                      <span class="text-[12px] leading-4 text-black/74">编辑助手</span>
                    </button>
                    <button
                      v-if="confirmingAssistantDeleteId !== assistant.id"
                      data-testid="assistant-menu-delete"
                      class="flex w-full items-center gap-2 rounded-[12px] px-3 py-2 text-left transition-colors hover:bg-[#FEF2F2]"
                      @click.stop="showAssistantDeleteConfirm(assistant.id)"
                    >
                      <Trash2 class="h-3.5 w-3.5 shrink-0 text-[#EF4444]" />
                      <span class="text-[12px] leading-4 text-[#EF4444]">删除助手</span>
                    </button>
                    <div v-else class="rounded-[14px] bg-[#FFF6F5] px-3 py-2.5">
                      <div class="text-[11px] font-medium leading-4 text-[#D14343]">删除后将同时移除该助手下的全部会话与产物视图。</div>
                      <div class="mt-2 flex items-center justify-end gap-2">
                        <button
                          class="rounded-[10px] px-2.5 py-1 text-[11px] leading-4 text-black/44 transition-colors hover:bg-white/70"
                          @click.stop="cancelAssistantDeleteConfirm()"
                        >
                          取消
                        </button>
                        <button
                          class="rounded-[10px] bg-[#EF4444] px-2.5 py-1 text-[11px] leading-4 text-white shadow-[0_8px_18px_rgba(239,68,68,0.16)]"
                          @click.stop="handleAssistantMenuAction('delete', assistant.id)"
                        >
                          删除助手
                        </button>
                      </div>
                    </div>
                  </div>
                </template>
              </a-dropdown>
            </div>

            <div
              v-if="expanded && canExpand(assistant)"
              :data-testid="`assistant-session-list-${assistant.id}`"
              class="space-y-0.5 pl-[38px] pr-1"
            >
              <div
                v-for="session in sessions"
                :key="session.id"
                :data-testid="`assistant-session-row-${assistant.id}-${session.id}`"
                class="group/session flex items-center gap-1.5 rounded-[10px] px-2 py-1 transition-all duration-150"
                :class="session.id === activeSessionId
                  ? 'bg-[rgba(114,111,255,0.10)] text-[#5E5AE8]'
                  : 'text-black/68 hover:bg-white/80 hover:text-black/84'"
              >
                <button
                  class="flex min-w-0 flex-1 items-center gap-2 text-left"
                  @click="emit('select-session', assistant.id, session.id)"
                >
                  <span
                    v-if="session.id === activeSessionId"
                    class="h-1.5 w-1.5 shrink-0 rounded-full bg-[#726FFF] shadow-[0_0_0_4px_rgba(114,111,255,0.08)]"
                  />
                  <span
                    :data-testid="`assistant-session-title-${assistant.id}-${session.id}`"
                    class="min-w-0 flex-1 truncate text-[12px] font-medium leading-[18px]"
                  >
                    {{ session.title }}
                  </span>
                </button>
                <div class="flex shrink-0 items-center gap-1 opacity-0 transition-all group-hover/session:opacity-100">
                  <a-popconfirm
                    placement="rightTop"
                    title="删除会话"
                    description="删除会话后，当前聊天记录和右侧产物预览将一并移除。"
                    ok-text="删除会话"
                    cancel-text="取消"
                    @confirm="emit('delete-session', assistant.id, session.id)"
                  >
                    <button
                      :data-testid="`session-delete-trigger-${assistant.id}-${session.id}`"
                      class="flex h-5 w-5 items-center justify-center rounded-[7px] transition-colors hover:bg-[#FEF2F2]"
                      title="删除会话"
                    >
                      <Trash2 class="h-3 w-3 text-[#EF4444]" />
                    </button>
                  </a-popconfirm>
                </div>
              </div>
            </div>
          </div>
        </template>

        <div
          v-else
          class="rounded-[18px] bg-white/72 px-4 py-8 text-center text-[12px] leading-5 text-black/42 shadow-[0_10px_24px_rgba(15,23,42,0.04)]"
        >
          没有匹配的助手或会话
        </div>
      </div>
    </ScrollArea>

    <div class="bg-[rgba(255,255,255,0.6)] px-3.5 pb-4 pt-2 backdrop-blur-[12px]">
      <div class="space-y-2">
        <button
          data-testid="sidebar-entry-automation"
          :class="props.activeSurface === 'automation' ? 'bg-[rgba(114,111,255,0.10)] text-[#726FFF]' : 'bg-white/56 text-black/66 hover:bg-white/80'"
          class="flex w-full items-center gap-3 rounded-[14px] px-3.5 py-2.5 text-left transition-colors"
          @click="emit('open-automation')"
        >
          <div
            :class="props.activeSurface === 'automation' ? 'bg-[#EEF2FF] text-[#726FFF]' : 'bg-[#F4F7FF] text-black/52'"
            class="flex h-7 w-7 shrink-0 items-center justify-center rounded-[10px]"
          >
            <Zap class="h-3.5 w-3.5" />
          </div>
          <span class="min-w-0 flex-1 truncate text-[12px] font-semibold">自动化任务</span>
        </button>

        <button
          data-testid="sidebar-entry-settings"
          :class="props.activeSurface === 'settings' ? 'bg-[rgba(114,111,255,0.10)] text-[#726FFF]' : 'bg-white/56 text-black/66 hover:bg-white/80'"
          class="flex w-full items-center gap-3 rounded-[14px] px-3.5 py-2.5 text-left transition-colors"
          @click="emit('open-settings')"
        >
          <div
            :class="props.activeSurface === 'settings' ? 'bg-[#EEF2FF] text-[#726FFF]' : 'bg-[#F4F7FF] text-black/52'"
            class="flex h-7 w-7 shrink-0 items-center justify-center rounded-[10px]"
          >
            <Settings class="h-3.5 w-3.5" />
          </div>
          <span class="min-w-0 flex-1 truncate text-[12px] font-semibold">配置中心</span>
        </button>
      </div>
    </div>

  </aside>
</template>
