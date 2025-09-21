<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { FormInstance } from 'ant-design-vue'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed, reactive, ref } from 'vue'

import { newTeam } from '@/api/market'
import { TEAMMARKETS } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import { useMarketStore } from '@/stores/useMarketStore'
import type { FormRules } from '@/types/common'

interface FormState {
  marketName: string
  marketDescribe: string
}

const { t } = useTranslation()
const modal = NiceModal.useModal()
const formRef = ref<FormInstance>()
const formState = reactive<FormState>({
  marketName: '',
  marketDescribe: '',
})

const rules = computed<FormRules>(() => ({
  marketName: [
    { required: true, message: t('enterMarketName'), trigger: 'change' },
    { max: 20, message: t('donotExceedCharacters', { num: 20 }), trigger: 'change' },
  ],
  marketDescribe: [
    { max: 500, message: t('donotExceedCharacters', { num: 500 }), trigger: 'change' },
  ],
}))

async function handleOk() {
  await formRef.value.validate()
  await newTeam(formState)
  message.success(t('createSuccess'))
  useRoutePush({ name: TEAMMARKETS })
  useMarketStore().refreshTeamList()
  modal.hide()
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :title="t('createTeamMarketplace')"
    :width="500"
    @ok="handleOk"
  >
    <a-form
      ref="formRef"
      :model="formState"
      :rules="rules"
      layout="vertical"
      autocomplete="off"
    >
      <a-form-item name="marketName" :label="t('name')">
        <a-input v-model:value="formState.marketName" :placeholder="t('enterMarketName')" />
      </a-form-item>
      <a-form-item name="marketDescribe" :label="t('description-1')">
        <a-textarea v-model:value="formState.marketDescribe" :placeholder="t('enterMarketDesc')" :rows="3" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>
