<script setup lang="ts">
import { isEmpty } from 'lodash-es'
import { computed } from 'vue'

import { ATOM_FORM_TYPE, PY_IN_TYPE } from '@/constants/atom'
import { PICK_TYPE_CV } from '@/views/Arrange/config/atom'

import { useFormItemLimitLength, useFormItemRequired, useFormItemSort } from './hooks/useFormItemSort'
import RenderFormType from './RenderFormType.vue'

const { formItem, size = 'default' } = defineProps<{ formItem: RPA.AtomDisplayItem, size?: 'default' | 'small' }>()

// const mainColor = getComputedStyle(document.documentElement).getPropertyValue('--headerFontColorHover')
const iconStyle = { fontSize: '16px', color: 'inherit' }

const { extraItem, editItem } = useFormItemSort()

const renderList = computed(() => {
  const formType = formItem?.formType?.type ?? ''

  if (Array.isArray(formItem.value)) {
    formItem.value.forEach((i) => {
      if (i.type === PY_IN_TYPE)
        formItem.isExpr = true
    })
  }
  let formTypeArr: string[] = []
  if (Object.is(formType, ATOM_FORM_TYPE.RESULT)) {
    formTypeArr = [ATOM_FORM_TYPE.INPUT, ATOM_FORM_TYPE.VARIABLE]
  }
  else if (Object.is(formType, ATOM_FORM_TYPE.PICK)) {
    switch (formItem.formType.params.use) {
      case PICK_TYPE_CV:
        formTypeArr = [ATOM_FORM_TYPE.INPUT, ATOM_FORM_TYPE.CV_IMAGE, ATOM_FORM_TYPE.CVPICK]
        break
      default:
        formTypeArr = [ATOM_FORM_TYPE.INPUT, ATOM_FORM_TYPE.ELEMENT, ATOM_FORM_TYPE.PICK, ATOM_FORM_TYPE.VARIABLE]
        break
    }
  }
  else if (Object.is(formType, ATOM_FORM_TYPE.CONTENTPASTE)) {
    formTypeArr = [ATOM_FORM_TYPE.INPUT, ATOM_FORM_TYPE.PYTHON, ATOM_FORM_TYPE.VARIABLE, ATOM_FORM_TYPE.CONTENTPASTE]
  }
  else {
    formTypeArr = formType.split('_')
  }

  return {
    editList: editItem.filter(item => formTypeArr.includes(item.type)),
    extraList: extraItem.filter(item => formTypeArr.includes(item.type)),
  }
})
</script>

<template>
  <div class="form-item-container w-full flex items-center" :class="[`form-item-container__${size}`]">
    <div
      v-if="!isEmpty(renderList.editList)"
      :style="{ width: `calc(100% - ${renderList.extraList.length * 40}px)` }"
      class="same-container editor-container flex items-center  text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)] bg-[#f3f3f7] dark:bg-[rgba(255,255,255,0.08)]"
      :class="[useFormItemRequired(formItem) || !useFormItemLimitLength(formItem) ? 'tip-required' : 'active-container']"
    >
      <RenderFormType
        v-for="item in renderList.editList"
        :key="item.type"
        :item-type="item.type"
        :item-data="formItem"
        :icon-style="iconStyle"
        :var-type="formItem.types"
      />
    </div>
    <div
      v-if="!isEmpty(renderList.extraList)"
      class="cursor-pointer flex items-center flex-1"
      :class="[!isEmpty(renderList.editList) ? 'same-container extra-btn justify-center ml-3  text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)] bg-[#f3f3f7] dark:bg-[rgba(255,255,255,0.08)]' : '']"
    >
      <RenderFormType
        v-for="item in renderList.extraList"
        :key="item.type"
        :item-type="item.type"
        :item-data="formItem"
        :icon-style="iconStyle"
        :var-type="formItem.types"
      />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.form-item-container {
  .same-container {
    border-radius: 8px;
  }

  .editor-container {
    position: relative;
    padding: 6px 10px;
    line-height: 20px;
  }

  .active-container {
    &:hover {
      border-color: var(--menuItemFontColor);
    }
  }

  .tip-required {
    border-color: $color-error;
  }

  .extra-btn {
    padding: 0px;
  }
}

.form-item-container__small {
  .editor-container {
    padding: 2px 7px;
  }
}
</style>
