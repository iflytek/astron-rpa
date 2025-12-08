<script setup lang="ts">
import { ConfigProvider } from '@rpa/components/config-provider'
</script>

<template>
  <ConfigProvider>
    <router-view />
  </ConfigProvider>
</template>
