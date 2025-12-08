<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'
import { Input, Button, message } from 'ant-design-vue'

interface Props {
  modelValue?: string
  phone?: string
  placeholder?: string
  maxlength?: number
  codeLength?: number
  countdownSeconds?: number
  disabled?: boolean
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  maxlength: 6,
  codeLength: 6,
  countdownSeconds: 60,
  placeholder: '请输入验证码'
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  send: [phone: string | undefined]
}>()

const code = ref(props.modelValue || '')
const countdown = ref(0)
const isCodeSending = ref(false)
let countdownTimer: number | null = null

// 验证码按钮文本
const codeButtonText = computed(() => {
  if (countdown.value > 0) {
    return `${countdown.value}s 后重试`
  }
  if (isCodeSending.value) {
    return '发送中...'
  }
  return '发送验证码'
})

// 验证码按钮是否禁用
const codeButtonDisabled = computed(() => {
  return isCodeSending.value || countdown.value > 0 || props.disabled
})

// 发送验证码
const handleSendCode = async () => {
  if (codeButtonDisabled.value) {
    return
  }

  if (!props.phone) {
    message.error('请填写手机号')
    return
  }

  isCodeSending.value = true
  try {
    emit('send', props.phone)

    // 开始倒计时
    startCountdown()
  } catch (error) {
    console.error('发送验证码失败:', error)
  } finally {
    isCodeSending.value = false
  }
}

// 开始倒计时
const startCountdown = () => {
  if (countdownTimer) clearInterval(countdownTimer)

  countdown.value = props.countdownSeconds
  countdownTimer = window.setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      if (countdownTimer) clearInterval(countdownTimer)
      countdownTimer = null
    }
  }, 1000)
}

// 清空倒计时
const clearCountdown = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  countdown.value = 0
}

// 更新值
const handleInput = (value: string) => {
  code.value = value
  emit('update:modelValue', value)
}

// 清空表单
const resetForm = () => {
  code.value = ''
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
  <div class="code-input-wrapper">
    <Input
      :value="code"
      :placeholder="placeholder"
      :maxlength="maxlength"
      :disabled="disabled"
      size="large"
      @input="(e) => handleInput(e.target.value ?? '')"
    />
    <Button size="large" type="link" class="absolute !w-auto !h-auto !m-0 !p-0 right-[10px] top-[7px] !text-[14px] text-[#000000D9] dark:text-[#FFFFFFD9]" @click="handleSendCode">
      {{ codeButtonText }}
    </Button> 
  </div>
</template>

<style scoped>
.code-input-wrapper {
  width: 100%;
}
</style>