<script lang="ts" setup>
import { NiceModal } from '@rpa/components'
import { cloneDeep } from 'lodash-es'
import { provide, ref } from 'vue'

import DialogContent from './components/dialogContent.vue'
import DialogFooter from './components/dialogFooter.vue'
import type { FormItemConfig } from './types/index.ts'

const props = defineProps({
  title: {
    type: String,
    default: () => '自定义对话框',
  },
  option: {
    type: String,
    default: () => '',
  },
})
const emit = defineEmits(['ok'])

const modal = NiceModal.useModal()
const dialogData = ref(!props.option
  ? cloneDeep({
      mode: 'window',
      title: '自定义对话框',
      buttonType: 'confirm_cancel',
      formList: [] as Array<FormItemConfig>,
      table_required: false,
    })
  : JSON.parse(props.option).value) // 初始化自定义对话框结果

dialogData.value.title = props.title
const selectedFormItem = ref(dialogData.value?.formList[0] || null as FormItemConfig) // 当前选中需要配置的数据

provide('dialogData', {
  dialogData,
  updateDialogDataFormList: (type: 'splice' | 'push', ...params: any) => {
    dialogData.value?.formList[type](...params)
  },
})

provide('selectedFormItem', {
  selectedFormItem,
  updateSelectedFormItem: (data: FormItemConfig) => {
    selectedFormItem.value = data
  },
})

function saveData(data) {
  emit('ok', data)
  modal.hide()
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    centered
    :width="800"
    title="自定义对话框"
    class="dialog-modal"
    :z-index="19"
    :footer="null"
  >
    <DialogContent />
    <DialogFooter @save-data="saveData" @close="modal.hide" />
  </a-modal>
</template>

<style lang="scss">
@import './index.scss';
</style>
