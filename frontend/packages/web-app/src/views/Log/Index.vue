<script lang="ts" setup>
import LogWindow from '@/components/LogWindow/Index.vue'
import ConfigProvider from '@/components/ConfigProvider/index.vue'
</script>

<template>
  <ConfigProvider>
    <LogWindow />
  </ConfigProvider>
</template>

<style lang="scss">
#app-log {
  width: 100vw;
  height: 100vh;
}
html,
body {
  margin: 0;
  padding: 0;
}
</style>
