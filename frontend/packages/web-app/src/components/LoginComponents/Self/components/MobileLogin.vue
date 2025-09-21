<!-- @format -->
<script setup lang="ts">
import { CodeOutlined, UserOutlined } from '@ant-design/icons-vue'
import {
  Button,
  Col,
  Form,
  FormItem,
  Input,
  message,
  Row,
} from 'ant-design-vue'
import type { Rule } from 'ant-design-vue/es/form'
import { useTranslation } from 'i18next-vue'
import { throttle } from 'lodash-es'
import { computed, inject, reactive, ref } from 'vue'

import { setLoginFromType } from '@/utils/storage'
import { codeValidate, phoneValidate } from '@/utils/validate'

import { mobileLogin, sendSMSCode } from '@/api/login/login'

// import RegisterBtn from '@/components/LoginComponents/components/RegisterBtn.vue'

export interface PhoneFormState {
  phone: string
  code: string
}

const { t } = useTranslation()

const isLoading = ref(false)
const codeLoading = ref(false)
const codeLoginRef = ref()
const computedTime = ref(0)
const loginStep = inject('loginStepFn', (...args) => { return args })

const formData = reactive<PhoneFormState>({
  phone: '',
  code: '',
})

const codeLoginRules: Record<string, Rule[]> = reactive({
  phone: [{ validator: phoneValidate, trigger: 'blur' }],
  code: [{ validator: codeValidate, trigger: 'blur' }],
})

/**
 * 提交手机号登录
 */
function phoneSubmit() {
  codeLoginRef.value
  && codeLoginRef.value.validate().then((valid) => {
    if (valid) {
      isLoading.value = true
      mobileLogin({
        phone: formData.phone,
        code: formData.code,
      })
        .then(() => {
          loginStep('tenant')
          isLoading.value = false
          setLoginFromType('code')
        })
        .catch(() => {
          isLoading.value = false
        })
    }
  })
}

/**
 * 获取验证码
 */
const getCode = throttle(() => {
  codeLoginRef.value
  && codeLoginRef.value.validateFields(['phone']).then((valid) => {
    if (valid) {
      codeLoading.value = true
      sendSMSCode({
        phone: formData.phone,
      }).then(() => {
        codeCountdown()
        codeLoading.value = false
        message.success(t('verificationCodeSended'))
      }).catch(() => {
        codeLoading.value = false
      })
    }
  })
}, 1000)

/**
 * 倒计时
 */
function codeCountdown() {
  computedTime.value = 60
  const timer = setInterval(() => {
    computedTime.value--
    if (computedTime.value === 0) {
      clearInterval(timer)
    }
  }, 1000)
}
/**
 * 清除校验
 */
function clearValidate() {
  codeLoginRef.value && codeLoginRef.value.clearValidate()
}
/**
 * 获取验证码按钮文本
 */
const codeText = computed(() => {
  if (codeLoading.value) {
    return ''
  }
  let text = t('getVerificationCode')
  text
    = computedTime.value > 0
      ? t('acquiredAfterSeconds', { second: computedTime.value })
      : t('getVerificationCode')
  return text
})
/**
 * 暴露出去的方法
 */
defineExpose({
  clearValidate,
})
</script>

<template>
  <div>
    <Form ref="codeLoginRef" class="Login-right_form" :rules="codeLoginRules" :model="formData">
      <FormItem name="phone">
        <Input v-model:value="formData.phone" autocomplete="off" :placeholder="$t('enterMobileNumber')" :maxlength="11">
          <template #prefix>
            <UserOutlined style="color: rgba(0, 0, 0, 0.25)" />
          </template>
        </Input>
      </FormItem>
      <FormItem name="code">
        <Row>
          <Col span="15">
            <Input v-model:value="formData.code" autocomplete="off" :placeholder="$t('verificationCode')" :maxlength="6">
              <template #prefix>
                <CodeOutlined style="color: rgba(0, 0, 0, 0.25)" />
              </template>
            </Input>
          </Col>
          <Col span="8" offset="1">
            <Button class="codeButton" :disabled="computedTime > 0 || codeLoading" :loading="codeLoading" @click="getCode">
              {{ codeText }}
            </Button>
          </Col>
        </Row>
      </FormItem>
    </Form>
    <div class="otherOperation otherOperationLeft">
      <!-- <RegisterBtn /> -->
      <Button type="primary" style="width: 100%" :loading="isLoading" @click="phoneSubmit">
        {{ $t("login") }}
      </Button>
    </div>
  </div>
</template>
