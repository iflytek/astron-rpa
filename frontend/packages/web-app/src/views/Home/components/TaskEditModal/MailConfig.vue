<script lang="ts" setup>
import { useTranslation } from 'i18next-vue'
import { inject, ref } from 'vue'

import { EMAIL_OPTIONS_MAP } from '@/constants/mail'
import type { Mail } from '@/types/schedule'
import MailSelect from '@/components/MailManage/MailSelect.vue'

import MailTable from './MailTable.vue'

const { taskJson, formState } = defineProps({
  taskJson: {
    type: Object,
  },
  formState: {
    type: Object as () => Mail,
  },
})

Object.assign(formState, taskJson)

const { t } = useTranslation()

const mailTableRef = inject('mailTableRef', ref())

function handleChange(mailItem: RPA.IMailItem) {
  formState.user_authorization = mailItem.authorizationCode
  formState.mail_flag = mailItem.emailService
  if (EMAIL_OPTIONS_MAP[formState.mail_flag] === 'advance') {
    formState.custom_mail_port = mailItem.port
    formState.custom_mail_server = mailItem.emailServiceAddress
  }
}
</script>

<template>
  <a-row>
    <a-col :span="12">
      <a-form-item name="userMail">
        <template #label>
          <label for="form_item_userMail" class="custom-label">{{ t('mailAccount') }}</label>
        </template>
        <MailSelect :placeholder="t('mailAccountPlaceholder')" v-model:value="formState.user_mail" @change="handleChange" />
      </a-form-item>
    </a-col>
    <a-col :span="12">
      <a-form-item name="intervalTime" class="ml-4 flex items-center text-[12px]">
        <template #label>
          <label for="form_item_intervalTime" class="custom-label">{{ t('mailCheckInterval') }}</label>
        </template>
        <div class="flex items-center text-[12px]">
          <!-- 数字输入，范围1-60 -->
          <a-input-number v-model:value="formState.interval_time" class="text-[12px]" :min="1" :max="60" />
          <span class="ml-2">{{ t('minutes') }}</span>
        </div>
      </a-form-item>
    </a-col>
  </a-row>

  <!-- 匹配规则 -->
  <a-form-item name="mailRules">
    <template #label>
      <label for="form_item_mailRules" class="custom-label" :title="t('mailRules')">{{ t('mailRules') }}</label>
    </template>
    <!-- 表格 -->
    <MailTable ref="mailTableRef" :form-state="formState" />
  </a-form-item>
</template>

<style lang="scss" scoped>
:deep(.ant-form-item-explain-error) {
  font-size: 12px;
}
:deep(.ant-form-item .ant-form-item-label) {
  text-align: left;
}

.custom-label {
  &::before {
    display: inline-block;
    margin-inline-end: 4px;
    color: #ff4d4f;
    font-size: 14px;
    font-family: SimSun, sans-serif;
    line-height: 1;
    content: '*';
  }
}
</style>
