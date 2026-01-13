<script setup lang="ts">
import { HintIcon } from '@rpa/components'
import { Form, Empty } from 'ant-design-vue'
import { isEmpty } from 'lodash-es'

import type { AnyObj } from '@/types/common'
import type { DialogOption } from '@/views/Arrange/components/customDialog/types'

import createUserFormItem from '../hooks/createUserFormItem'
import useUserFormDialog from '../hooks/useUserFormDialog'

const simpleImage = Empty.PRESENTED_IMAGE_SIMPLE;

const props = defineProps<{ option: DialogOption, draggable?: boolean }>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', data: AnyObj): void
}>()

const { createItemFn } = createUserFormItem()

const close = () => emit('close')
const save = (data: AnyObj) => emit('save', data)

const {
  formRef,
  formState,
  handleClose,
  renderFooterBtns,
} = useUserFormDialog(props.option, close, save)
</script>

<template>
  <div data-tauri-drag-region class="userform">
    <div data-tauri-drag-region class="userform-header flex items-center justify-between">
      <div class="flex-1 leading-[50px]" :class="{ drag: draggable }">
        {{ option.title }}
      </div>
      <HintIcon name="close" :enable-hover-bg="true" size="20" @click="handleClose" />
    </div>
    <div
      data-tauri-drag-region
      class="userform-content"
      :style="option.mode === 'modal' ? { maxHeight: '350px' } : {}"
    >
      <Form ref="formRef" layout="vertical" :model="formState">
        <template v-if="!isEmpty(option?.itemList)">
          <Form.Item
            v-for="formItem in option.itemList"
            :key="formItem.bind"
            class="mb-3"
            :label="formItem.label"
            :name="formItem.bind"
            :rules="[
              ...(formItem?.rules || []),
              ...(formItem?.required ? [{ required: true, message: `${formItem.label}不能为空` }] : []),
            ]"
          >
            <component :is="createItemFn[formItem.dialogFormType](formItem, formState)" />
          </Form.Item>
        </template>
        <a-empty v-else :image="simpleImage" />
      </Form>
    </div>
    <div class="userform-footer">
      <component :is="renderFooterBtns(option.buttonType)" />
    </div>
  </div>
</template>

<style lang="scss">
.userform {
  background: $color-bg-container;
  width: 100%;
  border-radius: 4px;
  padding: 0 10px 10px 10px;

  &-header {
    font-size: 16px;
    font-weight: 400;
    padding: 0 14px;
  }

  &-content {
    overflow-x: hidden;
    overflow-y: auto;
    padding: 0 14px 10px 14px;

    .ant-select-dropdown {
      position: relative;
      z-index: 9999;
    }
  }

  &-footer {
    height: 6%;
    min-height: 30px;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    padding: 10px 14px;

    button {
      margin-left: 10px;
    }
  }
}
</style>
