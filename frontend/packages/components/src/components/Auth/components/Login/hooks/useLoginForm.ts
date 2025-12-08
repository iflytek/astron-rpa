import { reactive, ref } from 'vue'
import type { LoginFormData, LoginMode } from '../../../interface'
import { generateFormData } from '../../../schemas/factories'
import { accountLoginFormConfig, phoneLoginFormConfig } from '../../../schemas/loginRegister'

export type LoginEmitEvent =
  | 'submit'
  | 'switchToRegister'
  | 'forgetPassword'
  | 'sendCaptcha'

export function useLoginForm<M extends LoginMode>(
  mode: M,
  emit: ((e: 'submit', data: any) => void) &
        ((e: 'switchToRegister') => void) &
        ((e: 'forgetPassword') => void) &
        ((e: 'sendCaptcha', phone: string) => void)
) {
  const formRef = ref()

  const initialData = (): LoginFormData =>
    (mode === 'account'
      ? generateFormData(accountLoginFormConfig, { remember: false })
      : generateFormData(phoneLoginFormConfig))  as LoginFormData

  const formData = reactive<LoginFormData>(initialData())

  const handleSubmit = async () => {
    try {
      await formRef.value?.validateFields()
      emit('submit', formData)
    } catch (e) {
      console.error(`${mode} 表单校验失败`, e)
    }
  }

  const resetForm = () => {
    Object.assign(formData, initialData())
    formRef.value?.resetFields()
  }

  const emitEvent = (event: string) => {
    if (event === 'submit') return handleSubmit()
    if (event === 'switchToRegister') return emit('switchToRegister')
    if (event === 'forgetPassword') return emit('forgetPassword')
    if (event === 'sendCaptcha')
      return emit('sendCaptcha', formData.phone)
  }

  const config = mode === 'account' ? accountLoginFormConfig : phoneLoginFormConfig

  return { formRef, formData, config, resetForm, emitEvent }
}