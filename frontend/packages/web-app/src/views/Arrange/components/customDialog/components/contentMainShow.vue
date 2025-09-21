<script lang="ts" setup>
import { cloneDeep } from 'lodash-es'
import { inject, nextTick } from 'vue'
import draggable from 'vuedraggable'

import type { Fun } from '@/types/common.js'
import { genNonDuplicateID } from '@/views/Arrange/utils/index.ts'

import { limitFormsNum } from '../config/index.ts'
import type { FormItemConfig } from '../types/index.ts'
import { getRightIndex } from '../utils/index.ts'

import FormItem from './formItem.vue'

const { dialogData, updateDialogDataFormList } = inject('dialogData') as { dialogData: any, updateDialogDataFormList: any }
const { selectedFormItem, updateSelectedFormItem } = inject('selectedFormItem') as { selectedFormItem: FormItemConfig, updateSelectedFormItem: Fun }

function handleDragChange(event: any) {
  const { added } = event
  if (added && added.element) {
    const idx = dialogData.value?.formList.findIndex(i => i.id === added.element.id)
    const dialogItem = cloneDeep(added.element)
    updateDialogDataFormList('splice', idx, 1) // 删除, 为了不影响bindKey的计算
    if (dialogItem) {
      dialogItem.id = genNonDuplicateID()
      const bindKey = dialogItem?.bind?.key
      bindKey && (dialogItem.bind.value[0].value = `${bindKey}_${getRightIndex(dialogData.value?.formList, bindKey)}`)
      updateDialogDataFormList('splice', idx, 0, dialogItem) // 将更新好的dialogItem插入到原有位置
      updateSelectedFormItem(null)
      nextTick(() => {
        updateSelectedFormItem(dialogItem)
      })
    }
  }
}
function deleteItem(e: Event, item: FormItemConfig, index: number) {
  e.stopPropagation()
  dialogData.value.formList.splice(index, 1)
  if (selectedFormItem.value.id === item.id) {
    let resetIdx = -1
    if (dialogData.value.formList.length) {
      resetIdx = index
      if (index === dialogData.value.formList.length) {
        resetIdx -= 1
      }
    }
    updateSelectedFormItem(resetIdx > -1 ? dialogData.value.formList[resetIdx] : null)
  }
}
function handleClick(e: Event, item: FormItemConfig) {
  e.preventDefault()
  e.stopPropagation()
  updateSelectedFormItem(null)
  nextTick(() => {
    updateSelectedFormItem(item)
  })
}
</script>

<template>
  <div class="dialog-modal_main flex flex-col">
    <div class="header">
      对话框配置
    </div>
    <div class="flex-1 container border-[#E6E6E6] dark:border-[#494949]">
      <draggable
        item-key="id"
        :list="dialogData?.formList"
        filter=".forbid"
        :group="{ name: 'dialog', put: dialogData?.formList.length < limitFormsNum }"
        class="list-items"
        :touch-start-threshold="3"
        @change="handleDragChange"
      >
        <template #item="{ element: item, index }">
          <div
            class="group hover:bg-[#5D59FF]/[.35]"
            :class="`${selectedFormItem && selectedFormItem.id === item.id ? 'active item' : 'item'}`"
            :style="`min-height: 50px;${item.dialogFormType !== 'TEXT_DESC' && !item?.label.value[0].value ? 'border-color:#f00;' : ''}`"
            @click="(e) => handleClick(e, item)"
          >
            <div v-if="item.dialogFormType !== 'TEXT_DESC'" class="name" :style="`${!item?.label.value[0].value ? 'color:#f00;' : ''}`">
              <span v-if="item?.required?.value" class="starRequired">*</span>
              {{ !item?.label.value[0].value ? '请配置标题' : item.label.value[0].value }}
            </div>
            <div><FormItem :option="item" /></div>
            <rpa-hint-icon
              name="close-circle"
              class="absolute right-1 top-1 hidden group-hover:inline-flex"
              enable-hover-bg
              @click="(e) => { deleteItem(e, item, index) }"
            />
          </div>
        </template>
      </draggable>
      <div v-if="dialogData" class="footer">
        <a-button>取消</a-button>
        <a-button type="primary" style="margin-left: 8px;">
          确定
        </a-button>
      </div>
      <span
        v-if="dialogData?.formList.length === 0"
        class="list-empty-items text-[#000000]/[.85] dark:text-[#FFFFFF]/[.85]"
      >
        从左侧表单控件中拖拽控件进行对话框配置
      </span>
    </div>
  </div>
</template>
