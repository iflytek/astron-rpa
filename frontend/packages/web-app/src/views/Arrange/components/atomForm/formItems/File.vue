<script setup lang="ts">
import { EllipsisOutlined } from '@ant-design/icons-vue'
import { utilsManager } from '@/platform'

import type { FormItemProps, FormItemEmits } from './index'

const props = defineProps<FormItemProps>()
const emits = defineEmits<FormItemEmits>()

const handleClick = async () => {
  const res = await utilsManager.showDialog(props.item.formType.params);
  if (res) {
    const strVal = Array.isArray(res) ? res.join(',') : res
    emits('update', props.item.key, strVal)
  }
}
</script>

<template>
  <a-tooltip title="选择文件">
    <EllipsisOutlined class="cursor-pointer w-4 h-4 text-black dark:text-white opacity-45" @click="handleClick" />
  </a-tooltip>
</template>
