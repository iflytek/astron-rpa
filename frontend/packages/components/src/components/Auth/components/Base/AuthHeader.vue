<script setup lang="ts">
import { Button } from 'ant-design-vue'

interface Props {
  title: string
  subTitle?: string
  actionText?: string
}

const { actionText = '', title, subTitle = '' } = defineProps<Props>()

const emit = defineEmits<{
  actionClick: []
}>()

function handleActionClick() {
  emit('actionClick')
}
</script>

<template>
  <div class="auth-header">
    <div class="flex justify-between items-center mb-[24px]">
      <div class="text-[24px] text-[#000000D9] dark:text-[#FFFFFFD9]">
        {{ title }}
        <div v-if="subTitle" class="mt-[24px] text-[14px] text-[#000000A6] dark:text-[#FFFFFFD9]">
          {{ subTitle }}
        </div>
      </div>
      <Button
        v-if="actionText"
        type="link"
        class="!m-0 !p-0"
        @click="handleActionClick"
      >
        {{ actionText }}
      </Button>
    </div>
  </div>
</template>
