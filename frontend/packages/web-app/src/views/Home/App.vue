<script setup lang="ts">
import { useIntervalFn } from '@vueuse/core'
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'

import BackendReaction from '@/components/BackendReaction/Index.vue'
import ConfigProvider from '@/components/ConfigProvider/index.vue'
import GlobalRegister from '@/components/GlobalRegister/Index.vue'
import Loading from '@/components/Loading.vue'
import { useAppConfigStore } from '@/stores/useAppConfig'

const appStore = useAppConfigStore()

// 每小时检查一次更新
useIntervalFn(() => appStore.checkUpdate(), 60 * 60 * 1000)

onMounted(() => appStore.checkUpdate())
</script>

<template>
  <ConfigProvider>
    <BackendReaction />
    <RouterView />
    <Loading />
    <GlobalRegister />
  </ConfigProvider>
</template>
