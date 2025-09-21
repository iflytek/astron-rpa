<script setup lang="ts">
import { LockOutlined, UserOutlined } from '@ant-design/icons-vue'
import { Button, Checkbox, Form, FormItem, Input } from 'ant-design-vue'
import type { Rule } from 'ant-design-vue/es/form'
import { inject, onMounted, reactive, ref } from 'vue'

import { clearAccount, getAccount, setAccount, setLoginFromType, setUserName } from '@/utils/storage'
import { validateAccount, validatePass } from '@/utils/validate'

import { rpaLoginPassWord } from '@/api/login/login'
import RegisterBtn from '@/components/LoginComponents/components/RegisterBtn.vue'

export interface AccountFormState {
  userName: string
  password: string
}

const remember = ref(false)
const isLoading = ref(false)
const passwordLoginRef = ref(null)

const loginStep = inject('loginStepFn', (...args) => { return args })

const formData = reactive<AccountFormState>({
  userName: '',
  password: '',
})
const passwordLoginRules: Record<string, Rule[]> = reactive({
  userName: [
    { validator: validateAccount, trigger: 'blur' },
  ],
  password: [
    { validator: validatePass, trigger: 'blur' },
  ],
})

onMounted(() => {
  getAccountInfo()
})

// 获取本地存储的账户信息
function getAccountInfo() {
  getAccount().then((res) => {
    if (res) {
      const { userName, password } = res
      formData.userName = userName
      formData.password = password
      remember.value = true
    }
  })
}

// 记住密码
function rememberPasswordFn() {
  const { userName, password } = formData
  if (remember.value) {
    setAccount({
      userName,
      password,
    })
  }
  else {
    clearAccount()
  }
}

// 账户密码登录
function accountSubmit() {
  passwordLoginRef.value
  && passwordLoginRef.value.validate().then(() => {
    const { userName, password } = formData
    isLoading.value = true
    rpaLoginPassWord({
      phone: userName,
      password,
    }).then(() => {
      loginStep('tenant')
      setUserName(userName)
      // useRoutePush({ name: DESIGNER })
      rememberPasswordFn()
      setLoginFromType('account')
      isLoading.value = false
    }).catch(() => {
      isLoading.value = false
    })
  })
}

// 清除校验
function clearValidate() {
  passwordLoginRef.value && passwordLoginRef.value.clearValidate()
}

defineExpose({
  clearValidate,
})
</script>

<template>
  <div>
    <Form ref="passwordLoginRef" :model="formData" :rules="passwordLoginRules" class="Login-right_form" :label-col="{ span: 4 }">
      <FormItem name="userName">
        <Input v-model:value="formData.userName" autocomplete="off" :placeholder="$t('enterUserName')">
          <template #prefix>
            <UserOutlined style="color: rgba(0, 0, 0, 0.25)" />
          </template>
        </Input>
      </FormItem>
      <FormItem name="password">
        <Input v-model:value="formData.password" autocomplete="off" type="password" :placeholder="$t('enterPassword')" :maxlength="20">
          <template #prefix>
            <LockOutlined style="color: rgba(0, 0, 0, 0.25)" />
          </template>
          <!-- <template #suffix>
            <Button slot="suffix" size="small" type="link" style="margin-right: -16px;" @click="handleForget">
              {{ $t("forgotPassword") }}
            </Button>
          </template> -->
        </Input>
      </FormItem>
    </Form>
    <div class="otherOperation otherOperationLeft">
      <Checkbox v-model:checked="remember" class="rememberChecked mb-2">
        {{ $t("rememberPassword") }}
      </Checkbox>
      <RegisterBtn />
      <Button type="primary" style="width: 100%" :loading="isLoading" @click="accountSubmit">
        {{ $t("login") }}
      </Button>
    </div>
  </div>
</template>
