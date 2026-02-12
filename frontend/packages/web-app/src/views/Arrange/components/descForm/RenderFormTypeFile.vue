<script setup lang="ts">
import { computed } from 'vue'

import { useFlowStore } from '@/stores/useFlowStore'
import { replaceMiddle } from '@/utils/common'
import { utilsManager } from '@/platform'
import { DEFAULT_DESC_TEXT } from '@/views/Arrange/config/flow'

const { itemData, desc, canEdit } = defineProps({
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

const flowStore = useFlowStore()

const isFolder = computed(() => {
  return itemData.formType.params?.file_type === 'folder'
})

function getFileTxt() {
  return isFolder.value ? '选择文件夹' : '选择文件'
}

function fileTxt() {
  return desc !== DEFAULT_DESC_TEXT ? desc : getFileTxt()
}

async function clickHandle() {
  const res = await utilsManager.showDialog(itemData.formType.params)
  const strVal = res.join(',')
  if (strVal) {
    itemData.value = strVal
    flowStore.setFormItemValue(itemData.key, strVal, flowStore.activeAtom.id)
  }
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
