<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { computed } from 'vue'

import { CustomComponentSettingModal } from '@/components/CustomComponentSetting'
import { useProcessStore } from '@/stores/useProcessStore'

import ToolButton from '../components/ToolButton.vue'

const className = '_tools-custom-comp-setting'
const settingModal = NiceModal.useModal(CustomComponentSettingModal)
const processStore = useProcessStore()

const show = computed(() => processStore.isComponent)
const disabled = computed(() => !processStore.isComponent)

function handleClick() {
  if (!processStore.isComponent) return
  settingModal.visible ? settingModal.hide() : settingModal.show({ clickOutsideIgnoreSelector: className })
}
</script>

<template>
  <ToolButton v-if="show" :tooltip="$t('components.customComponentSetting')" :label="$t('components.customComponentSetting')" :disabled="disabled" icon="tools-custom-comp-setting" :class="['_tools-custom-comp-setting']" @click="handleClick" />
</template>

