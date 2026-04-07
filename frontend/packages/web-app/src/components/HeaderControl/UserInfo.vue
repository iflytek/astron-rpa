<script setup lang="ts">
import { ConsultUpgradeTrigger } from '@rpa/components/auth'
import { NiceModal } from '@rpa/components'
import { Button, Checkbox, Dropdown } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { storeToRefs } from 'pinia'
import { computed, h, inject } from 'vue'

import { getTermianlStatus, startSchedulingMode } from '@/api/engine'
import { taskNotify } from '@/api/task'
import GlobalModal from '@/components/GlobalModal/index.ts'
import { PointsModal } from '@/components/PointsModal'
import { utilsManager, windowManager } from '@/platform'
import { useAppConfigStore } from '@/stores/useAppConfig'
import { useRunningStore } from '@/stores/useRunningStore'
import { useUserStore } from '@/stores/useUserStore'

import { OPEN_HEADER_UPGRADE_CONSULT_KEY } from './headerUpgradeConsult'

const { t } = useTranslation()

const openHeaderUpgradeConsult = inject(OPEN_HEADER_UPGRADE_CONSULT_KEY, () => {})
const runningStore = useRunningStore()
const userStore = useUserStore()
const appStore = useAppConfigStore()
const { appInfo } = storeToRefs(appStore)

const menuData = computed(() => {
  return [
    // {
    //   key: 'userRight',
    //   icon: 'rights',
    //   label: t('userInfo.userRight'),
    // },
    {
      key: 'changeMode',
      icon: 'rights',
      label: t('changeMode'),
      hidden: () => userStore.currentTenant?.tenantType === 'personal',
    },
    {
      key: 'pointsManage',
      icon: 'ai',
      label: t('userInfo.pointsManage'),
    },
    {
      key: 'logout',
      icon: 'logout',
      label: t('logout'),
    },
  ].filter(item => !item.hidden || !item.hidden())
})

async function menuClick(item: any) {
  if (item.key === 'pointsManage') {
    NiceModal.show(PointsModal, {
      workspaceName: userStore.currentTenant?.name,
    })
    return
  }
  const { data: { running } } = await getTermianlStatus()
  if (running) {
    modalTip()
    return
  }
  if (item.key === 'logout') {
    await logout()
  }
  if (item.keyPath[0] === 'changeMode') {
    let startWatch = false
    const modal = GlobalModal.confirm({
      title: t('userInfo.startSchedulingMode'),
      content: t('userInfo.schedulingModeDesc'),
      footer: h('div', { class: 'flex items-center justify-between w-full pl-[30px] mt-[30px]' }, [
        userStore.currentTenant?.tenantType === 'enterprise'
          ? h(Checkbox, {
              defaultChecked: false,
              onChange: (e: any) => {
                startWatch = e.target.checked
              },
            }, {
              default: () => t('common.enableDesktopMonitoring'),
            })
          : h('div'),
        h('div', { class: 'flex gap-[10px]' }, [
          h(Button, {
            onClick: () => {
              modal.destroy()
            },
          }, {
            default: () => t('cancel'),
          }),
          h(Button, {
            type: 'primary',
            onClick: () => {
              startSchedulingMode({ start_watch: startWatch }) // 通知引擎用户确定切换为调度模式
              useAppConfigStore().setAppMode('scheduling') // 设置为调度模式
              windowManager.hideWindow() // 隐藏主界面
              utilsManager.invoke('tray_change', { mode: 'scheduling', status: 'idle' }) // 改变托盘菜单
              modal.destroy()
            },
          }, {
            default: () => t('confirm'),
          }),
        ]),
      ]),
    })
  }
}

async function logout() {
  await userStore.logout()
  taskNotify({ event: 'exit' }) // 不阻塞
  location.replace(`/boot.html`)
}

function modalTip() {
  const modal = GlobalModal.confirm({
    title: t('common.warning'),
    content: t('common.stopRunningConfirm'),
    okText: t('confirm'),
    cancelText: t('cancel'),
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
      <a-menu class="!bg-[#f6f8ff] dark:!bg-[#141414] w-[256px] rounded-[16px]  !px-[8px] !py-[16px]" @click="menuClick">
        <div class="flex items-center mb-[12px]">
          <div class="w-[48px] h-[48px] bg-primary rounded-[50%] ml-[8px] mr-[12px] flex items-center justify-center p-[8px]">
            <rpa-icon name="robot" class="w-[32px] h-[32px] text-[#fff]" />
          </div>
          <div class="flex flex-col">
            <span class="font-semibold">{{ t('userInfo.userName') }}</span>
            <span class="text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)]">{{ userStore.currentUserInfo?.name || userStore.currentUserInfo?.loginName }}</span>
          </div>
        </div>
        <ConsultUpgradeTrigger
          v-if="userStore.currentTenant?.tenantType !== 'enterprise'"
          class="upgrade-btn"
          :auth-type="appInfo.appAuthType"
          :button-conf="{
            buttonType: 'tag',
            currentEdition: userStore.currentTenant?.tenantType,
            expirationDate: userStore.currentTenant?.expirationDate,
            shouldAlert: userStore.currentTenant?.shouldAlert,
          }"
          @open="openHeaderUpgradeConsult"
        />
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
