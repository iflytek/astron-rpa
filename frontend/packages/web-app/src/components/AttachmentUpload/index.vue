<script setup lang="ts">
import { InfoCircleOutlined, UploadOutlined } from '@ant-design/icons-vue'
import { useVModel } from '@vueuse/core'
import type { UploadFile } from 'ant-design-vue'
import { Button, message, Tooltip, Upload } from 'ant-design-vue'
import { isFunction } from 'lodash-es'
import { nanoid } from 'nanoid'
import type { PropType } from 'vue'

import { getBaseURL } from '@/api/http/env'
import { uploadFile } from '@/api/resource'

export type Attachment = UploadFile

const props = defineProps({
  value: {
    type: Array as PropType<UploadFile[]>,
    required: true,
  },
  title: String,
  tooltip: String,
  accept: String,
  maxCount: Number,
  maxSize: Number, // 允许上传的最大体积，单位KB
  upload: Function as PropType<typeof uploadFile>,
})

const emits = defineEmits(['update:value'])

const data = useVModel(props, 'value', emits)

function updateFileState(id: string, file: Attachment) {
  data.value = data.value.map((item) => {
    return item.uid === id ? { ...item, ...file } : item
  })
}

async function handleBeforeUpload(file: File) {
  if (file.size / 1024 > props.maxSize) {
    message.error(`文件必须小于 ${props.maxSize / 1024}MB!`)
  }
  else {
    const fileData: Attachment = {
      uid: nanoid(),
      name: file.name,
      status: 'uploading',
    }

    // 移除第一个元素
    if (data.value.length >= props.maxCount) {
      data.value.shift()
    }
    data.value.push(fileData)

    const uploadFn = isFunction(props.upload) ? props.upload : uploadFile

    try {
      const res = await uploadFn(
        { file },
        {
          onUploadProgress: (progressEvent) => {
            updateFileState(fileData.uid, {
              ...fileData,
              percent: progressEvent.progress * 100,
              status: 'uploading',
            })
          },
        },
      )
      updateFileState(fileData.uid, {
        ...fileData,
        uid: res,
        status: 'success',
        url: `${getBaseURL()}/resource/file/download?fileId=${res}`,
      })
    }
    catch (error) {
      updateFileState(fileData.uid, { ...fileData, status: 'error', error })
    }
  }

  return false
}

function handleRemove(file: UploadFile) {
  data.value = data.value.filter(item => item.uid !== file.uid)
}
</script>

<template>
  <Upload
    name="file" :file-list="data" :accept="props.accept" :max-count="props.maxCount"
    :before-upload="handleBeforeUpload" @remove="handleRemove"
  >
    <div class="flex items-center gap-2">
      <Button class="flex items-center">
        <UploadOutlined />
        {{ title || '上传文件' }}
      </Button>

      <Tooltip v-if="props.tooltip" :title="props.tooltip">
        <InfoCircleOutlined />
      </Tooltip>
    </div>
  </Upload>
</template>

<style lang="scss" scoped>
:deep(.ant-upload-list-item) {
  .ant-upload-list-item-name {
    color: var(--color-primary);
  }
}
</style>
