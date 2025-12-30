<script setup lang="ts">
import { Button, Input, message } from 'ant-design-vue'
import type { FormInstance } from 'ant-design-vue'
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

const { modelValue = '', placeholder = '请输入验证码', maxlength = 6, countdownSeconds = 60, disabled, wrapRef, relationKey, sendCaptcha } = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'send': []
}>()

const captcha = ref(modelValue || '')
const countdown = ref(0)
const isCodeSending = ref(false)
let countdownTimer: number | null = null

// 验证码按钮文本
const codeButtonText = computed(() => {
  if (countdown.value > 0) {
    return `验证码已发送(${countdown.value}s)`
  }
  if (isCodeSending.value) {
    return '发送中...'
  }
  return '发送验证码'
})

// 验证码按钮是否禁用
const codeButtonDisabled = computed(() => {
  return isCodeSending.value || countdown.value > 0 || disabled
})

// 发送验证码
async function handleSendCode() {
  if (codeButtonDisabled.value)
    return
  isCodeSending.value = true
  try {
    await wrapRef?.validateFields([relationKey || 'phone'])
    const phone = wrapRef?.getFieldsValue()[relationKey || 'phone']
    if (sendCaptcha) {
      await sendCaptcha?.(phone)
      startCountdown()
      message.success('验证码发送成功')
    }
    else {
      throw new Error('sendCaptcha 方法未定义')
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

  countdown.value = countdownSeconds
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
      :placeholder="placeholder"
      :maxlength="maxlength"
      :disabled="disabled"
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
