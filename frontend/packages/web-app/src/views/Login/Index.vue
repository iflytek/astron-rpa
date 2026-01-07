<script setup lang="ts">
import { onMounted } from 'vue'

import Header from '@/components/Header.vue'
import { windowManager } from '@/platform'

onMounted(() => {
  windowManager.restoreLoginWindow()
})
</script>

<template>
  <div class="login-container bg-no-repeat bg-cover padT60">
    <Header :maximize="false" />
  </div>
</template>

<style lang="scss">
</style>
