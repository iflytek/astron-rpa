<script lang="ts" setup>
import { getAntdvTheme, NiceModal } from '@rpa/components'
import { watchImmediate } from '@vueuse/core'
import { App, ConfigProvider } from 'ant-design-vue'
import enUS from 'ant-design-vue/es/locale/en_US'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import dayjs from 'dayjs'
import { useTranslation } from 'i18next-vue'
import 'dayjs/locale/zh-cn'
import { computed } from 'vue'
import { VxeUI } from 'vxe-table'

import { useAppConfigStore } from '@/stores/useAppConfig'

const NiceModalProvider = NiceModal.Provider

const appStore = useAppConfigStore()
const { i18next } = useTranslation()

const locale = computed(() => (i18next.language === 'zh-CN' ? zhCN : enUS))
const theme = computed(() => getAntdvTheme(appStore.colorTheme))

watchImmediate(
  () => appStore.colorTheme,
  theme => VxeUI.setTheme(theme),
)

watchImmediate(
  () => i18next.language,
  (lang) => {
    dayjs.locale(lang === 'zh-CN' ? 'zh-cn' : 'en')
  },
)
</script>

<template>
  <ConfigProvider :theme="theme" :locale="locale">
    <App class="w-full h-full">
      <NiceModalProvider>
        <slot />
      </NiceModalProvider>
    </App>
  </ConfigProvider>
</template>
