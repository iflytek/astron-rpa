<script setup lang="ts">
import { Button } from 'ant-design-vue'
import { computed } from 'vue'

declare global {
  interface Window {
    UtilsManager?: {
      openInBrowser: (url: string) => void
    }
  }
}

interface Props {
  type?: 'show' | 'check'
}

const { type = 'check' } = defineProps<Props>()

const text = computed(() => {
  if (type === 'show') {
    return '点击加入即代表您同意并接受'
  }
  return '勾选即代表您同意并接受'
})

function openLink(linkType: 'service' | 'privacy') {
  const urls: Record<string, string> = {
    service: 'https://www.iflyrpa.com/resource/server.html',
    privacy: 'https://www.iflyrpa.com/resource/licence.html',
  }
  if (urls[linkType]) {
    if (window.UtilsManager) {
      window.UtilsManager.openInBrowser(urls[linkType])
      return
    }
    window.open(urls[linkType], '_blank')
  }
}
</script>

<template>
  <div class="flex justify-start items-center text-center text-[#000000D9] dark:text-[#FFFFFFD9] text-[14px]">
    {{ text }}
    <Button class="p-0 h-auto" :class="type === 'show' ? '' : 'mx-[4px]'" type="link" @check="openLink('service')">
      服务协议
    </Button>与<Button class="p-0 h-auto ml-[4px]" type="link" @check="openLink('privacy')">
      隐私政策
    </Button>
  </div>
</template>
