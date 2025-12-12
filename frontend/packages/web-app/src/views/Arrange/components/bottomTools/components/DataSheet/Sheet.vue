<script lang="ts" setup>
import { Sheet, SheetLocaleType, useTheme } from '@rpa/components'
import { useTranslation } from 'i18next-vue'
import { computed } from 'vue'

const props = defineProps<{ height: number }>()

const { isDark } = useTheme()
const { i18next } = useTranslation()

const locale = computed(() => {
  return i18next.language === 'zh-CN' ? SheetLocaleType.ZH_CN : SheetLocaleType.EN_US
})
</script>

<template>
  <Sheet :style="{ height: `${props.height}px` }" :dark-mode="isDark" :locale="locale" />
</template>