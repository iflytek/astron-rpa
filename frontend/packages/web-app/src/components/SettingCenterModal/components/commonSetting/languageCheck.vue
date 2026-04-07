<script setup lang="ts">
import { Select } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'

import GlobalModal from '@/components/GlobalModal'
import locales from '@/constants/i18n'
import { utilsManager } from '@/platform'
import useUserSettingStore from '@/stores/useUserSetting'

import Card from '../card.vue'

const userSettingStore = useUserSettingStore()
const { t, i18next } = useTranslation()

const handleCheck = (locale: typeof locales[0]) => {
  if (locale.lng === i18next.language) {
    return
  }

  GlobalModal.confirm({
    title: t('settingCenter.languageRestartTitle', { lang: locale.lang }),
    okType: 'primary',
    okText: t('restart'),
    onOk: async () => {
      await userSettingStore.setLanguageSetting(locale.lng)
      utilsManager.restartApp()
    },
  })
}
</script>

<template>
  <Card class="px-5 py-4" :title="$t('displayLanguage')">
    <template #suffix>
      <Select :value="i18next.language" style="width: 160px;">
        <Select.Option
          v-for="locale in locales"
          :key="locale.lng"
          :value="locale.lng"
          @click="handleCheck(locale)"
        >
          {{ locale.lang }}
        </Select.Option>
      </Select>
    </template>
  </Card>
</template>
