import { reactive, ref } from 'vue'

import type { LoginFormData } from '../../../interface'
import { generateFormData } from '../../../schemas/factories'
import { forgotPasswordFormConfig } from '../../../schemas/loginRegister'

export type ForgotPasswordEmitEvent
  = | 'submit'
    | 'switchToLogin'

export function useForgotPassword(
  emit: ((e: 'submit', data: LoginFormData) => void)
    & ((e: 'switchToLogin') => void),
) {
  const formRef = ref()

  const initialData = (): LoginFormData =>
    generateFormData(forgotPasswordFormConfig)
  const formData = reactive<LoginFormData>(initialData())

  const handleSubmit = async () => {
    try {
      await formRef.value?.validateFields()
      emit('submit', formData)
    }
    catch (e) {
      console.error('忘记密码表单校验失败', e)
    }
  }

  const handleEvents = (event: string) => {
    if (event === 'submit')
      return handleSubmit()
    if (event === 'switchToLogin')
      return emit('switchToLogin')
  }

  return { formRef, formData, config: forgotPasswordFormConfig, handleEvents }
}
