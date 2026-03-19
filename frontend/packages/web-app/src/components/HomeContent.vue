<script setup lang="ts">
import { Auth } from '@rpa/components/auth'
import { storeToRefs } from 'pinia'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import MarketSiderMenu from '@/components/MarketSiderMenu.vue'
import SiderMenu from '@/components/SiderMenu.vue'
import { COMMON_SIDER_WIDTH } from '@/constants'
import { AIASSISTANT, APPLICATIONMARKET } from '@/constants/menu'
import { useAppConfigStore } from '@/stores/useAppConfig'
import { useUserStore } from '@/stores/useUserStore'

const appStore = useAppConfigStore()
const userStore = useUserStore()
const route = useRoute()
const { appInfo } = storeToRefs(appStore)

const isMarket = computed(() => {
  return route.matched[0].name === APPLICATIONMARKET
})

const showSider = computed(() => {
  return route.matched[0].name !== AIASSISTANT
})
</script>

<template>
  <div class="flex h-full min-h-0">
    <MarketSiderMenu v-if="showSider && isMarket" />
    <SiderMenu v-else-if="showSider" />
    <div v-if="showSider" class="absolute bottom-[20px] left-0" :style="{ width: `${COMMON_SIDER_WIDTH}px` }">
      <Auth.TenantDropdown :auth-type="appInfo.appAuthType" :before-switch="userStore.beforeSwitch" @switch-tenant="userStore.switchTenant" />
    </div>
    <div class="flex-1 relative h-full min-h-0">
      <router-view />
    </div>
  </div>
</template>

<style lang="scss" scoped>
:deep(.ant-menu-light.ant-menu-root.ant-menu-inline) {
  border-inline-end: none;
}
</style>
