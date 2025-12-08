import { reactive, ref } from 'vue'
import type { ForgotPasswordFormData } from '../../../interface'
import { generateFormData } from '../../../schemas/factories'
import { forgotPasswordFormConfig } from '../../../schemas/loginRegister'

export type ForgotPasswordEmitEvent =
  | 'submit'
  | 'sendCaptcha'
  | 'switchToLogin'

export function useForgotPassword(
  emit: ((e: 'submit', data: ForgotPasswordFormData) => void) &
        ((e: 'sendCaptcha', phone: string) => void) &
        ((e: 'switchToLogin') => void)
) {
  const formRef = ref()

  const initialData = (): ForgotPasswordFormData =>
    generateFormData(forgotPasswordFormConfig)
  const formData = reactive<ForgotPasswordFormData>(initialData())

  const handleSubmit = async () => {
    try {
      await formRef.value?.validateFields()
      emit('submit', formData)
    } catch (e) {
      console.error('忘记密码表单校验失败', e)
    }
  }

  const emitEvent = (event: string) => {
    if (event === 'submit') return handleSubmit()
    if (event === 'sendCaptcha') {
      const phone = formData.phone
      if (phone) emit('sendCaptcha', phone)
      return
    }
    if (event === 'switchToLogin') return emit('switchToLogin')
  }

  return { formRef, formData, config: forgotPasswordFormConfig, emitEvent }
}