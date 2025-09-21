<script setup lang="ts">
import { RichTextEditor } from '@rpa/components'
import { theme } from 'ant-design-vue'

import { getBaseURL } from '@/api/http/env'
import { uploadFile } from '@/api/resource'

defineProps<{ placeholder?: string }>()

const data = defineModel<string>('value')

const { hashId } = theme.useToken()

async function upload(file: File) {
  const imageId = await uploadFile({ file })

  return `${getBaseURL()}/resource/file/download?fileId=${imageId}`
}
</script>

<template>
  <RichTextEditor
    v-model:value="data"
    :placeholder="placeholder"
    :upload-file="upload"
    :class="`ant-input ${hashId}`"
  />
</template>
