<script setup lang="ts">
import { onActivated, onMounted } from 'vue'

import { launchOpenClaw } from '@/api/openclaw-manager'
import Header from '@/components/Header.vue'
import HeaderControl from '@/components/HeaderControl/HeaderControl.vue'
import HeaderMenu from '@/components/HeaderMenu.vue'
import ChatPanel from '@/components/AstronAssistant/ChatPanel.vue'

let launchingPromise: Promise<void> | null = null

async function ensureOpenClawLaunched() {
  if (launchingPromise)
    return await launchingPromise

  launchingPromise = (async () => {
    try {
      await launchOpenClaw()
    }
    catch (error) {
      console.warn('Failed to auto launch OpenClaw:', error)
    }
    finally {
      launchingPromise = null
    }
  })()

  return await launchingPromise
}

onMounted(() => {
  void ensureOpenClawLaunched()
})

onActivated(() => {
  void ensureOpenClawLaunched()
})
</script>

<template>
  <div class="w-full h-full flex flex-col bg-[#f6f8ff] dark:bg-[#141414]">
    <Header>
      <template #headMenu>
        <HeaderMenu />
      </template>
      <template #headControl>
        <HeaderControl />
      </template>
    </Header>
    <div class="flex-1 min-h-0 p-4">
      <ChatPanel />
    </div>
  </div>
</template>
