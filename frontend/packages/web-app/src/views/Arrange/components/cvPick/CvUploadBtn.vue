<script lang="ts" setup>
import { NiceModal } from '@rpa/components'
import { message, Upload } from 'ant-design-vue'
import { ref } from 'vue'

import { getFileExtension, getFileName } from '@/utils/common'

import { uploadFile } from '@/api/resource'
import { useCvStore } from '@/stores/useCvStore.ts'

import { ElementRenameModal } from './modals'

const { type, groupId } = defineProps({
  type: {
    type: String,
    default: 'default', // default-默认展示图标和文字 icon-只展示图标 text-只展示文字
  },
  groupId: {
    type: String,
    default: '',
  },
})

const accepts = ['.jpg', '.jpeg', '.png']

const MAX_SIZE = 1024 * 10
const name = ref('')
const imageId = ref('')

function rename() {
  NiceModal.show(ElementRenameModal, {
    name: name.value,
    onConfirm: (newName: string) => {
      name.value = newName
      saveImg()
    },
  })
}

function saveImg() {
  if (!name.value) {
    message.error('请输入图像名称')
    return
  }
  useCvStore()
    .saveCvItem({
      id: '',
      name: name.value,
      imageId: imageId.value,
      parentImageId: '',
      elementData: JSON.stringify({
        version: '',
        type: 'cv',
        app: '',
        path: '',
        img: {
          self: '',
          parent: '',
        },
        pos: {
          self_x: '',
          self_y: '',
          parent_x: '',
          parent_y: '',
        },
        sr: {
          screen_w: window.screen.width,
          screen_h: window.screen.height,
        },
        picker_type: 'ELEMENT',
      }),
    }, groupId)
    .then(() => {
      message.success('上传成功')
    })
    .catch((err) => {
      if ([600000, '600000'].includes(err?.code)) {
        rename()
      }
    })
}

function handleBeforeUpload(file: File) {
  const isLt50M = file.size / 1024 < MAX_SIZE
  if (!isLt50M) {
    message.error(`上传图像必须小于 ${MAX_SIZE / 1024}MB!`)
    return false
  }
  const suffix = getFileExtension(file.name)
  if (!accepts.includes(suffix.toLowerCase())) {
    message.error('上传图像仅支持png/jpg/jpeg格式的图像')
    return false
  }

  upload(file)
  return false
}

function upload(file: File) {
  uploadFile({ file }).then((res) => {
    imageId.value = res
    name.value = getFileName(file.name)
    saveImg()
  })
}
</script>

<template>
  <Upload
    name="file"
    :file-list="[]"
    :accept="accepts.join(',')"
    action=""
    :before-upload="handleBeforeUpload"
  >
    <rpa-hint-icon
      v-if="type === 'icon'"
      placement="top"
      title="上传图像"
      name="word-insert-image"
      enable-hover-bg
    />
    <span v-else-if="type === 'text'">上传图像</span>
    <rpa-hint-icon v-else name="word-insert-image" class="!text-[12px]" enable-hover-bg>
      <template #suffix>
        <span class="ml-1">上传图像</span>
      </template>
    </rpa-hint-icon>
  </Upload>
</template>

<style lang="scss" scoped>
.rename {
  color: #999;
  font-size: 14px;
  margin-top: 5px;
  margin-bottom: 10px;
  display: inline-block;
  // margin-left: 5px;
}
</style>
