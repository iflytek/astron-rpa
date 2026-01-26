<script lang="ts" setup>
import { onMounted } from 'vue'
import { windowManager } from '@/platform'

import ConfigProvider from '@/components/ConfigProvider/index.vue'

import LogWindow from './LogWindow.vue'

onMounted(() => {
  // 在创建日志窗口时虽然已经设置了窗口置顶，但是依然有可能被其他窗口遮挡
  // 因此在挂载完成后再设置一遍窗口置顶
  windowManager.setWindowAlwaysOnTop(true)
})
</script>

<template>
  <ConfigProvider>
    <LogWindow />
  </ConfigProvider>
</template>

<style lang="scss">
#app {
  width: 100vw;
  height: 100vh;
}
html,
body {
  margin: 0;
  padding: 0;
}
</style>
