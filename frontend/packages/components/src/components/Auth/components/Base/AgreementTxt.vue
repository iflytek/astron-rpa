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
  <div class="w-full flex justify-start items-center text-[12px] text-center text-[#000000D9] dark:text-[#FFFFFFD9]" :class="type === 'invite' ? ' text-[12px] mt-[20px] ' : 'text-[14px]'">
    {{text}}
    <Button class="p-0 h-auto" :class="type === 'invite' ? ' text-[12px]' : 'text-[14px]'" type="link">服务协议</Button>与<Button class="p-0 h-auto" :class="type === 'invite' ? ' text-[12px]' : 'text-[14px]'" type="link">隐私政策</Button>
  </div>
</template>
