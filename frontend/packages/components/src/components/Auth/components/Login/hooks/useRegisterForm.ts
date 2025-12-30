import { reactive, ref } from 'vue'

import type {
  AuthType,
  InviteInfo,
  RegisterFormData,
  RegisterMode,
} from '../../../interface'
import { generateFormData } from '../../../schemas/factories'
import {
  personalRegisterFormConfig,
} from '../../../schemas/loginRegister'

export type RegisterEmitEvent
  = | 'submit'
    | 'switchToLogin'

export function useRegisterForm(
  opts: { inviteInfo?: InviteInfo, edition?: string, authType?: AuthType } | null,
  emit: ((e: 'submit', data: any, mode: RegisterMode) => void)
    & ((e: 'switchToLogin') => void),
) {
  const formRef = ref()

  const formData = reactive<RegisterFormData>({
    loginName: '',
    phone: '',
    password: '',
    confirmPassword: '',
    captcha: '',
    agreement: false,
  })

  const formConfig = personalRegisterFormConfig(formData, !!opts?.inviteInfo, opts?.edition, opts?.authType)

  const initialData = () => generateFormData(formConfig as any)

  Object.assign(formData, initialData())

  const handleSubmit = async () => {
    try {
      await formRef.value?.validateFields()
      emit('submit', formData, 'REGISTER')
    }
    catch (e) {
      console.error(`注册表单校验失败`, e)
    }
  }

  const resetForm = () => {
    Object.assign(formData, initialData())
    formRef.value?.resetFields()
  }

  const handleEvents = (event: string) => {
    if (event === 'submit')
      return handleSubmit()
    if (event === 'switchToLogin')
      return emit('switchToLogin')
  }

  return { formRef, formData, config: formConfig, resetForm, handleEvents }
}
