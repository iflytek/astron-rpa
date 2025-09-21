<!-- @format -->

<script lang="ts" setup>
import { QuestionCircleOutlined } from '@ant-design/icons-vue'
import { useTranslation } from 'i18next-vue'
import { ref } from 'vue'

import type { Mail } from '@/types/schedule'

const { formState } = defineProps({
  formState: {
    type: Object as () => Mail,
  },
})

const showGlobalError = ref(false)
const globalError = ref('')
const { t } = useTranslation()

const conditionOptions = [
  { label: t('mailRulesListData.and'), value: 'and' },
  { label: t('mailRulesListData.or'), value: 'or' },
  { label: t('mailRulesListData.all'), value: 'all' },
]

function mailTableValidate() {
  const fillKeys = ['sender_text', 'receiver_text', 'theme_text', 'content_text', 'attachment']
  const fillContent = fillKeys.filter(key => formState[key])
  if (formState.condition === 'all') {
    // 如果选择触发任意邮件，则不需要填写其他条件
    showGlobalError.value = false
    return true
  }
  if (formState.condition) {
    if (fillContent.length >= 1) {
      showGlobalError.value = false
      return true
    }
    else {
      showGlobalError.value = true
      globalError.value = t('taskRuleRequire.mailExpressionRequired')
      return false
    }
  }
  else {
    if (fillContent.length > 0) {
      showGlobalError.value = false
      return true
    }
    else {
      showGlobalError.value = true
      globalError.value = t('taskRuleRequire.mailExpressionRequired')
      return false
    }
  }
}

defineExpose({
  mailTableValidate,
})
</script>

<template>
  <div class="mail-table">
    <!-- <div class="mail-table__header">
    </div> -->
    <div class="mail-table__body">
      <a-form ref="mailTable" :model="formState" layout="vertical">
        <a-form-item name="condition">
          <template #label>
            {{ t('mailRulesList') }}
            <a-tooltip placement="top" :title="t('mailRulesListPlaceholder')">
              <QuestionCircleOutlined style="color: #1677ff; margin-left: 4px" />
            </a-tooltip>
          </template>
          <a-radio-group v-model:value="formState.condition" class="mail-table__header__select" :options="conditionOptions" />
        </a-form-item>
        <!-- 发件人地址包含，收件人地址包含，邮件主题包含， 邮件正文包含， 有附件 -->
        <div v-if="formState.condition !== 'all'">
          <a-row>
            <a-col :span="12">
              <a-form-item :label="t('mailRulesConfig.fromAddress')" name="sender_text" class="mr-2">
                <a-input v-model:value="formState.sender_text" class="text-[12px] h-[32px]" autocomplete="off" :placeholder="t('mailRulesConfig.fromAddressPlaceholder')" @input="mailTableValidate" />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item :label="t('mailRulesConfig.toAddress')" name="receiver_text" class="ml-2">
                <a-input
                  v-model:value="formState.receiver_text"
                  class="text-[12px] h-[32px]"
                  autocomplete="off"
                  :placeholder="t('mailRulesConfig.toAddressPlaceholder')"
                  @input="mailTableValidate"
                />
              </a-form-item>
            </a-col>
          </a-row>

          <a-row>
            <a-col :span="12">
              <a-form-item :label="t('mailRulesConfig.mailTheme')" name="theme_text" class="mr-2">
                <a-input
                  v-model:value="formState.theme_text"
                  class="text-[12px] h-[32px]"
                  autocomplete="off"
                  :placeholder="t('mailRulesConfig.mailThemePlaceholder')"
                  @input="mailTableValidate"
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item :label="t('mailRulesConfig.mailContent')" name="content_text" class="ml-2">
                <a-input
                  v-model:value="formState.content_text"
                  class="text-[12px] h-[32px]"
                  autocomplete="off"
                  :placeholder="t('mailRulesConfig.mailContentPlaceholder')"
                  @input="mailTableValidate"
                />
              </a-form-item>
            </a-col>
          </a-row>

          <a-form-item label="" name="attachment">
            <a-checkbox
              v-model:checked="formState.attachment"
              class="text-[12px]"
              @change="mailTableValidate"
            >
              {{ t('mailRulesConfig.hasAttachment') }}
            </a-checkbox>
          </a-form-item>
        </div>
      </a-form>
      <div v-if="showGlobalError" class="ant-form-item-explain-error">
        {{ globalError }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.mail-table {
  width: 100%;
  /* border: 1px solid #d9d9d9; */
  /* padding: 6px; */
}

.mail-table__header {
  padding: 0px 8px;
  height: 40px;
  /* background-color: #f0f2f5; */
}

.mail-table__body {
  /* padding-top: 16px; */
  /* border: 1px solid #d9d9d9; */
  border-top: none;
  /* padding-right: 8px; */
  /* padding-left: 8px; */
}

/* .mail-table__header__select {
  width: 80px;
} */
:deep(.ant-form-item-explain-error) {
  font-size: 12px;
}

:deep(.ant-form-item .ant-form-item-label) {
  text-align: left;
}
</style>
