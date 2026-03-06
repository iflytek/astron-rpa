<script setup lang="ts">
import { Button } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
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
const { t } = useTranslation()

const text = computed(() => {
  if (type === 'show') {
    return t('components.auth.agreeToJoin')
  }
  return t('components.auth.checkToAgree')
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
    <Button class="p-0 h-auto" :class="type === 'show' ? '' : 'mx-[4px]'" type="link" @click="openLink('service')">
      {{ t('components.auth.serviceAgreement') }}
    </Button>{{ t('components.auth.and') }}<Button class="p-0 h-auto ml-[4px]" type="link" @click="openLink('privacy')">
      {{ t('components.auth.privacyPolicy') }}
    </Button>
  </div>
</template>
