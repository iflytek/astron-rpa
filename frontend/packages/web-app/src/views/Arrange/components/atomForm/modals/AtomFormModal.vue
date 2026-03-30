<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { storeToRefs } from 'pinia'
import { Modal } from 'ant-design-vue'

import { useProcessStore } from '@/stores/useProcessStore'

import AtomBaseForm from '../AtomBaseForm.vue'
import AtomFooter from '../AtomFooter.vue'
import { RIGHT_TAB_KEY } from '../../../config'

const modal = NiceModal.useModal()
const processStore = useProcessStore()

const { rightTabActiveKey } = storeToRefs(processStore)

const handleClose = () => {
  modal.hide()
}

const handleToggleCollapsed = () => {
  modal.hide()
  rightTabActiveKey.value = RIGHT_TAB_KEY.NODE
}

const handleOk = () => {
  modal.hide()
}
</script>

<template>
  <Modal
    v-bind="NiceModal.antdModal(modal)"
    :closable="false"
    :footer="null"
    class="atom-form-modal"
    width="auto"
    centered
  >
    <AtomBaseForm
      class="mw-[1080px] w-[70vw] min-h-[60vh] max-h-[80vh]"
      headerClass="px-6 pt-5"
      bodyClass="px-6"
      @close="handleClose"
      :collapsed="false"
      @toggleCollapsed="handleToggleCollapsed"
    >
      <template #footer>
        <div class="flex items-center p-6">
          <AtomFooter />
          <div class="ml-auto space-x-2">
            <a-button key="back" @click="handleClose">{{ $t('cancel') }}</a-button>
            <a-button key="submit" type="primary" @click="handleOk">{{ $t('confirm') }}</a-button>
          </div>
        </div>
      </template>
    </AtomBaseForm>
  </Modal>
</template>

<style lang="scss">
.atom-form-modal {
  .ant-modal-content {
    padding: 0;
  }

  .ant-modal-footer {
    padding: 0 24px 20px 24px;
  }
}
</style>
