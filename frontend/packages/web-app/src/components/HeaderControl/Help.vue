<script setup lang="ts">
import { NiceModal } from '@rpa/components'

import { VUE_APP_HELP } from '@/constants'
import { utilsManager } from '@/platform'
import { ComplaintModal } from '@/components/ComplaintModal'

import ControlButton from './ControlButton.vue'

function handleHelpInfo() {
  utilsManager.openInBrowser(VUE_APP_HELP)
}

function handleComplaint() {
  NiceModal.show(ComplaintModal)
}
</script>

<template>
  <a-dropdown placement="bottom">
    <ControlButton :class="['cursor-pointer']">
      <rpa-icon name="help-circle" />
    </ControlButton>

    <template #overlay>
      <a-menu>
        <a-menu-item @click="handleHelpInfo">{{ $t('helperCenter') }}</a-menu-item>
        <a-menu-item @click="handleComplaint">{{ $t('complaint') }}</a-menu-item>
      </a-menu>
    </template>
  </a-dropdown>
</template>
