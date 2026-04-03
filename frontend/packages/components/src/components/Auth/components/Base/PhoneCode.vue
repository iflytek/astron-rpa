<script setup lang="ts">
import { Button, Input, message } from 'ant-design-vue'
import type { FormInstance } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed, onBeforeUnmount, ref } from 'vue'

interface Props {
  modelValue?: string
  placeholder?: string
  maxlength?: number
  codeLength?: number
  countdownSeconds?: number
  disabled?: boolean
  wrapRef?: FormInstance | undefined
  relationKey?: string
  sendCaptcha?: (phone: string) => Promise<void>
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  maxlength: 6,
  countdownSeconds: 60,
})
const emit = defineEmits<{
  'update:modelValue': [value: string]
  'send': []
}>()
const { t } = useTranslation()
const captcha = ref(props.modelValue || '')
const countdown = ref(0)
const isCodeSending = ref(false)
let countdownTimer: number | null = null

const placeholderText = computed(() => props.placeholder || t('components.auth.enterCaptcha'))

// 验证码按钮文本
const codeButtonText = computed(() => {
  if (countdown.value > 0) {
    return t('components.auth.captchaSent', { seconds: countdown.value })
  }
  if (isCodeSending.value) {
    return t('components.auth.sending')
  }
  return t('components.auth.sendCaptcha')
})

// 验证码按钮是否禁用
const codeButtonDisabled = computed(() => {
  return isCodeSending.value || countdown.value > 0 || props.disabled
})

// 发送验证码
async function handleSendCode() {
  if (codeButtonDisabled.value)
    return
  isCodeSending.value = true
  try {
    await props.wrapRef?.validateFields([props.relationKey || 'phone'])
    const phone = props.wrapRef?.getFieldsValue()[props.relationKey || 'phone']
    if (props.sendCaptcha) {
      await props.sendCaptcha?.(phone)
      startCountdown()
      message.success(t('components.auth.captchaSendSuccess'))
    }
    else {
      throw new Error(t('components.auth.sendCaptchaUndefined'))
    }
  }
  catch (e) {
    console.log(e)
  }
  finally {
    isCodeSending.value = false
  }
}

// 开始倒计时
function startCountdown() {
  if (countdownTimer)
    clearInterval(countdownTimer)

  countdown.value = props.countdownSeconds
  countdownTimer = window.setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      if (countdownTimer)
        clearInterval(countdownTimer)
      countdownTimer = null
    }
  }, 1000)
}

// 清空倒计时
function clearCountdown() {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  countdown.value = 0
}

// 更新值
function handleInput(value: string) {
  captcha.value = value
  emit('update:modelValue', captcha.value)
}

function trimInput(e: Event) {
  captcha.value = (e.target as HTMLInputElement).value.trim()
  emit('update:modelValue', captcha.value)
}

// 清空表单
function resetForm() {
  captcha.value = ''
  clearCountdown()
  isCodeSending.value = false
}

// 暴露方法
defineExpose({
  resetForm,
  startCountdown,
  clearCountdown,
})

onBeforeUnmount(() => {
  clearCountdown()
})
</script>

<template>
  <div class="captcha-input-wrapper">
    <Input
      :value="captcha"
      :placeholder="placeholderText"
      :maxlength="props.maxlength"
      :disabled="props.disabled"
      size="large"
      @input="(e) => handleInput(e.target.value ?? '')"
      @blur="trimInput"
    />
    <Button size="large" type="link" class="absolute !w-auto !h-auto !m-0 !p-0 right-[10px] top-[7px] !text-[14px] text-[#000000D9] dark:text-[#FFFFFFD9]" :disabled="codeButtonDisabled" @click="handleSendCode">
      {{ codeButtonText }}
    </Button>
  </div>
</template>

<style scoped>
.captcha-input-wrapper {
  width: 100%;
}
</style>
