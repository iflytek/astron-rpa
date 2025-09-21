<script setup lang="ts">
import { Select } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'

import locales from '@/constants/i18n'

import Card from '../card.vue'

const { i18next } = useTranslation()
</script>

<template>
  <Card class="px-5 py-4" :title="$t('displayLanguage')">
    <template #suffix>
      <Select :default-value="i18next.language" style="width: 160px;" @change="(lng: string) => i18next.changeLanguage(lng)">
        <Select.Option v-for="locale in locales" :key="locale.lng" :value="locale.lng">
          {{ locale.lang }}
        </Select.Option>
      </Select>
    </template>
  </Card>
</template>
