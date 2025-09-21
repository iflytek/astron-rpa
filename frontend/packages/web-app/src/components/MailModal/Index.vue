<script setup lang="ts">
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import type { Rule } from 'ant-design-vue/es/form'
import { useTranslation } from 'i18next-vue'
import { nanoid } from 'nanoid'
import { reactive, ref } from 'vue'

import { apiCheckEmail, apiSaveMail } from '@/api/mail'
import { EMAIL_OPTIONS, PROTOCAL_OPTIONS } from '@/constants/mail'

const props = defineProps<{ data: object }>()
const emit = defineEmits(['ok'])

const modal = NiceModal.useModal()
const { t } = useTranslation()

const emailOptions = EMAIL_OPTIONS.map((it) => {
  return {
    label: t(`mailServer.${it.value}`),
    value: it.value,
  }
})

const emailFormRef = ref(null)
const isEdit = ref(false)
const email = reactive({
  resourceId: nanoid(),
  mode: 'add',
  emailService: '163Email',
  emailProtocol: 'IMAP',
  emailServiceAddress: '',
  port: '',
  enableSSL: true,
  emailAccount: '',
  authorizationCode: '',
})

const emailFormRules: Record<string, Rule[]> = {
  emailServiceAddress: [{
    required: true,
    message: t('mailManageConfig.inputServerAddress'),
    trigger: 'blur',
  }],
  port: [{
    required: true,
    message: t('mailManageConfig.inputPort'),
    trigger: 'blur',
  }],
  emailAccount: [
    { required: true, message: t('mailManageConfig.inputEmailAccount') },
    { validator: validateTypedEmail },
  ],
  authorizationCode: [{
    required: true,
    message: t('mailManageConfig.inputAuthorizationCode'),
    trigger: 'blur',
  }],
}

const testStatus = ref('')
const errorMsg = ref('')

async function okhandle() {
  await validateForm()
  const data = await apiSaveMail(email)

  if (data.code === '000000') {
    emit('ok', email)
    modal.hide()
  }
}

async function testConnection() {
  if (testStatus.value === 'loading')
    return

  await validateForm()
  testStatus.value = 'loading'

  const mail = {
    enableSSL: email.enableSSL,
    emailService: email.emailService,
    emailProtocol: email.emailProtocol,
    emailAccount: email.emailAccount,
    authorizationCode: email.authorizationCode,
    ...(email.emailService === 'customEmail' && {
      emailServiceAddress: email.emailServiceAddress,
      port: email.port,
    }),
  }

  apiCheckEmail(mail).then(
    (res) => {
      if (res.data === '1') {
        testStatus.value = 'success'
        errorMsg.value = ''
      }
      else {
        testStatus.value = 'error'
        errorMsg.value = res.message
      }
    },
    (err) => {
      testStatus.value = 'error'
      errorMsg.value = err.message
    },
  )
}

function changeEmailService() {
  testStatus.value = ''
  resetForm()
}

function resetForm() {
  // 除了 resourceId, mode, emailService 其他重制
  emailFormRef.value.resetFields([
    'emailServiceAddress',
    'port',
    'emailAccount',
    'authorizationCode',
  ])
}

function validateForm() {
  return new Promise((resolve) => {
    emailFormRef.value.validate().then(() => {
      resolve(true)
    })
  })
}

// 邮箱地址校验
async function validateTypedEmail(_rule, value) {
  if (!value) {
    return Promise.resolve()
  }
  const type = email.emailService
  // xxx@xxx.xxx 的正则
  let pattern = /^\S+@\S+\.\S+$/
  if (type === '126Email') {
    pattern = /^([\w-])+@126\.com$/
  }
  if (type === '163Email') {
    pattern = /^([\w-])+@163\.com$/
  }
  if (type === 'qqEmail') {
    pattern = /^([\w-])+@qq\.com$/
  }
  // if (type === 'iflytek') {
  //   pattern = /^([\w-])+@iflytek\.com$/
  // }
  if (type === 'customMail') {
    pattern = /^([\w-])+@([\w-])+\.[\w-]+$/
  }
  // console.log('pattern: ', pattern)
  if (pattern && pattern.test(email.emailAccount)) {
    return Promise.resolve()
  }
  else {
    return Promise.reject(new Error(t('mailManageConfig.emailFormatError')))
  }
}

// 编辑邮箱数据
function assignEmailData(data) {
  if (data && data.resourceId) {
    Object.assign(email, data)
    isEdit.value = true
  }
}

