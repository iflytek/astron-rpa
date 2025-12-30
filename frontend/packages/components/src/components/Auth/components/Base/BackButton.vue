<script setup lang="ts">
import { Button } from 'ant-design-vue'

import { Icon as RpaIcon } from '../../../Icon'

interface Props {
  text?: string
}

const { text = '返回' } = defineProps<Props>()

const emit = defineEmits<{
  click: []
}>()

function handleClick() {
  emit('click')
}
</script>

<template>
  <Button
    class="!m-0 !mb-[8px] !p-0 h-auto cursor-pointer text-[#000000D9] dark:text-[#FFFFFFD9]"
    type="link"
    @click="handleClick"
  >
    <RpaIcon
      class="inline-block mr-[8px] text-[16px] h-[10px]"
      name="back"
    />
    <span class="text-[#000000D9] dark:text-[#FFFFFFD9]">{{ text }}</span>
  </Button>
</template>
