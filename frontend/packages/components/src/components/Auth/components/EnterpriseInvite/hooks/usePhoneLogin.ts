import { reactive, ref } from 'vue'
import type { LoginFormData, LoginMode } from '../../../interface'
import { generateFormData  } from '../../../schemas/factories'
import { enterprisePhoneLoginFormConfig } from '../../../schemas/enterpriseInvite'

export type PhoneLoginEmitEvent =
  | 'submit'
  | 'sendCaptcha'
  | 'switchToRegister'

export function usePhoneLogin(
  emit: ((e: 'submit', data: LoginFormData, mode: LoginMode) => void) &
        ((e: 'sendCaptcha', phone: string) => void) &
        ((e: 'switchToRegister') => void)
) {
  const formRef = ref()

  const initialData = (): LoginFormData =>
    generateFormData(enterprisePhoneLoginFormConfig)
  const formData = reactive<LoginFormData>(initialData())

  const handleSubmit = async () => {
    try {
      await formRef.value?.validateFields()
      emit('submit', formData, 'CODE')
    } catch (e) {
      console.error('手机登录表单校验失败', e)
    }
  }

  const handleEvents = (event: string) => {
    if (event === 'submit') return handleSubmit()
    if (event === 'sendCaptcha') {
      const phone = formData.phone
      if (phone) emit('sendCaptcha', phone)
      return
    }
    if (event === 'switchToRegister') return emit('switchToRegister')
  }

  return { formRef, formData, config: enterprisePhoneLoginFormConfig, handleEvents }
}