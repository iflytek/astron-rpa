<script lang="ts" setup>
import { NiceModal } from '@rpa/components'
import { provide, ref } from 'vue'
import { get } from 'lodash-es'

import DialogContent from './components/dialogContent.vue'
import DialogFooter from './components/dialogFooter.vue'
import type { FormItemConfig } from './types/index.ts'

interface IDialogData {
  mode: string,
  title: string,
  buttonType: string,
  formList: Array<FormItemConfig>,
  table_required: boolean,
}

const props = withDefaults(defineProps<{ title?: string, option?: string }>(), {
  title: '自定义对话框'
})
const emit = defineEmits(['ok'])

const DEFAULT_DIALOG_DATA = (): IDialogData => ({
  mode: 'window',
  title: '自定义对话框',
  buttonType: 'confirm_cancel',
  formList: [],
  table_required: false,
})

const parseDialogData = (dataText: string): IDialogData => {
  try {
    const data = JSON.parse(dataText);
    // 需要兼容老的数据结构 { value: dialogData.value, rpa: 'special' }
    return get(data, 'rpa') === 'special' ? data.value : data;
  } catch {
    return DEFAULT_DIALOG_DATA()
  }
}

const modal = NiceModal.useModal()
// 初始化自定义对话框结果
const dialogData = ref(props.option ?  parseDialogData(props.option): DEFAULT_DIALOG_DATA())
dialogData.value.title = props.title

 // 当前选中需要配置的数据
const selectedFormItem = ref(dialogData.value?.formList[0] || null as FormItemConfig)

provide('dialogData', {
  dialogData,
  updateDialogDataFormList: (type: 'splice' | 'push', ...params: any) => {
    // TODO: 这里需要拆成两个函数
    // @ts-expect-error Dynamic method call on array with string index
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
