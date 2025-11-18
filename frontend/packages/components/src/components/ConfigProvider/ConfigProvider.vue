<script setup lang="ts">
import { ConfigProvider } from 'ant-design-vue'
import enUS from 'ant-design-vue/es/locale/en_US'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import { computed } from 'vue'

import { getAntdvTheme, useTheme } from '../../theme'

const props = withDefaults(defineProps<{ locale?: string }>(), {
  locale: 'zh-CN',
})

const themeState = useTheme()

const locale = computed(() => (props.locale === 'zh-CN' ? zhCN : enUS))
const theme = computed(() => getAntdvTheme(themeState.colorTheme.value))
</script>

<template>
  <ConfigProvider :theme="theme" :locale="locale">
    <slot />
  </ConfigProvider>
</template>
