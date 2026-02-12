<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import { taskNotify } from '@/api/task'
import Header from '@/components/Header.vue'
import HeaderControl from '@/components/HeaderControl/HeaderControl.vue'
import HeaderMenu from '@/components/HeaderMenu.vue'
import Content from '@/components/HomeContent.vue'
import { windowManager } from '@/platform'

import type { Illustration } from './components/BgIllustration.vue'
import BgIllustration from './components/BgIllustration.vue'
import { useHome } from './hooks/useHome'

const route = useRoute()

// 调整窗口铺满屏幕
async function windowResize() {
  const isMaximized = await windowManager.isMaximized()
  if (!isMaximized) {
    await windowManager.maximizeWindow()
  }
}

useHome()

onMounted(() => {
  windowResize()

  // lazy load Arrange view for better performance
  const importArrange = () => import('@/views/Arrange/index.vue')
  window.addEventListener('load', () => {
    if ('requestIdleCallback' in window) {
      window.requestIdleCallback(() => importArrange())
    }
    else {
      setTimeout(() => importArrange(), 0)
    }
  })
})

const illustration = computed<Illustration | undefined>(() => {
  return route.meta?.illustration as Illustration
})

taskNotify({ event: 'login' })
</script>

<template>
  <BgIllustration v-if="illustration" :illustration="illustration" />

  <div class="w-full h-full flex flex-col bg-[#f6f8ff] dark:bg-[#141414]">
    <Header>
      <template #headMenu>
        <HeaderMenu />
      </template>
      <template #headControl>
        <HeaderControl />
      </template>
    </Header>
    <Content class="flex-1" />
  </div>
</template>
