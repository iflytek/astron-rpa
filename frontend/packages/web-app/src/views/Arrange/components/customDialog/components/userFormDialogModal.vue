<script setup lang="ts">
import { NiceModal } from '@rpa/components'

import UserFormDialog from './userFormDialog.vue'

const props = defineProps<{ option: object }>()

const modal = NiceModal.useModal()
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    class="user-form-dialog-modal"
    :width="500"
    centered
    :closable="false"
    :footer="null"
  >
    <UserFormDialog :option="props.option" @close="modal.hide" />
  </a-modal>
</template>

<style lang="scss">
.user-form-dialog-modal {
  .ant-modal-content {
    padding: 0;
  }
}
</style>
