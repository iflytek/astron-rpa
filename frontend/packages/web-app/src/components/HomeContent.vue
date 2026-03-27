<script setup lang="ts">
import { Auth } from '@rpa/components/auth'
import { storeToRefs } from 'pinia'
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { DEFAULT_AI_STUDIO_SESSION_ID } from '@/views/AIStudio/contracts'
import AIStudioSidebar from '@/views/AIStudio/components/AssistantSidebar.vue'

import MarketSiderMenu from '@/components/MarketSiderMenu.vue'
import SiderMenu from '@/components/SiderMenu.vue'
import { COMMON_SIDER_WIDTH } from '@/constants'
import { AIASSISTANT, APPLICATIONMARKET } from '@/constants/menu'
import { useAppConfigStore } from '@/stores/useAppConfig'
import { useAIStudioStore } from '@/stores/useAIStudioStore'
import { useUserStore } from '@/stores/useUserStore'

const appStore = useAppConfigStore()
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const { appInfo } = storeToRefs(appStore)
const aiStudioStore = useAIStudioStore()
const { assistantGroups } = storeToRefs(aiStudioStore)

const isMarket = computed(() => route.matched[0].name === APPLICATIONMARKET)
const isAIStudio = computed(() => route.matched[0].name === AIASSISTANT)
const routeDefaultSessionId = typeof window !== 'undefined' && 'opencodeApi' in window ? '' : DEFAULT_AI_STUDIO_SESSION_ID
const activeSessionId = computed(() => String(route.query.sessionId || routeDefaultSessionId))

async function handleSelectSession(_assistantId: string, sessionId: string) {
  aiStudioStore.openSurface('main')
  await aiStudioStore.setActiveSession(sessionId)
  await router.replace({
    query: {
      ...route.query,
      sessionId,
    },
  })
}

async function handleDeleteSession(assistantId: string, sessionId: string) {
  aiStudioStore.openSurface('main')
  const nextSessionId = await aiStudioStore.deleteSession(assistantId, sessionId)
  if (nextSessionId) {
    await router.replace({
      query: {
        ...route.query,
        sessionId: nextSessionId,
      },
    })
  }
}

async function handleDeleteAssistant(assistantId: string) {
  aiStudioStore.openSurface('main')
  const nextSessionId = await aiStudioStore.deleteAssistant(assistantId)
  if (nextSessionId) {
    await router.replace({
      query: {
        ...route.query,
        sessionId: nextSessionId,
      },
    })
  }
}

function handleOpenNewSession(assistantId: string) {
  aiStudioStore.openNewSession(assistantId)
}

watch(
  [isAIStudio, activeSessionId],
  ([visible, sessionId]) => {
    if (visible)
      void aiStudioStore.ensureInitialized(sessionId)
  },
  { immediate: true },
)
</script>

<template>
  <div class="flex h-full min-h-0" :class="isAIStudio ? 'bg-[#F6F8FF]' : ''">
    <MarketSiderMenu v-if="isMarket" />
    <AIStudioSidebar
      v-else-if="isAIStudio"
      :groups="assistantGroups"
      :active-session-id="activeSessionId"
      :active-surface="aiStudioStore.activeSurface"
      @select-session="handleSelectSession"
      @open-edit-assistant="aiStudioStore.openEditAssistant($event)"
      @open-new-group-template="aiStudioStore.openNewGroupTemplate()"
      @open-new-session="handleOpenNewSession"
      @delete-assistant="handleDeleteAssistant"
      @delete-session="handleDeleteSession"
      @open-new-assistant="aiStudioStore.openNewAssistant()"
      @open-automation="aiStudioStore.openSurface('automation')"
      @open-settings="aiStudioStore.openSurface('settings')"
    />
    <SiderMenu v-else />

    <div
      v-if="!isAIStudio"
      class="absolute bottom-[20px] left-0"
      :style="{ width: `${COMMON_SIDER_WIDTH}px` }"
    >
      <Auth.TenantDropdown :auth-type="appInfo.appAuthType" :before-switch="userStore.beforeSwitch" @switch-tenant="userStore.switchTenant" />
    </div>

    <div class="relative flex-1 min-h-0" :class="isAIStudio ? 'min-h-0 pb-3 pr-3 pt-3' : ''">
      <div
        :data-testid="isAIStudio ? 'ai-studio-shell' : undefined"
        class="h-full"
        :class="isAIStudio
          ? 'overflow-hidden rounded-[24px] bg-[rgba(255,255,255,0.28)] shadow-[0_20px_48px_rgba(15,23,42,0.03)]'
          : ''"
      >
        <router-view />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
:deep(.ant-menu-light.ant-menu-root.ant-menu-inline) {
  border-inline-end: none;
}
</style>
