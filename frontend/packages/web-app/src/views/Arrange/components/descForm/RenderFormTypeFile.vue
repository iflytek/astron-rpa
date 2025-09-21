<script setup lang="ts">
import { computed } from 'vue'

import { replaceMiddle } from '@/utils/common'

import { formBtnHandle } from '@/views/Arrange/components/atomForm/hooks/useRenderFormType'
import { DEFAULT_DESC_TEXT } from '@/views/Arrange/config/flow'

const { itemData, itemType, desc, id, canEdit } = defineProps({
  itemType: {
    type: String,
    default: '',
  },
  id: {
    type: String,
    default: '',
  },
  desc: {
    type: String,
    default: '',
  },
  itemData: {
    type: Object as () => RPA.AtomDisplayItem,
    default: () => ({}),
  },
  canEdit: {
    type: Boolean,
    default: true,
  },
})

const isFolder = computed(() => {
  return itemData.formType.params?.file_type === 'folder'
})

function getFileTxt() {
  return isFolder.value ? '选择文件夹' : '选择文件'
}

function fileTxt() {
  return desc !== DEFAULT_DESC_TEXT ? desc : getFileTxt()
}

function clickHandle() {
  formBtnHandle(itemData, itemType, { id })
}
</script>

<template>
  <!-- 文件、文件夹 -->
  <a-tooltip placement="top" :title="fileTxt()" :disabled="!canEdit">
    <span class="inline-flex items-center gap-1" @click="clickHandle">
      {{ replaceMiddle(fileTxt()) }}
      <rpa-icon name="open-folder" />
    </span>
  </a-tooltip>
</template>