assignEmailData(props.data)
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    class="mailAddModal"
    :width="400"
    :title="`${!isEdit ? t('mailManageConfig.addEmail') : t('mailManageConfig.editEmail')}`"
    :mask-closable="false"
    @ok="okhandle"
  >
    <a-form
      ref="emailFormRef"
      :rules="emailFormRules"
      :model="email"
      layout="vertical"
    >
      <!-- 邮箱服务器 -->
      <a-form-item
        :label="t('mailManageConfig.emailServer')"
        name="emailService"
      >
        <a-select
          v-model:value="email.emailService"
          style="width: 100%"
          :options="emailOptions"
          @select="changeEmailService"
        />
      </a-form-item>
      <!-- 邮箱协议 -->
      <div v-if="email.emailService === 'customEmail'" class="form-item custom">
        <a-form-item
          :label="t('mailManageConfig.emailProtocol')"
          name="emailProtocol"
        >
          <a-select
            v-model:value="email.emailProtocol"
            style="width: 100%"
            :options="PROTOCAL_OPTIONS"
          />
        </a-form-item>
        <!-- 服务器地址 -->
        <a-form-item
          :label="t('mailManageConfig.serverAddress')"
          name="emailServiceAddress"
        >
          <a-input
            v-model:value="email.emailServiceAddress"
            autocomplete="off"
            :placeholder="t('mailManageConfig.inputServerAddress')"
          />
        </a-form-item>
        <!-- 端口 -->
        <a-form-item :label="t('mailManageConfig.port')" name="port">
          <a-input
            v-model:value="email.port"
            autocomplete="off"
            :placeholder="t('mailManageConfig.inputPort')"
          />
        </a-form-item>
        <!-- 是否启用SSL -->
        <a-form-item :label="t('mailManageConfig.enableSSL')" name="enableSSL">
          <a-switch v-model:checked="email.enableSSL" />
        </a-form-item>
      </div>
      <!-- 邮箱账号 -->
      <a-form-item
        :label="t('mailManageConfig.emailAccount')"
        name="emailAccount"
      >
        <a-input
          v-model:value="email.emailAccount"
          autocomplete="off"
          :placeholder="t('mailManageConfig.inputEmailAccount')"
        />
      </a-form-item>
      <!-- 邮箱授权码 -->
      <a-form-item name="authorizationCode">
        <template #label>
          {{ t("mailManageConfig.authorizationCode") }}
          <a-tooltip :title="t('mailManageConfig.authorizationCodeTip')">
            <QuestionCircleOutlined class="ml-1" style="color: #1677ff" />
          </a-tooltip>
        </template>
        <a-input-password
          v-model:value="email.authorizationCode"
          autocomplete="off"
          :placeholder="t('mailManageConfig.inputAuthorizationCode')"
        />
      </a-form-item>
      <!-- 测试连接 -->
      <div class="form-item test-status flex items-center text-small">
        <div class="test-btn cursor-pointer" @click="testConnection">
          {{ t("mailManageConfig.testConnection") }}
        </div>
      </div>
      <div class="form-item test-status flex items-center text-small">
        <div>
          <div v-if="testStatus === 'loading'" class="flex items-center">
            <LoadingOutlined class="mr-2 primary" />{{
              t("mailManageConfig.connecting")
            }}...
          </div>
          <div v-if="testStatus === 'success'" class="flex items-center">
            <CheckCircleOutlined class="success mr-2" />{{
              t("mailManageConfig.connectSuccess")
            }}
          </div>
          <div v-else-if="testStatus === 'error'" class="flex items-center">
            <CloseCircleOutlined class="error mr-2" />{{
              t("mailManageConfig.connectFail")
            }}
          </div>
        </div>
        <div
          v-if="testStatus === 'error' && errorMsg"
          class="flex items-center ml-2"
        >
          {{ errorMsg }}
        </div>
      </div>
    </a-form>
  </a-modal>
</template>

<style lang="scss">
.mailAddModal {
  .ant-modal-body {
    max-height: 400px;
    overflow-y: auto;
    padding-bottom: 20px;
  }
  .ant-form-item {
    margin-bottom: 20px;
  }
  .test {
    margin-top: 10px;
    padding: 0;
  }
  .test-status {
    display: flex;
  }
  .test-btn {
    color: var(--color-primary);
  }
  .primary {
    color: #1677ff;
  }
  .success {
    color: #52c41a;
  }
  .error {
    color: #ff4d4f;
  }
}
</style>
