<script setup lang="ts">
import { Auth } from '@rpa/components/auth'
import { storeToRefs } from 'pinia'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import MarketSiderMenu from '@/components/MarketSiderMenu.vue'
import SiderMenu from '@/components/SiderMenu.vue'
import { COMMON_SIDER_WIDTH } from '@/constants'
import { APPLICATIONMARKET } from '@/constants/menu'
import { useAppConfigStore } from '@/stores/useAppConfig'
import { useUserStore } from '@/stores/useUserStore'

const appStore = useAppConfigStore()
const userStore = useUserStore()
const route = useRoute()
const { appInfo } = storeToRefs(appStore)

const isMarket = computed(() => {
  return route.matched[0].name === APPLICATIONMARKET
})
</script>

<template>
  <div class="flex">
    <MarketSiderMenu v-if="isMarket" />
    <SiderMenu v-else />
    <div class="absolute bottom-[20px] left-0" :style="{ width: `${COMMON_SIDER_WIDTH}px` }">
      <Auth.TenantDropdown :auth-type="appInfo.appAuthType" :before-switch="userStore.beforeSwitch" @switch-tenant="userStore.switchTenant" />
    </div>
    <div class="flex-1 relative">
      <router-view />
    </div>
  </div>
</template>

<style lang="scss" scoped>
:deep(.ant-menu-light.ant-menu-root.ant-menu-inline) {
  border-inline-end: none;
}
</style>
