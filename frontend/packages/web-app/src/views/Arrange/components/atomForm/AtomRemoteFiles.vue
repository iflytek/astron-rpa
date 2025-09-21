<script lang="ts" setup>
import { NiceModal } from '@rpa/components'
import { ref } from 'vue'

import { OTHER_IN_TYPE } from '@/constants/atom'
import { useSharedData } from '@/stores/useSharedData'

import { FileManageModal } from './modals'

defineOptions({
  name: 'AtomRemoteFiles',
})

const { renderData } = defineProps({
  renderData: {
    type: Object as () => any,
    default: () => ({}),
  },
})
const emit = defineEmits(['refresh'])

const shareDataStore = useSharedData()

function handleFilesModal() {
  NiceModal.show(FileManageModal, {
    itemDataVal: renderData.value[0]?.value || '',
    onOk: (fileId: string) => {
      emit('refresh', [{ type: OTHER_IN_TYPE, value: fileId }])
      setFileName(fileId)
      shareDataStore.getSharedFiles()
    },
  })
}

const fileName = ref('')
setFileName(renderData.value[0]?.value || '')

function setFileName(fileId: string) {
  fileName.value = fileId ? shareDataStore.sharedFiles.find(i => i.fileId === fileId)?.fileName : ''
}
</script>

<template>
  <div class="editor flex-1">
    {{ fileName }}
  </div>
  <span class="w-5 h-5 flex justify-center items-center relative" @click="handleFilesModal">
    <rpa-hint-icon title="选择文件" class="cursor-pointer" width="16px" height="16px" name="bottom-menu-ele-manage" />
  </span>
</template>
