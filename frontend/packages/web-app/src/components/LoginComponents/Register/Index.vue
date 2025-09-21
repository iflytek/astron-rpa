<!-- @format -->
<script setup>
import { CodeOutlined, LeftOutlined, LockOutlined, UserOutlined } from '@ant-design/icons-vue'
import { Button, Col, Form, FormItem, Input, InputPassword, message, Row } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { throttle } from 'lodash-es'
import { computed, inject, reactive, ref } from 'vue'

import { codeValidate, phoneValidate, validatePassNew } from '@/utils/validate'

import { rpaGetSMSCode, rpaRegister } from '@/api/login/login'

const loginStep = inject('loginStepFn', (...args) => { return args })
const { t } = useTranslation()
const codeLoginRef = ref(null)
const codeLoading = ref(false)
const computedTime = ref(0)

const formData = reactive({
  phone: '',
  code: '',
  password: '',
  confirmPassword: '',
})
const codeLoginRules = {
  phone: [
    {
      required: true,
      validator: phoneValidate,
      trigger: ['blur', 'change'],
    },
  ],
  code: [
    {
      required: true,
      validator: codeValidate,
      trigger: ['blur', 'change'],
    },
  ],
  password: [
    {
      required: true,
      validator: validatePassNew,
      trigger: ['blur', 'change'],
    },
  ],
  confirmPassword: [
    {
      required: true,
      trigger: ['blur', 'change'],
      validator: (_rule, value) => {
        if (!value) {
          return Promise.reject(new Error('密码不能为空'))
        }
        // 对比密码
        if (value !== formData.password) {
          return Promise.reject(new Error('两次输入不一致!'))
        }
        return Promise.resolve()
      },
    },
  ],
}
const getCode = throttle(() => {
  codeLoginRef.value
  && codeLoginRef.value.validateFields(['phone', 'password', 'confirmPassword']).then((valid) => {
    if (valid) {
      codeLoading.value = true
      rpaGetSMSCode({
        phone: formData.phone,
        code: formData.code,
      })
        .then(() => {
          codeCountdown()
          codeLoading.value = false
          message.success(t('verificationCodeSended'))
        })
        .catch(() => {
          codeLoading.value = false
        })
    }
  })
}, 1000)

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

function codeCountdown() {
  computedTime.value = 60
  const timer = setInterval(() => {
    computedTime.value--
    if (computedTime.value === 0) {
      clearInterval(timer)
    }
  }, 1000)
}

const registerSubmit = throttle(() => {
  codeLoginRef.value
  && codeLoginRef.value.validate().then((valid) => {
    if (valid) {
      rpaRegister({
        ...formData,
      }).then(() => {
        loginStep('login')
      })
    }
  })
}, 1000, {
  leading: true,
  trailing: false,
})

function backToLogin() {
  loginStep('login')
}
</script>

<template>
  <div class="self-container box-main">
    <div class="w-full">
      <div class="LoginBox">
        <div class="LoginBox-register " @click="backToLogin">
          <LeftOutlined />
          {{ $t("goBack") }}
        </div>
        <h5 class="LoginBox-title">
          注册
        </h5>
        <Form ref="codeLoginRef" class="Login-right_form" :rules="codeLoginRules" :model="formData">
          <FormItem name="phone">
            <Input v-model:value="formData.phone" autocomplete="off" :placeholder="$t('enterMobileNumber')" :maxlength="11">
              <template #prefix>
                <UserOutlined style="color: rgba(0, 0, 0, 0.25)" />
              </template>
            </Input>
          </FormItem>
          <FormItem name="password">
            <InputPassword v-model:value="formData.password" autocomplete="off" type="password" :placeholder="$t('enterPassword')" :maxlength="20">
              <template #prefix>
                <LockOutlined style="color: rgba(0, 0, 0, 0.25)" />
              </template>
            </InputPassword>
          </FormItem>
          <FormItem name="confirmPassword">
            <InputPassword v-model:value="formData.confirmPassword" autocomplete="off" type="password" :placeholder="$t('confirmPassword')" :maxlength="20">
              <template #prefix>
                <LockOutlined style="color: rgba(0, 0, 0, 0.25)" />
              </template>
            </InputPassword>
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
          <Button type="primary" style="width: 100%" :loading="isLoading" @click="registerSubmit">
            注册
          </Button>
        </Form>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
.self-container {
  position: absolute;
  top: 50%;
  transform: translateY(-45%);
  right: 80px;
  width: 338px;
  height: 340px;

  .LoginBox-register {
    position: absolute;
    top: -54px;
    left: -16px;
    font-size: 14px;
    font-weight: 400;
    color: #aaa;
    -webkit-user-select: none;
    -moz-user-select: none;
    user-select: none;
    cursor: pointer;
  }
}
</style>
