<script setup lang="ts">
import { useTheme } from '@rpa/components'
import type { SegmentedProps } from 'ant-design-vue'
import { Segmented } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed } from 'vue'

import Card from '../card.vue'

const { t } = useTranslation()

const themeOptions = computed<SegmentedProps['options']>(() => [
  {
    title: t('settingCenter.theme.light'),
    value: 'light',
    payload: 'sun',
  },
  {
    title: t('settingCenter.theme.dark'),
    value: 'dark',
    payload: 'moon',
  },
  {
    title: t('settingCenter.theme.auto'),
    value: 'auto',
    payload: 'system-mode',
  },
])

const { setColorMode, colorMode } = useTheme()
</script>

<template>
  <Card class="px-5 py-4" :title="t('settingCenter.appearance')">
    <template #suffix>
      <Segmented
        :value="colorMode"
        :options="themeOptions"
        @update:value="setColorMode"
      >
        <template #label="{ title, payload: icon }">
          <div class="flex items-center gap-1">
            <rpa-icon :name="icon" /> <span>{{ title }}</span>
          </div>
        </template>
      </Segmented>
    </template>
  </Card>
</template>
