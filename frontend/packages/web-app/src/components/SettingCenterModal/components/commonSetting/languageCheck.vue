<script setup lang="ts">
import { Select } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'

import GlobalModal from '@/components/GlobalModal'
import { LanguageText } from '@rpa/components'
import { utilsManager } from '@/platform'
import useUserSettingStore from '@/stores/useUserSetting'

import Card from '../card.vue'

const userSettingStore = useUserSettingStore()
const { t, i18next } = useTranslation()

const handleCheck = (lang: string) => {
  if (lang === i18next.language) {
    return
  }

  GlobalModal.confirm({
    title: t('settingCenter.languageRestartTitle', { lang: LanguageText[lang] }),
    okType: 'primary',
    okText: t('restart'),
    onOk: async () => {
      await userSettingStore.setLanguageSetting(lang)
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
          v-for="[lng, text] in Object.entries(LanguageText)"
          :key="lng"
          :value="lng"
          @click="handleCheck(lng)"
        >
          {{ text }}
        </Select.Option>
      </Select>
    </template>
  </Card>
</template>
