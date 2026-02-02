<script setup lang="ts">
import { Button } from 'ant-design-vue'

import LoginSvg from '../../assets/imgs/login_img.svg?component'

const emit = defineEmits<{
  accept: []
}>()

function handleClick() {
  emit('accept')
}
</script>

<template>
  <div
    class="w-full flex justify-center items-center"
  >
    <LoginSvg class="w-[316px] h-[262px]" />
    <Button type="primary" size="large" class="!h-[48px] w-[calc(100%-40px)] text-[16px] text-[#000000D9] bg-white fixed bottom-[65px] left-1/2 -translate-x-1/2 z-[99]" @click="handleClick">
      接受邀请
    </Button>
  </div>
</template>
