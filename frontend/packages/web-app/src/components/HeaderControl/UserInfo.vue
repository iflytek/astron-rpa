<script setup lang="ts">
import { Dropdown } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed } from 'vue'

import { getTermianlStatus, startSchedulingMode } from '@/api/engine'
import { sendTenantId } from '@/api/login/login'
import { taskNotify } from '@/api/task'
import authService from '@/auth/index'
import GlobalModal from '@/components/GlobalModal/index.ts'
import { DESIGNER } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import { utilsManager, windowManager } from '@/platform'
import { useAppModeStore } from '@/stores/useAppModeStore'
import { useRunningStore } from '@/stores/useRunningStore'
import { useUserStore } from '@/stores/useUserStore'

const { t } = useTranslation()
const { userNameState } = useUserStore()
const runningStore = useRunningStore()

const auth = authService.getAuth()

const menuData = computed(() => [
  // {
  //   key: 'userRight',
  //   icon: 'rights',
  //   label: t('userInfo.userRight'),
  // },
  // UAP 暂时隐藏租户空间
  // {
  //   key: 'changeTenant',
  //   icon: () => h(TeamOutlined),
  //   title: t('changeSpace'),
  //   label: t('changeSpace'),
  //   children: [],
  // },
  // {
  //   key: 'changeMode',
  //   icon: 'rights',
  //   label: t('changeMode'),
  // },
  {
    key: 'logout',
    icon: 'logout',
    label: t('logout'),
  },
])

async function menuClick(item: any) {
  const { data: { running } } = await getTermianlStatus()
  if (running) {
    modalTip()
    return
  }
  if (item.key === 'logout') {
    await logout()
  }
  if (item.keyPath[0] === 'changeTenant') {
    // 回传租户Id后重新跳转到首页
    await sendTenantId({ tenantId: item.key })
    taskNotify({ event: 'switch' })
    useRoutePush({ name: DESIGNER })
  }
  if (item.keyPath[0] === 'changeMode') {
    GlobalModal.confirm({
      title: '开始调度模式',
      content: '开启后本机画面和应用执行情况会被卓越中心监控，同时接受卓越中心下发的任务',
      okText: '确定',
      cancelText: '取消',
      onOk: () => {
        console.log('enter_scheduling_mode')
        startSchedulingMode() // 通知引擎用户确定切换为调度模式
        useAppModeStore().setAppMode('scheduling') // 设置为调度模式
        windowManager.hideWindow() // 隐藏主界面
        utilsManager.invoke('tray_change', { mode: 'scheduling', status: 'idle' }) // 改变托盘菜单
      },
    })
  }
}

async function logout() {
  taskNotify({ event: 'exit' }) // 不阻塞
  auth.logout()
}
 
function modalTip() {
  const modal = GlobalModal.confirm({
    title: '警告',
    content: '当前有应用/计划任务正在执行，是否立即停止',
    okText: '确定',
    cancelText: '取消',
    onOk() {
      console.log('User acknowledged the message')
      modal.destroy()
      runningStore.stop(runningStore.getRunProjectId())
    },
  })
}
</script>

<template>
  <Dropdown placement="bottom" :trigger="['click']">
    <span class="flex items-center justify-center w-full h-full">
      <rpa-icon name="user-circle" style="outline: none;" />
    </span>
    <template #overlay>
      <a-menu class="!bg-[#f6f8ff] dark:!bg-[#141414] w-[200px] rounded-[16px]  !px-[8px] !py-[16px]" @click="menuClick">
        <div class="flex items-center mb-[12px]">
          <div class="w-[48px] h-[48px] bg-primary rounded-[50%] ml-[8px] mr-[12px] flex items-center justify-center p-[8px]">
            <rpa-icon name="robot" class="w-[32px] h-[32px] text-[#fff]" />
          </div>
          <div class="flex flex-col">
            <span class="font-semibold">{{ t('userInfo.userName') }}</span>
            <span class="text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)]">{{ userNameState.state }}</span>
          </div>
        </div>
        <a-menu-item v-for="item in menuData" :key="item.key">
          <template #icon>
            <rpa-icon :name="item.icon" class="w-[16px] h-[16px] text-[rgba(0,0,0)] dark:text-[rgba(255,255,255)]" />
          </template>
          <div class="h-[34px] leading-[34px] text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)] truncate">
            {{ item.label }}
          </div>
        </a-menu-item>
      </a-menu>
    </template>
  </Dropdown>
</template>

<style lang="scss" scoped>
:deep(.ant-dropdown-menu) {
  background: red;
}
</style>
