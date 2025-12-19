<script setup lang="ts">
import { NiceModal } from '@rpa/components'

import { VUE_APP_HELP } from '@/constants'
import { utilsManager } from '@/platform'
import { ComplaintModal } from '@/components/ComplaintModal'

const props = defineProps<{ class: string }>()

function handleHelpInfo() {
  utilsManager.openInBrowser(VUE_APP_HELP)
}

function handleComplaint() {
  NiceModal.show(ComplaintModal)
}
</script>

<template>
  <a-dropdown placement="bottomCenter">
    <span :class="['cursor-pointer', props.class]">
      <rpa-icon name="help-circle" />
    </span>

    <template #overlay>
      <a-menu>
        <a-menu-item @click="handleHelpInfo">{{ $t('helperCenter') }}</a-menu-item>
        <a-menu-item @click="handleComplaint">投诉举报</a-menu-item>
      </a-menu>
    </template>
  </a-dropdown>
</template>
