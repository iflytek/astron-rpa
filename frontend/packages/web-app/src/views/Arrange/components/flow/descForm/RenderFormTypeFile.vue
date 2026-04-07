<script setup lang="ts">
import { computed } from 'vue'
import { useTranslation } from 'i18next-vue'

import { replaceMiddle } from '@/utils/common'

import { DEFAULT_DESC_TEXT } from '@/views/Arrange/config/flow'

interface Props {
  itemType?: string
  id?: string
  desc?: string
  itemData?: RPA.AtomDisplayItem
  canEdit?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  itemType: '',
  id: '',
  desc: '',
  itemData: () => ({} as RPA.AtomDisplayItem),
  canEdit: true,
})

const { t } = useTranslation()

const isFolder = computed(() => {
  return props.itemData.formType?.params?.file_type === 'folder'
})

const fileText = computed(() => {
  if (props.desc !== DEFAULT_DESC_TEXT) {
    return props.desc
  }
  return isFolder.value ? t('common.selectFolder') : t('common.selectFile')
})

function handleClick() {
}
</script>

<template>
  <!-- 文件、文件夹 -->
  <a-tooltip placement="top" :title="fileText" :disabled="!canEdit">
    <span class="inline-flex items-center gap-1" @click="handleClick">
      {{ replaceMiddle(fileText) }}
      <rpa-icon name="open-folder" />
    </span>
  </a-tooltip>
</template>
