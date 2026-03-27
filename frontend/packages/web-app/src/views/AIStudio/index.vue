<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed, onBeforeUnmount, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { DEFAULT_AI_STUDIO_SESSION_ID } from './contracts'
import AutomationTaskView from './components/AutomationTaskView.vue'
import ArtifactPanel from './components/ArtifactPanel.vue'
import InviteAssistantModal from './components/InviteAssistantModal.vue'
import NewAssistantModal from './components/NewAssistantModal.vue'
import NewSessionModal from './components/NewSessionModal.vue'
import SettingsCenterView from './components/SettingsCenterView.vue'
import StudioChatPane from './components/StudioChatPane.vue'
import DiffuseLight from '@/components/Illustration/DiffuseLight.vue'
import { useAIStudioStore } from '@/stores/useAIStudioStore'

const route = useRoute()
const router = useRouter()
const aiStudioStore = useAIStudioStore()
const routeDefaultSessionId = typeof window !== 'undefined' && 'opencodeApi' in window ? '' : DEFAULT_AI_STUDIO_SESSION_ID
const { activeSession, activeSurface, assistantModalMode, assistantTemplateKind, editingAssistant, invitedAssistants, isActiveSessionPending, isAiTyping, newSessionAssistant, newSessionParticipantCandidates, showInviteAssistant, showNewAssistant, showNewSession, workspaceOpen } = storeToRefs(aiStudioStore)
const groupTemplateParticipants = computed(() => {
  const assistant = newSessionAssistant.value
  if (!assistant || assistant.status !== '群聊')
    return []
  const candidateMap = new Map(newSessionParticipantCandidates.value.map(candidate => [candidate.id, candidate]))
  return (assistant.groupParticipantAssistantIds || []).map((id) => {
    const matched = candidateMap.get(id)
    if (matched)
      return matched
    return {
      id,
      name: id,
      badge: id.slice(0, 1).toUpperCase(),
    }
  })
})

const activeSessionId = computed(() => String(route.query.sessionId || routeDefaultSessionId))

watch(
  activeSessionId,
  (sessionId) => {
    void aiStudioStore.ensureInitialized(sessionId)
  },
  { immediate: true },
)

onMounted(() => {
  document.body.classList.add('ai-assistant-preview')
})

onBeforeUnmount(() => {
  document.body.classList.remove('ai-assistant-preview')
})

function handleCloseSurface() {
  aiStudioStore.openSurface('main')
}

async function handleAssistantSubmit(payload: {
  name: string
  persona: string
  capabilities: string
  skills: string[]
  templateKind: 'assistant' | 'group'
  groupParticipantAssistantIds?: string[]
  groupCollaborationMode?: 'auto' | 'pipeline' | 'race' | 'debate'
}) {
  if (assistantModalMode.value === 'edit' && editingAssistant.value) {
    await aiStudioStore.updateAssistant(editingAssistant.value.id, payload)
    return
  }

  await aiStudioStore.createAssistant(payload)
}

async function handleCreateSession(payload: {
  workspacePath: string
  sessionTitle?: string
}) {
  const sessionId = await aiStudioStore.createSession(payload)
  if (!sessionId)
    return
  void router.replace({
    query: {
      ...route.query,
      sessionId,
    },
  })
}
</script>

