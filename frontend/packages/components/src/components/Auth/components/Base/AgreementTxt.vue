<script setup lang="ts">
import { Button } from 'ant-design-vue'
import { computed } from 'vue';

interface Props {
  type?: 'invite' | 'login'
}

const { type } = withDefaults(defineProps<Props>(), {
  type: 'login',
})

const text = computed(() => {
  if (type === 'invite') {
    return '点击加入即代表您同意并接受'
  }
  return '勾选即代表您同意并接受'
})

</script>

<template>
  <div class="w-full flex justify-center items-center text-[12px] text-center text-[#000000D9] mt-[20px] dark:text-[#FFFFFFD9]">
    {{text}}
    <Button class="text-[12px] mx-[2px] p-0 h-auto" type="link">服务协议</Button>与<Button class="text-[12px] ml-[2px] p-0 h-auto" type="link">隐私政策</Button>
  </div>
</template>
