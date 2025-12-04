<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import MarketSiderMenu from '@/components/MarketSiderMenu.vue'
import SiderMenu from '@/components/SiderMenu.vue'
import { APPLICATIONMARKET, DESIGNER } from '@/constants/menu'
import { Auth, TenantItem } from '@rpa/components/auth'
import { useTenantStore } from '@/stores/useTenantStore'
import router from '@/router'
import GlobalModal from '@/components/GlobalModal/index.ts'
import { useRoutePush } from '@/hooks/useCommonRoute'
import { useRunningStore } from '@/stores/useRunningStore'
import { getTermianlStatus } from '@/api/engine'
import { taskNotify } from '@/api/task'
import { COMMON_SIDER_WIDTH } from '@/constants'

const route = useRoute()
 
const isMarket = computed(() => {
  return route.matched[0].name === APPLICATIONMARKET
})

const handleToggleTenant = (tenant: TenantItem) => {
  useTenantStore().setCurrentTenant(tenant)
  if(router.currentRoute.value.name !== DESIGNER) {
    useRoutePush({ name: DESIGNER })
  }
  // 切换租户后通知任务更新
  taskNotify({ event: 'login' })
}

const beforeSwitch = async (): Promise<void> => {
  const { data } = await getTermianlStatus()
  if (!data.running) {
    return Promise.resolve()
  }

  return new Promise<void>((resolve, reject) => {
    const modal = GlobalModal.confirm({
      title: '警告',
      content: '切换工作空间将中断正在运行的应用，请确认？',
      okText: '确定',
      cancelText: '取消',
      maskClosable: false,
      onOk: async () => {
        const runningStore = useRunningStore()
        runningStore.stop(runningStore.getRunProjectId())
        modal.destroy()
        resolve()
      },
      onCancel: () => {
        modal.destroy()
        reject(new Error('用户取消切换'))
      },
    })
  })
}
</script>

<template>
  <div class="home-content flex h-full">
    <MarketSiderMenu v-if="isMarket" />
    <SiderMenu v-else />
    <div class="fixed bottom-[20px] left-0" :style="{ width: `${COMMON_SIDER_WIDTH}px` }">
      <Auth.TenantDropdown :before-switch="beforeSwitch" @switch-tenant="handleToggleTenant"/>
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

.home-content {
  padding-top: var(--headerHeight);
}
</style>
