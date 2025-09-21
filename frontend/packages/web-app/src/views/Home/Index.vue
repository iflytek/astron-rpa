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
  windowManager.isMaximized().then(async (isMaximized) => {
    if (!isMaximized) {
      await windowManager.setWindowSize()
      await windowManager.maximizeWindow()
    }
  })
}

useHome()

onMounted(() => windowResize())

const illustration = computed<Illustration | undefined>(() => {
  return route.meta?.illustration as Illustration
})

taskNotify({ event: 'login' })
</script>

<template>
  <BgIllustration v-if="illustration" :illustration="illustration" />

  <div class="w-full h-full bg-[#f6f8ff] dark:bg-[#141414]">
    <Header>
      <template #headMenu>
        <HeaderMenu />
      </template>
      <template #headControl>
        <HeaderControl />
      </template>
    </Header>
    <Content />
  </div>
</template>
