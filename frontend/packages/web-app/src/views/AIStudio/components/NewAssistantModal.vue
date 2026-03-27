<script setup lang="ts">
import { Bot, Search, Users, Wrench, Zap } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'

import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'

import { aiStudioSkillRegistry } from '../registry'
import type { StudioAssistant, StudioCollaborationMode } from '../types'
import ModalActionBar from './ModalActionBar.vue'
import ModalShell from './ModalShell.vue'
import SegmentedPills from './SegmentedPills.vue'

type SessionParticipantCandidate = {
  id: string
  name: string
  badge: string
}

const props = withDefaults(defineProps<{
  mode?: 'create' | 'edit'
  assistant?: StudioAssistant | null
  templateKind?: 'assistant' | 'group'
  participantCandidates?: SessionParticipantCandidate[]
}>(), {
  mode: 'create',
  assistant: null,
  templateKind: 'assistant',
  participantCandidates: () => [],
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'submit', payload: {
    name: string
    persona: string
    capabilities: string
    skills: string[]
    templateKind: 'assistant' | 'group'
    groupParticipantAssistantIds?: string[]
    groupCollaborationMode?: StudioCollaborationMode
  }): void
}>()

const name = ref('')
const persona = ref('')
const capabilities = ref('')
const skillSearch = ref('')
const skills = ref<string[]>([])
const groupParticipants = ref<string[]>([])
const groupCollaborationMode = ref<StudioCollaborationMode>('auto')

const isEditMode = computed(() => props.mode === 'edit')
const resolvedTemplateKind = computed<'assistant' | 'group'>(() =>
  props.assistant?.status === '群聊' ? 'group' : props.templateKind || 'assistant',
)
const isGroupTemplate = computed(() => resolvedTemplateKind.value === 'group')
const canSubmit = computed(() => {
  if (!isGroupTemplate.value)
    return name.value.trim().length > 0
  return name.value.trim().length > 0 && groupParticipants.value.length > 0
})
const modalTitle = computed(() => {
  if (isGroupTemplate.value)
    return isEditMode.value ? '编辑群聊模板' : '新建群聊模板'
  return isEditMode.value ? '编辑 AI 助手模板' : '新建 AI 助手模板'
})
const modalDescription = computed(() => {
  if (isGroupTemplate.value)
    return '群聊模板仅定义协作入口，不绑定工作目录和执行技能。'
  return '助手模板用于定义角色与能力，不绑定工作目录。'
})
const submitLabel = computed(() => isEditMode.value ? '保存模板' : '创建模板')
const skillSummary = computed(() => skills.value.length > 0 ? `已选 ${skills.value.length} 项` : '按需连接')
const normalizedSkillQuery = computed(() => skillSearch.value.trim().toLocaleLowerCase())
const collaborationModeOptions: ReadonlyArray<{ value: StudioCollaborationMode, label: string }> = [
  { value: 'auto', label: '自动' },
  { value: 'pipeline', label: '流水线' },
  { value: 'race', label: '赛马' },
  { value: 'debate', label: '会审' },
]

const visibleSkillGroups = computed(() => {
  const query = normalizedSkillQuery.value
  return aiStudioSkillRegistry
    .map(group => ({
      ...group,
      skills: group.skills.filter(skill => !query
        || skill.label.toLocaleLowerCase().includes(query)
        || skill.description.toLocaleLowerCase().includes(query)),
    }))
    .filter(group => group.skills.length > 0)
})

function syncForm() {
  name.value = props.assistant?.name || ''
  persona.value = props.assistant?.persona || ''
  capabilities.value = props.assistant?.capabilities || ''
  skills.value = props.assistant?.skills ? [...props.assistant.skills] : []
  groupParticipants.value = props.assistant?.groupParticipantAssistantIds ? [...props.assistant.groupParticipantAssistantIds] : []
  groupCollaborationMode.value = props.assistant?.groupCollaborationMode || 'auto'
  skillSearch.value = ''
}

watch(() => props.assistant, syncForm, { immediate: true })
watch(() => props.mode, syncForm)

