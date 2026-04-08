<script setup lang="ts">
import { useIntervalFn } from '@vueuse/core'
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'

import BackendReaction from '@/components/BackendReaction/Index.vue'
import ConfigProvider from '@/components/ConfigProvider/index.vue'
import GlobalRegister from '@/components/GlobalRegister/Index.vue'
import Loading from '@/components/Loading.vue'
import MacPermissionDialog from '@/components/MacPermissionDialog/index.vue'
import BUS from '@/utils/eventBus'
import { useAppConfigStore } from '@/stores/useAppConfig'

const appStore = useAppConfigStore()

useIntervalFn(() => appStore.checkUpdate(), 60 * 60 * 1000)

onMounted(() => {
  appStore.checkUpdate()
  const raw = sessionStorage.getItem('mac_permission')
  if (raw) {
    sessionStorage.removeItem('mac_permission')
    BUS.$emit('mac-permission-check', JSON.parse(raw))
  }
})
</script>

<template>
  <ConfigProvider>
    <BackendReaction />
    <RouterView />
    <Loading />
    <GlobalRegister />
    <MacPermissionDialog />
  </ConfigProvider>
</template>
