<script setup lang="ts">
import { baseUrl } from '@/utils/env'
import { WINDOW_NAME } from '@/constants'
import { windowManager, type CreateWindowOptions } from '@/platform'

import { useFormStore } from "./hooks/useFormStore";

const { atom } = useFormStore();

const handleAIDebug = async () => {
  // 从输入参数中挑出 key 为 instruction 的参数
  const instruction = atom.value?.inputList?.find((item) => item.key === 'instruction')?.value[0]?.value || ''
  const options: CreateWindowOptions = {
    url: `${baseUrl}/${WINDOW_NAME.CUA}.html?message=${encodeURIComponent(instruction)}`,
    title: WINDOW_NAME.CUA,
    label: WINDOW_NAME.CUA,
    alwaysOnTop: true,
    fullscreen: true,
    decorations: false,
    transparent: true,
  }

  await windowManager.createWindow(options, () => {
    windowManager.showWindow()
  })

  windowManager.hideWindow()
}
</script>

<template>
  <div class="flex" v-if="atom.debugButton">
    <a-button @click="handleAIDebug" v-if="atom.debugButton === 'ai_debug'">
      运行调试
    </a-button>
  </div>
</template>