function toggleSkill(skill: string) {
  skills.value = skills.value.includes(skill)
    ? skills.value.filter(item => item !== skill)
    : [...skills.value, skill]
}

function toggleGroupParticipant(assistantId: string) {
  if (groupParticipants.value.includes(assistantId)) {
    groupParticipants.value = groupParticipants.value.filter(id => id !== assistantId)
    return
  }
  groupParticipants.value = [...groupParticipants.value, assistantId]
}

function handleSubmit() {
  if (!canSubmit.value)
    return
  emit('submit', {
    name: name.value.trim(),
    persona: persona.value.trim(),
    capabilities: capabilities.value.trim(),
    skills: [...skills.value],
    templateKind: resolvedTemplateKind.value,
    groupParticipantAssistantIds: isGroupTemplate.value ? [...groupParticipants.value] : undefined,
    groupCollaborationMode: isGroupTemplate.value ? groupCollaborationMode.value : undefined,
  })
}
</script>

<template>
  <ModalShell
    :title="modalTitle"
    :description="modalDescription"
    width-class="w-[520px]"
    close-label="关闭助手表单"
    @close="emit('close')"
  >
    <div data-testid="new-assistant-modal" class="space-y-5 px-6 py-5">
      <div class="space-y-1.5">
        <label class="text-[12px] font-medium text-black/78">{{ isGroupTemplate ? '模板名称' : '助手名称' }} <span class="text-[#EC483E]">*</span></label>
        <Input
          v-model="name"
          data-testid="new-assistant-name-input"
          class="h-10 rounded-[16px] border-0 bg-[var(--ai-surface-soft)] text-[13px] shadow-[inset_0_0_0_1px_rgba(215,224,239,0.9)]"
          :placeholder="isGroupTemplate ? '例如：财务+代码协作评审' : '例如：财务助手、代码审查官'"
        />
      </div>

      <div class="flex items-center gap-3">
        <Separator class="bg-[var(--ai-line-soft)]" />
        <span class="shrink-0 text-[10px] font-medium tracking-[0.08em] text-black/32">可选配置</span>
        <Separator class="bg-[var(--ai-line-soft)]" />
      </div>

      <div class="space-y-4">
        <div class="space-y-1.5">
          <label class="flex items-center gap-1.5 text-[12px] font-medium text-black/76">
            <Bot class="h-3.5 w-3.5 text-[var(--color-primary)]" />
            {{ isGroupTemplate ? '模板定位说明' : '人设与角色定义' }}
          </label>
          <textarea
            v-model="persona"
            rows="3"
            class="w-full resize-none rounded-[16px] border-0 bg-[var(--ai-surface-soft)] px-3 py-2.5 text-[13px] leading-6 text-black/76 shadow-[inset_0_0_0_1px_rgba(215,224,239,0.9)] outline-none transition-all placeholder:text-black/28 focus:ring-4 focus:ring-[var(--color-primary)]/8"
            :placeholder="isGroupTemplate ? '描述群聊模板的职责边界和适用任务…' : '描述助手的身份、性格和行为准则…'"
          />
        </div>

        <div v-if="isGroupTemplate" class="space-y-2">
          <label class="flex items-center gap-1.5 text-[12px] font-medium text-black/76">
            <Users class="h-3.5 w-3.5 text-black/52" />
            协作模式
          </label>
          <SegmentedPills
            v-model="groupCollaborationMode"
            test-id="group-template-collaboration-mode"
            :options="collaborationModeOptions"
          />
        </div>

        <div v-if="isGroupTemplate" class="space-y-2">
          <label class="text-[12px] font-medium text-black/76">
            参与助手 <span class="text-[#EC483E]">*</span>
          </label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="candidate in props.participantCandidates"
              :key="candidate.id"
              type="button"
              :data-testid="`group-template-participant-${candidate.id}`"
              class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-[12px] transition-all"
              :class="groupParticipants.includes(candidate.id)
                ? 'border-[#726FFF] bg-[#F3F1FF] text-[#5E5AE8]'
                : 'border-[#E5E7EB] bg-white text-black/64 hover:border-[#D5D9E5]'"
              @click="toggleGroupParticipant(candidate.id)"
            >
              <span class="inline-flex h-5 w-5 items-center justify-center rounded-full bg-[#F5F7FF] text-[10px] font-semibold text-black/58">
                {{ candidate.badge }}
              </span>
              <span>{{ candidate.name }}</span>
            </button>
          </div>
          <div class="text-[10px] leading-4 text-black/36">
            主 Agent 为系统通用协调器，不在此处配置。
          </div>
        </div>

        <div class="space-y-1.5">
          <label class="flex items-center gap-1.5 text-[12px] font-medium text-black/76">
            <Zap class="h-3.5 w-3.5 text-[#F59E0B]" />
            {{ isGroupTemplate ? '适用场景' : '能力描述' }}
          </label>
          <textarea
            v-model="capabilities"
            rows="2"
            class="w-full resize-none rounded-[16px] border-0 bg-[var(--ai-surface-soft)] px-3 py-2.5 text-[13px] leading-6 text-black/76 shadow-[inset_0_0_0_1px_rgba(215,224,239,0.9)] outline-none transition-all placeholder:text-black/28 focus:ring-4 focus:ring-[var(--color-primary)]/8"
            :placeholder="isGroupTemplate ? '例如：跨财务与代码评审的联调协作。' : '描述助手具备的核心能力…'"
          />
        </div>

        <div v-if="!isGroupTemplate" class="space-y-2">
          <div class="flex items-center justify-between gap-3">
            <label class="flex items-center gap-1.5 text-[12px] font-medium text-black/76">
              <Wrench class="h-3.5 w-3.5 text-black/46" />
              连接的 Skills
            </label>
            <span class="text-[11px] text-black/38">{{ skillSummary }}</span>
          </div>

          <div class="relative">
            <Search class="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-black/28" />
            <Input
              v-model="skillSearch"
              data-testid="assistant-skill-search-input"
              class="h-9 rounded-[14px] border-0 bg-[var(--ai-surface-soft)] pl-9 text-[12px] shadow-[inset_0_0_0_1px_rgba(215,224,239,0.84)]"
              placeholder="搜索技能，例如：RPA、数据、审批"
            />
          </div>

          <ScrollArea
            data-testid="new-assistant-skills-region"
            class="max-h-[182px] rounded-[18px] bg-[var(--ai-surface-soft)] p-2.5 shadow-[inset_0_0_0_1px_rgba(228,234,245,0.92)]"
            viewport-class="pr-1"
          >
            <div class="space-y-3">
              <div
                v-for="group in visibleSkillGroups"
                :key="group.id"
                class="space-y-2"
              >
                <div class="px-1 text-[10px] font-medium tracking-[0.08em] text-black/34">{{ group.label }}</div>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="skill in group.skills"
                    :key="skill.id"
                    :data-testid="`new-assistant-skill-${skill.label}`"
                    type="button"
                    :class="skills.includes(skill.label)
                      ? 'border-[var(--color-primary)] bg-[linear-gradient(135deg,#726FFF,#5D59FF)] text-white shadow-[0_8px_18px_rgba(114,111,255,0.16)]'
                      : 'border-[var(--ai-line)] bg-white text-black/58 hover:border-[var(--color-primary)]/30 hover:bg-[#FAFAFF]'"
                    class="rounded-[12px] border px-3 py-1.5 text-[11px] font-medium transition-all"
                    :title="skill.description"
                    @click="toggleSkill(skill.label)"
                  >
                    {{ skill.label }}
                  </button>
                </div>
              </div>
            </div>
          </ScrollArea>
        </div>
      </div>
    </div>

    <ModalActionBar
      test-id="assistant"
      :submit-label="submitLabel"
      :submit-disabled="!canSubmit"
      @cancel="emit('close')"
      @submit="handleSubmit"
    />
  </ModalShell>
</template>
