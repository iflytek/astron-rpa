<script setup lang="ts">
import { Button } from 'ant-design-vue'
import { computed } from 'vue';

declare global {
  interface Window {
    UtilsManager?: {
      openInBrowser: (url: string) => void
    }
  }
}

interface Props {
  type?: 'invite' | 'login'
}

const { type = 'login' } = defineProps<Props>()

const text = computed(() => {
  if (type === 'invite') {
    return '点击加入即代表您同意并接受'
  }
  return '勾选即代表您同意并接受'
})

const openLink = (linkType: 'service' | 'privacy') => {
  const urls: Record<string, string> = {
    service: 'https://www.iflyrpa.com/resource/server.html',
    privacy: 'https://www.iflyrpa.com/resource/licence.html',
  }
  if(window.UtilsManager){
    window.UtilsManager.openInBrowser(urls[linkType])
    return
  }
  window.open(urls[linkType], '_blank')
}

</script>

<template>
  <div class="w-full flex justify-start items-center text-center text-[#000000D9] dark:text-[#FFFFFFD9]" :class="type === 'invite' ? ' text-[12px] mt-[20px] ' : 'text-[14px]'">
    {{text}}
    <Button class="p-0 h-auto" :class="type === 'invite' ? ' text-[12px]' : 'text-[14px] mx-[4px]'" type="link" @click="openLink('service')">服务协议</Button>与<Button class="p-0 h-auto ml-[4px]" :class="type === 'invite' ? ' text-[12px]' : 'text-[14px]'" type="link" @click="openLink('privacy')">隐私政策</Button>
  </div>
</template>
