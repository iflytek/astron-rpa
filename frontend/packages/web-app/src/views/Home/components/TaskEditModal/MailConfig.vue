<script lang="ts" setup>
import { MailOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import { useTranslation } from 'i18next-vue'
import { inject, ref } from 'vue'

import { apiGetMailList } from '@/api/mail'
import { MailListModal } from '@/components/MailModal'
import { EMAIL_OPTIONS_MAP } from '@/constants/mail'
import type { Mail } from '@/types/schedule'

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
const mailList = ref([])

const mailTableRef = inject('mailTableRef', ref())
async function getMailList() {
  apiGetMailList({ pageNo: 1, pageSize: 100 }).then((res) => {
    mailList.value = res.data.records.map((item) => {
      return {
        value: item.emailAccount,
        label: item.emailAccount,
        data: item,
      }
    })
  })
}

function handleChange() {
  const mailItem = mailList.value.find(item => item.value === formState.user_mail)
  if (!mailItem)
    return
  formState.user_authorization = mailItem?.data.authorizationCode
  formState.mail_flag = mailItem?.data.emailService
  if (EMAIL_OPTIONS_MAP[formState.mail_flag] === 'advance') {
    formState.custom_mail_port = mailItem?.data.port
    formState.custom_mail_server = mailItem?.data.emailServiceAddress
  }
}
function mailModal() {
  NiceModal.show(MailListModal)
}
getMailList()
</script>

<template>
  <a-row>
    <a-col :span="12">
      <a-form-item name="userMail">
        <template #label>
          <label for="form_item_userMail" class="custom-label">{{ t('mailAccount') }}</label>
        </template>
        <a-select v-model:value="formState.user_mail" style="width: 100%" placeholder="t('mailAccountPlaceholder')" :options="mailList" @change="handleChange">
          <template #suffixIcon>
            <a-tooltip :title="t('mailManage')">
              <MailOutlined class="cursor-pointer text-base hover:text-primary" @click="mailModal" />
            </a-tooltip>
          </template>
        </a-select>
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
