import { reactive, ref } from 'vue'
import type {
  RegisterMode,
  PersonalRegisterFormData,
  EnterpriseRegisterFormData,
  InviteInfo,
} from '../../../interface'
import { generateFormData } from '../../../schemas/factories'
import {
  personalRegisterFormConfig,
  enterpriseRegisterFormConfig,
} from '../../../schemas/loginRegister'

export type RegisterEmitEvent =
  | 'submit'
  | 'switchToLogin'
  | 'switchToPersonal'
  | 'switchToEnterprise'

export function useRegisterForm<M extends RegisterMode>(
  mode: M,
  opts: { inviteInfo: InviteInfo, edition?: string, authType?: string },
  emit: ((e: 'submit', data: any, mode: M) => void) &
        ((e: 'switchToLogin') => void) &
        ((e: 'switchToPersonal') => void) &
        ((e: 'switchToEnterprise') => void)
) {
  const formRef = ref()

  type TData = M extends 'PERSONAL' ? PersonalRegisterFormData : EnterpriseRegisterFormData

  const formData = reactive<TData>({
    loginName: '',
    phone: '',
    oldPassword: '',
    password: '',
    confirmPassword: '',
    captcha: '',
    agreement: false,
  } as unknown as TData)

  const formConfig = mode === 'PERSONAL'
    ? personalRegisterFormConfig(formData, !!opts.inviteInfo, opts.edition, opts.authType)
    : enterpriseRegisterFormConfig()
    
  const initialData = () => generateFormData(formConfig as any) as TData

  Object.assign(formData, initialData())

  const handleSubmit = async () => {
    try {
      await formRef.value?.validateFields()
      emit('submit', formData, mode)
    } catch (e) {
      console.error(`${mode} 注册表单校验失败`, e)
    }
  }

  const resetForm = () => {
    Object.assign(formData, initialData())
    formRef.value?.resetFields()
  }

  const handleEvents = (event: string) => {
    if (event === 'submit') return handleSubmit()
    if (event === 'switchToLogin') return emit('switchToLogin')
    if (event === 'switchToPersonal') return emit('switchToPersonal')
    if (event === 'switchToEnterprise') return emit('switchToEnterprise')
  }

  return { formRef, formData, config: formConfig, resetForm, handleEvents }
}