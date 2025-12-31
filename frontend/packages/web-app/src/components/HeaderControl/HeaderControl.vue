<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { Tooltip } from 'ant-design-vue'

import { SettingCenterModal } from '@/components/SettingCenterModal'
import { VUE_APP_COMMANDER } from '@/constants'
import { utilsManager } from '@/platform'
import useUserSettingStore from '@/stores/useUserSetting.ts'

import MessageTip from '../MesssageTip/Index.vue'
import UserInfo from './UserInfo.vue'
import Help from './Help.vue'
import ControlButton from './ControlButton.vue'

interface HeaderControlProps {
  setting?: boolean
  control?: boolean
  message?: boolean
  userInfo?: boolean
}

// 控制按钮显示
const props = withDefaults(defineProps<HeaderControlProps>(), ({
  setting: true,
  control: false,
  message: true,
  userInfo: true,
}))

useUserSettingStore()

function handleOpenSetting() {
  NiceModal.show(SettingCenterModal)
}

function handleToControl() {
  utilsManager.openInBrowser(VUE_APP_COMMANDER)
}
</script>

<template>
  <Help />

  <Tooltip v-if="props.setting" :title="$t('setting')">
    <ControlButton @click="handleOpenSetting">
      <rpa-icon name="setting" />
    </ControlButton>
  </Tooltip>

  <Tooltip v-if="props.control" :title="$t('excellenceCenter')">
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
</template>
