<script setup lang="ts">
import { computed } from 'vue'

import { ATOM_FORM_TYPE } from '@/constants/atom'
import { PICK_TYPE_CV } from '@/views/Arrange/config/atom'

import RenderFormTypeFile from './RenderFormTypeFile.vue'
import RenderFormTypePick from './RenderFormTypePick.vue'
import RenderFormTypeSelect from './RenderFormTypeSelect.vue'

// 可编辑的表单项类型
const EDITABLE_TYPES = [
  ATOM_FORM_TYPE.FILE,
  ATOM_FORM_TYPE.PICK,
  ATOM_FORM_TYPE.CVPICK,
  ATOM_FORM_TYPE.RADIO,
  ATOM_FORM_TYPE.SELECT,
  ATOM_FORM_TYPE.TEXTAREAMODAL,
] as const

// 选择类型集合
const SELECT_TYPES = new Set([
  ATOM_FORM_TYPE.RADIO,
  ATOM_FORM_TYPE.SELECT,
  ATOM_FORM_TYPE.SWITCH,
  ATOM_FORM_TYPE.CHECKBOX,
])

// 拾取类型集合
const PICK_TYPES = new Set([ATOM_FORM_TYPE.PICK, ATOM_FORM_TYPE.CVPICK])

const props = defineProps<{
  formItem: RPA.AtomDisplayItem
  desc: string | number
  id: string
  canEdit: boolean
}>()

/**
 * 获取表单类型数组
 */
const getFormTypeArray = (formType: string, params?: any): string[] => {
  if (formType === ATOM_FORM_TYPE.RESULT) {
    return [ATOM_FORM_TYPE.VARIABLE]
  }
  if (formType === ATOM_FORM_TYPE.PICK) {
    return params?.use === PICK_TYPE_CV
      ? [ATOM_FORM_TYPE.CVPICK]
      : [ATOM_FORM_TYPE.PICK]
  }
  return formType.split('_')
}

/**
 * 编辑配置列表
 */
const editList = computed(() => {
  const { type: formType, params } = props.formItem.formType
  const formTypeArr = getFormTypeArray(formType, params)
  return EDITABLE_TYPES.filter(type => formTypeArr.includes(type))
})

const hasEditList = computed(() => editList.value.length > 0)
</script>

<template>
  <template v-if="hasEditList">
    <template
      v-for="type in editList"
      :key="type"
    >
      <RenderFormTypeSelect
        v-if="SELECT_TYPES.has(type)"
        :id="id"
        :item-data="formItem"
        :can-edit="canEdit"
        :desc="desc"
        class="text-primary"
      />
      <RenderFormTypeFile
        v-else-if="type === ATOM_FORM_TYPE.FILE"
        :id="id"
        :item-type="type"
        :item-data="formItem"
        :can-edit="canEdit"
        :desc="desc.toString()"
        class="text-primary"
      />
      <RenderFormTypePick
        v-else-if="PICK_TYPES.has(type)"
        :id="id"
        :item-type="type as ATOM_FORM_TYPE.PICK | ATOM_FORM_TYPE.CVPICK"
        :can-edit="canEdit"
        :item-data="formItem"
        :desc="desc.toString()"
      />
    </template>
  </template>

  <a-tooltip v-else :title="desc">
    <span class="mx-1 px-1 whitespace-nowrap bg-[#726FFF]/[.1] rounded text-primary">
      {{ desc }}
    </span>
  </a-tooltip>
</template>
