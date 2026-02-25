<script setup lang="ts">
import { Auth } from '@rpa/components/auth'
import { Dropdown, Checkbox, Button } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { storeToRefs } from 'pinia'
import { computed, h } from 'vue'

import { getTermianlStatus, startSchedulingMode } from '@/api/engine'
import { taskNotify } from '@/api/task'
import GlobalModal from '@/components/GlobalModal/index.ts'
import { utilsManager, windowManager } from '@/platform'
import { useAppConfigStore } from '@/stores/useAppConfig'
import { useAppModeStore } from '@/stores/useAppModeStore'
import { useRunningStore } from '@/stores/useRunningStore'
import { useUserStore } from '@/stores/useUserStore'

const { t } = useTranslation()
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
      key: 'logout',
      icon: 'logout',
      label: t('logout'),
    }
  ].filter(item => !item.hidden || !item.hidden())
})

async function menuClick(item: any) {
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
      title: '开始调度模式',
      content: '开启后当前客户端会自动接收控制台下发的远程任务，对应任务执行情况会被控制台监控，请确认。',
      footer: h('div', { class: 'flex items-center justify-between w-full pl-[30px] mt-[30px]' }, [
        userStore.currentTenant?.tenantType === 'enterprise' 
          ? h(Checkbox, {
            defaultChecked: false,
            onChange: (e: any) => {
              startWatch = e.target.checked
            },
          }, {
            default: () => '开启桌面监控'
          })
          : h('div'),
        h('div', { class: 'flex gap-[10px]' }, [
          h(Button, {
            onClick: () => {
              modal.destroy()
            }
          }, {
            default: () => '取消'
          }),
          h(Button, {
            type: 'primary',
            onClick: () => {
              startSchedulingMode({ start_watch: startWatch }) // 通知引擎用户确定切换为调度模式
              useAppModeStore().setAppMode('scheduling') // 设置为调度模式
              windowManager.hideWindow() // 隐藏主界面
              utilsManager.invoke('tray_change', { mode: 'scheduling', status: 'idle' }) // 改变托盘菜单
              modal.destroy()
            }
          }, {
            default: () => '确定'
          })
        ])
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
        <Auth.Consult
          v-if="userStore.currentTenant?.tenantType !== 'enterprise'"
          :auth-type="appInfo.appAuthType"
          trigger="button"
          :button-conf="{ buttonType: 'tag', currentEdition: userStore.currentTenant?.tenantType, expirationDate: userStore.currentTenant?.expirationDate, shouldAlert: userStore.currentTenant?.shouldAlert }"
          custom-class="upgrade-btn"
          :consult="{
            consultType: userStore.currentTenant?.expirationDate ? 'renewal' : 'consult',
            consultEdition: userStore.currentTenant?.tenantType as 'professional' | 'enterprise',
          }"
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
