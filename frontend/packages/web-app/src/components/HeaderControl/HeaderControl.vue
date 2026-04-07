<script setup lang="ts">
import { Auth } from '@rpa/components/auth'
import { NiceModal } from '@rpa/components'
import { Tooltip } from 'ant-design-vue'
import { storeToRefs } from 'pinia'
import { provide, ref } from 'vue'

import { SettingCenterModal } from '@/components/SettingCenterModal'
import { utilsManager } from '@/platform'
import { useAppConfigStore } from '@/stores/useAppConfig'
import { usePermissionStore } from '@/stores/usePermissionStore'
import useUserSettingStore from '@/stores/useUserSetting.ts'
import { useUserStore } from '@/stores/useUserStore'

import MessageTip from '../MesssageTip/Index.vue'

import ControlButton from './ControlButton.vue'
import Help from './Help.vue'
import { OPEN_HEADER_UPGRADE_CONSULT_KEY } from './headerUpgradeConsult'
import Points from './Points.vue'
import Updater from './Updater.vue'
import UserInfo from './UserInfo.vue'

interface HeaderControlProps {
  setting?: boolean
  control?: boolean
  message?: boolean
  userInfo?: boolean
}

// 控制按钮显示
const props = withDefaults(defineProps<HeaderControlProps>(), ({
  setting: true,
  control: true,
  message: true,
  userInfo: true,
}))

useUserSettingStore()

const appStore = useAppConfigStore()
const userStore = useUserStore()
const permissionStore = usePermissionStore()
const { appInfo } = storeToRefs(appStore)

/** 与 UserInfo、积分弹层共用同一套开通/续费咨询弹窗 */
const headerUpgradeConsultRef = ref<InstanceType<typeof Auth.Consult> | null>(null)

function openHeaderUpgradeConsult() {
  headerUpgradeConsultRef.value?.openModal()
}

provide(OPEN_HEADER_UPGRADE_CONSULT_KEY, openHeaderUpgradeConsult)

function handleOpenSetting() {
  NiceModal.show(SettingCenterModal)
}

function handleToControl() {
  utilsManager.openInBrowser(`${appInfo.value.remotePath}admin/`)
}
</script>

<template>
  <Updater />

  <Points />

  <Help />

  <Tooltip v-if="props.setting" :title="$t('setting')">
    <ControlButton @click="handleOpenSetting">
      <rpa-icon name="setting" />
    </ControlButton>
  </Tooltip>

  <Tooltip v-if="props.control && userStore.currentTenant?.tenantType !== 'personal' && permissionStore.can('console', 'all')" :title="$t('excellenceCenter')">
    <ControlButton @click="handleToControl">
      <rpa-icon name="desktop" />
    </ControlButton>
  </Tooltip>
  <ControlButton v-if="props.message">
    <MessageTip />
  </ControlButton>
  <ControlButton v-if="props.userInfo">
    <UserInfo />
  </ControlButton>

  <Auth.Consult
    v-if="userStore.currentTenant?.tenantType !== 'enterprise'"
    ref="headerUpgradeConsultRef"
    class="hidden"
    :modal-only="true"
    :auth-type="appInfo.appAuthType"
    trigger="button"
    :button-conf="{
      buttonType: 'tag',
      currentEdition: userStore.currentTenant?.tenantType,
      expirationDate: userStore.currentTenant?.expirationDate,
      shouldAlert: userStore.currentTenant?.shouldAlert,
    }"
    :consult="{
      consultType: userStore.currentTenant?.expirationDate ? 'renewal' : 'consult',
      consultEdition: userStore.currentTenant?.tenantType as 'professional' | 'enterprise',
    }"
  />
</template>
