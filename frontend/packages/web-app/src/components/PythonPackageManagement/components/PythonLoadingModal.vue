<script setup lang="ts">
import { NiceModal } from '@rpa/components'

import { useAppConfigStore } from '@/stores/useAppConfig'

defineProps<{
  loadingConfig: {
    loadingType: string
    loadingText: string
    cancleBtn: boolean
    okBtn: boolean
    headerText?: string
    icon: string
    closable: boolean
  }
}>()

const emit = defineEmits(['confirm'])

const modal = NiceModal.useModal()
const appConfigStore = useAppConfigStore()

function handleOkConfirm() {
  emit('confirm')
  handleCancel()
}

function handleCancel() {
  modal.hide()
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :class="`pythonDependence-loading-modal ${loadingConfig.loadingType}`"
    :width="400"
    :mask-closable="false"
    :mask-style="{ background: 'rgba(0, 0, 0, 0.2)' }"
    :title="loadingConfig.headerText"
    :footer="null"
    :closable="loadingConfig?.closable"
    centered
  >
    <div v-if="loadingConfig" class="pythonDependence-loading-modal_inner">
      <div class="tip flex flex-col justify-center items-center">
        <rpa-icon :name="`${appConfigStore.colorTheme === 'dark' ? 'python-installing-dark' : 'python-installing-light'}`" width="36" height="36" />
        <div class="mt-3">
          {{ loadingConfig.loadingText }}
        </div>
      </div>
      <div class="flex justify-end gap-2 mt-6">
        <a-button
          v-if="loadingConfig.cancleBtn" @click="handleCancel"
        >
          {{ $t("cancel") }}
        </a-button>
        <a-button v-if="loadingConfig.okBtn" type="primary" @click="handleOkConfirm">
          {{ $t("confirm") }}
        </a-button>
      </div>
    </div>
  </a-modal>
</template>
