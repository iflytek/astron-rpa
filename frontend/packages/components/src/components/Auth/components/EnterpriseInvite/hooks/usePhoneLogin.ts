import { reactive, ref } from 'vue'
import type { PhoneLoginFormData } from '../../../interface'
import { generateFormData } from '../../../schemas/factories'
import { enterprisePhoneLoginFormConfig } from '../../../schemas/enterpriseInvite'

export type PhoneLoginEmitEvent =
  | 'submit'
  | 'sendCode'
  | 'switchToRegister'

export function usePhoneLogin(
  emit: ((e: 'submit', data: PhoneLoginFormData) => void) &
        ((e: 'sendCode', phone: string) => void) &
        ((e: 'switchToRegister') => void)
) {
  const formRef = ref()

  const initialData = (): PhoneLoginFormData =>
    generateFormData(enterprisePhoneLoginFormConfig)
  const formData = reactive<PhoneLoginFormData>(initialData())

  const handleSubmit = async () => {
    try {
      await formRef.value?.validateFields()
      emit('submit', formData)
    } catch (e) {
      console.error('手机登录表单校验失败', e)
    }
  }

  const emitEvent = (event: string) => {
    if (event === 'submit') return handleSubmit()
    if (event === 'sendCode') {
      const phone = formData.phone
      if (phone) emit('sendCode', phone)
      return
    }
    if (event === 'switchToRegister') return emit('switchToRegister')
  }

  return { formRef, formData, config: enterprisePhoneLoginFormConfig, emitEvent }
}