import { reactive, ref } from 'vue'
import type {
  RegisterMode,
  PersonalRegisterFormData,
} from '../../../interface'
import { generateFormData } from '../../../schemas/factories'
import {
  marketInvitePersonalRegisterFormConfig,
} from '../../../schemas/marketInvite'

export type RegisterEmitEvent =
  | 'submit'
  | 'sendCaptcha'
  | 'switchToLogin'
  | 'switchToPersonal'
  | 'switchToEnterprise'

export function useRegisterForm<M extends RegisterMode>(
  mode: M,
  emit: ((e: 'submit', data: any) => void) &
        ((e: 'sendCaptcha', phone: string) => void) &
        ((e: 'switchToLogin') => void) &
        ((e: 'switchToPersonal') => void) &
        ((e: 'switchToEnterprise') => void)
) {
  const formRef = ref()

  type TData = PersonalRegisterFormData
  const initialData = (): TData => generateFormData(marketInvitePersonalRegisterFormConfig)
    

  const formData = reactive<TData>(initialData())

  const handleSubmit = async () => {
    try {
      await formRef.value?.validateFields()
      emit('submit', formData)
    } catch (e) {
      console.error(`${mode} 注册表单校验失败`, e)
    }
  }

  const resetForm = () => {
    Object.assign(formData, initialData())
    formRef.value?.resetFields()
  }

  const emitEvent = (event: string) => {
    if (event === 'submit') return handleSubmit()

    if (event === 'sendCaptcha') {
      const phone = (formData as PersonalRegisterFormData).phone
      if (phone) emit('sendCaptcha', phone)
      return
    }

    if (event === 'switchToLogin') return emit('switchToLogin')
    if (event === 'switchToPersonal') return emit('switchToPersonal')
    if (event === 'switchToEnterprise') return emit('switchToEnterprise')
  }

  const config = marketInvitePersonalRegisterFormConfig

  return { formRef, formData, config, resetForm, emitEvent }
}