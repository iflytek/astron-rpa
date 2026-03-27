<script setup lang="ts">
import { Users } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'

import { Input } from '@/components/ui/input'

import ModalActionBar from './ModalActionBar.vue'
import ModalShell from './ModalShell.vue'

import type { StudioCollaborationMode } from '../types'

type SessionParticipantCandidate = {
  id: string
  name: string
  badge: string
}

const props = defineProps<{
  assistantName: string
  defaultWorkspacePath?: string
  isGroupSession?: boolean
  groupTemplateParticipants?: SessionParticipantCandidate[]
  groupTemplateMode?: StudioCollaborationMode
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'submit', payload: {
    workspacePath: string
    sessionTitle?: string
  }): void
}>()

const workspacePath = ref(props.defaultWorkspacePath || '~/Documents')
const sessionTitle = ref('')

const isGroupSessionMode = computed(() => !!props.isGroupSession)
const groupTemplateParticipants = computed(() => props.groupTemplateParticipants || [])
const groupTemplateMode = computed(() => props.groupTemplateMode || 'auto')
const groupTemplateModeLabel = computed(() => {
  if (groupTemplateMode.value === 'pipeline')
    return '流水线'
  if (groupTemplateMode.value === 'race')
    return '赛马'
  if (groupTemplateMode.value === 'debate')
    return '会审'
  return '自动'
})
const canCreate = computed(() => {
  if (!isGroupSessionMode.value)
    return workspacePath.value.trim().length > 0
  return workspacePath.value.trim().length > 0 && sessionTitle.value.trim().length > 0
})

watch(
  () => [props.defaultWorkspacePath, props.isGroupSession, props.assistantName],
  () => {
    workspacePath.value = props.defaultWorkspacePath || '~/Documents'
    sessionTitle.value = `${props.assistantName}协作会话`
  },
  { immediate: true },
)

function handleSubmit() {
  if (!canCreate.value)
    return
  if (!isGroupSessionMode.value) {
    emit('submit', { workspacePath: workspacePath.value.trim() })
    return
  }

  emit('submit', {
    workspacePath: workspacePath.value.trim(),
    sessionTitle: sessionTitle.value.trim(),
  })
}
</script>

<template>
  <ModalShell
    :title="isGroupSessionMode ? `新建「${props.assistantName}」群聊` : `与「${props.assistantName}」新建会话`"
    :description="isGroupSessionMode ? '群聊会话会绑定工作目录；参与助手与协作模式继承自群聊模板。' : undefined"
    :width-class="isGroupSessionMode ? 'w-[560px]' : 'w-[400px]'"
    close-label="关闭新建会话"
    @close="emit('close')"
  >
    <div data-testid="new-session-modal" class="px-6 py-5">
      <div class="space-y-4">
        <div v-if="isGroupSessionMode" class="space-y-1.5">
          <label class="block text-[12px] font-medium leading-4 text-black/76">会话名称</label>
          <Input
            v-model="sessionTitle"
            data-testid="new-group-session-title-input"
            class="h-10 rounded-[12px] border border-[#E5E7EB] bg-white px-3 text-[13px] text-black/72 shadow-none"
            placeholder="例如：合同审查联调协作"
          />
        </div>

        <div class="space-y-1.5">
          <label class="block text-[12px] font-medium leading-4 text-black/76">工作目录</label>
          <Input
            v-model="workspacePath"
            data-testid="new-session-workspace-input"
            class="h-10 rounded-[12px] border border-[#E5E7EB] bg-white px-3 text-[13px] text-black/72 shadow-none"
            placeholder="请输入工作目录，例如 ~/Projects/demo"
          />
        </div>

        <template v-if="isGroupSessionMode">
          <div class="rounded-[12px] bg-[#F8FAFF] px-3 py-2 text-[11px] leading-5 text-black/52">
            主 Agent 为系统通用协调器：负责澄清、分发、汇总；不绑定 Skills/MCP，不直接执行任务。
          </div>

          <div class="space-y-2">
            <label class="flex items-center gap-1.5 text-[12px] font-medium leading-4 text-black/76">
              <Users class="h-3.5 w-3.5 text-black/52" />
              模板配置（只读）
            </label>
            <div class="rounded-[12px] border border-[#E5E7EB] bg-white px-3 py-2.5">
              <div class="text-[11px] leading-5 text-black/56">
                协作模式：<span class="font-medium text-black/70">{{ groupTemplateModeLabel }}</span>
              </div>
              <div class="mt-1 flex flex-wrap gap-1.5">
                <span
                  v-for="participant in groupTemplateParticipants"
                  :key="participant.id"
                  class="inline-flex items-center gap-1.5 rounded-full bg-[#F5F7FF] px-2.5 py-1 text-[11px] text-black/62"
                >
                  <span class="inline-flex h-4 w-4 items-center justify-center rounded-full bg-white text-[9px] font-semibold text-black/58">
                    {{ participant.badge }}
                  </span>
                  <span>{{ participant.name }}</span>
                </span>
                <span v-if="groupTemplateParticipants.length === 0" class="text-[11px] text-black/42">未配置参与助手</span>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <ModalActionBar
      test-id="session"
      :submit-label="isGroupSessionMode ? '创建群聊' : '开始'"
      :submit-disabled="!canCreate"
      @cancel="emit('close')"
      @submit="handleSubmit"
    />
  </ModalShell>
</template>
