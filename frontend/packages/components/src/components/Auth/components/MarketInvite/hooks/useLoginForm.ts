import { reactive, ref } from 'vue'
import type { AccountLoginFormData, PhoneLoginFormData, LoginMode } from '../../../interface'
import { generateFormData } from '../../../schemas/factories'
import { marketInviteAccountLoginFormConfig, marketInvitePhoneLoginFormConfig } from '../../../schemas/marketInvite'

export type LoginEmitEvent =
  | 'submit'
  | 'switchToRegister'
  | 'forgetPassword'
  | 'sendCode'

export function useLoginForm<M extends LoginMode>(
  mode: M,
  emit: ((e: 'submit', data: any) => void) &
        ((e: 'switchToRegister') => void) &
        ((e: 'forgetPassword') => void) &
        ((e: 'sendCode', phone: string) => void)
) {
  const formRef = ref()

  type TData = M extends 'account' ? AccountLoginFormData : PhoneLoginFormData
  const initialData = (): TData =>
    (mode === 'account'
      ? generateFormData(marketInviteAccountLoginFormConfig, { remember: false })
      : generateFormData(marketInvitePhoneLoginFormConfig)) as TData

  const formData = reactive<TData>(initialData())

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
    if (event === 'sendCode')
      return emit('sendCode', (formData as PhoneLoginFormData).phone)
  }

  const config = mode === 'account' ? marketInviteAccountLoginFormConfig : marketInvitePhoneLoginFormConfig

  return { formRef, formData, config, resetForm, emitEvent }
}