<template>
  <div
    class="relative h-full overflow-hidden bg-[#F6F8FF]"
    style="font-family: var(--font-sans-ui);"
  >
    <DiffuseLight height="100%" class="pointer-events-none absolute right-0 top-0 h-full w-full opacity-[0.32]" />
    <div class="pointer-events-none absolute inset-x-0 top-0 h-[240px] bg-[radial-gradient(circle_at_32%_0%,rgba(114,111,255,0.10),transparent_42%),linear-gradient(180deg,rgba(255,255,255,0.54)_0%,rgba(255,255,255,0)_100%)]" />
    <div class="pointer-events-none absolute bottom-0 left-[12%] h-[240px] w-[240px] rounded-full bg-[radial-gradient(circle,rgba(114,111,255,0.08)_0%,rgba(114,111,255,0)_72%)] blur-2xl" />

    <div
      v-if="activeSession"
      class="relative z-10 flex h-full min-h-0 min-w-0 bg-[linear-gradient(180deg,rgba(255,255,255,0.44)_0%,rgba(255,255,255,0.14)_100%)]"
    >
      <template v-if="activeSurface === 'main'">
        <StudioChatPane
          :invited-assistants="invitedAssistants"
          :session="activeSession"
          :session-pending="isActiveSessionPending"
          :is-ai-typing="isAiTyping"
          :workspace-open="workspaceOpen"
          :is-action-pending="aiStudioStore.isActionPending"
          :is-card-pending="aiStudioStore.isCardPending"
          @open-invite="aiStudioStore.openInviteAssistant()"
          @send-message="aiStudioStore.sendMessage($event)"
          @submit-action="aiStudioStore.submitCardAction($event)"
          @submit-choice="aiStudioStore.submitChoiceForm($event)"
          @submit-param="aiStudioStore.submitParamForm($event)"
          @toggle-workspace="aiStudioStore.toggleWorkspace()"
        />
        <ArtifactPanel
          v-if="workspaceOpen"
          :session="activeSession"
          @close="aiStudioStore.setWorkspaceOpen(false)"
          @select-artifact="aiStudioStore.selectArtifact"
        />
      </template>
      <template v-else-if="activeSurface === 'automation'">
        <AutomationTaskView @close="handleCloseSurface" />
      </template>
      <template v-else>
        <StudioChatPane
          :invited-assistants="invitedAssistants"
          :session="activeSession"
          :session-pending="isActiveSessionPending"
          :workspace-open="workspaceOpen"
          :is-action-pending="aiStudioStore.isActionPending"
          :is-card-pending="aiStudioStore.isCardPending"
          class="pointer-events-none opacity-30 blur-[1px]"
        />
        <SettingsCenterView @close="handleCloseSurface" />
      </template>
    </div>
    <div
      v-else
      class="flex h-full items-center justify-center text-sm text-black/42"
    >
      AI 助手页面正在初始化...
    </div>

    <NewAssistantModal
      v-if="showNewAssistant"
      :mode="assistantModalMode"
      :template-kind="assistantTemplateKind"
      :assistant="editingAssistant"
      :participant-candidates="newSessionParticipantCandidates"
      @close="aiStudioStore.closeNewAssistant()"
      @submit="handleAssistantSubmit"
    />
    <NewSessionModal
      v-if="showNewSession && newSessionAssistant"
      :assistant-name="newSessionAssistant.name"
      :default-workspace-path="newSessionAssistant.workspacePath"
      :is-group-session="newSessionAssistant.status === '群聊'"
      :group-template-participants="groupTemplateParticipants"
      :group-template-mode="newSessionAssistant.groupCollaborationMode"
      @close="aiStudioStore.closeNewSession()"
      @submit="handleCreateSession"
    />
    <InviteAssistantModal
      v-if="showInviteAssistant"
      @close="aiStudioStore.closeInviteAssistant()"
      @submit="aiStudioStore.inviteAssistants"
    />
  </div>
</template>

<style scoped>
:global(body.ai-assistant-preview .ant-message) {
  display: none !important;
}

:global(body.ai-assistant-preview) {
  --ai-font-caption: calc(var(--font-size-sm) * 1px);
  --ai-font-body: calc(var(--font-size) * 1px);
  --ai-font-label: calc(var(--font-size) * 1px);
  --ai-font-title: calc(var(--font-size-heading5) * 1px);
  --ai-font-page-title: 18px;
  --ai-leading-caption: var(--line-height-sm);
  --ai-leading-body: var(--line-height);
  --ai-leading-title: var(--line-height-heading5);
  --ai-leading-page-title: 1.35;
  --ai-line-soft: #edf1f8;
  --ai-line: #e4eaf5;
  --ai-line-strong: #d7e0ef;
  --ai-surface-soft: #f7f9fd;
  --ai-surface-soft-2: #f3f6fb;
}
</style>
