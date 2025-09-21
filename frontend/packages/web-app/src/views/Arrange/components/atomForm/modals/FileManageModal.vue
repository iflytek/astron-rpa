<script setup lang="ts">
import { NiceModal } from '@rpa/components'

import NormalTable from '@/components/NormalTable/index.vue'

import useFileManageTable from './hooks/useFileManageTable'

const props = defineProps<{ itemDataVal: string }>()

const emit = defineEmits(['ok'])

const modal = NiceModal.useModal()
const { selectFileId, tableOption } = useFileManageTable()

selectFileId.value = props.itemDataVal || ''

function handleOk() {
  emit('ok', selectFileId.value)
  modal.hide()
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    title="共享文件夹文件"
    class="fileManageModal"
    :width="800"
    :scroll="{ y: 800 }"
    centered
    @ok="handleOk"
  >
    <NormalTable :option="tableOption" />
  </a-modal>
</template>

<style lang="scss">
.fileManageModal {
  .ant-modal-body {
    height: 480px;
    padding-top: 10px;
  }
  .ant-table-wrapper .ant-table-tbody > tr.ant-table-row {
    &:hover > td,
    &.selectRow > td {
      background: #d7d7ff66 !important;
      transition: none !important;
    }
  }
}
.dark {
  .fileManageModal .ant-table-wrapper .ant-table-tbody > tr.ant-table-row {
    &:hover > td,
    &.selectRow > td {
      background: #383764 !important;
    }
  }
}
</style>
