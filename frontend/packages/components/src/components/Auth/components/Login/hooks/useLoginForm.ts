import { onMounted, reactive, ref } from 'vue'

import type { InviteInfo, LoginFormData, LoginMode } from '../../../interface'
import { generateFormData } from '../../../schemas/factories'
import { accountLoginFormConfig, phoneLoginFormConfig } from '../../../schemas/loginRegister'
import { getRememberUser } from '../../../utils/remember'

export type LoginEmitEvent
  = | 'submit'
    | 'switchToRegister'
    | 'forgetPassword'
    | 'sendCaptcha'

export function useLoginForm<M extends LoginMode>(
  mode: M,
  opts: { inviteInfo: InviteInfo, edition?: string, authType?: string },
  emit: ((e: 'submit', data: any, mode: M) => void)
    & ((e: 'switchToRegister') => void)
    & ((e: 'forgetPassword') => void)
    & ((e: 'modifyPassword') => void),
) {
  const formRef = ref()

  const formConfig = mode === 'PASSWORD' ? accountLoginFormConfig(!!opts.inviteInfo, opts.edition, opts.authType) : phoneLoginFormConfig(!!opts.inviteInfo, opts.edition, opts.authType)

  const initialData = (): LoginFormData => formConfig
    ? generateFormData(formConfig, mode === 'PASSWORD' ? { remember: false } : {}) as LoginFormData
    : {} as LoginFormData

  const formData = reactive<LoginFormData>(initialData())

  const handleSubmit = async () => {
    try {
      await formRef.value?.validateFields()
      emit('submit', formData, mode)
    }
    catch (e) {
      console.error(`${mode} 表单校验失败`, e)
    }
  }

  const resetForm = () => {
    Object.assign(formData, initialData())
    formRef.value?.resetFields()
  }

  const clearValidates = () => {
    formRef.value?.clearValidates()
  }

  const handleEvents = async (event: string) => {
    if (event === 'submit')
      return handleSubmit()
    if (event === 'switchToRegister')
      return emit('switchToRegister')
    if (event === 'forgetPassword')
      return emit('forgetPassword')
    if (event === 'modifyPassword')
      return emit('modifyPassword')
  }

  onMounted(() => {
    const remembered = getRememberUser()
    if (mode === 'PASSWORD' && remembered && remembered.edition === opts.edition && remembered.authType === opts.authType) {
      const accountKey = opts.authType === 'uap' ? 'phone' : 'loginName'
      formData[accountKey] = remembered.account
      formData.password = remembered.password
      formData.remember = true
      formData.agreement = true
    }
  })

  return { formRef, formData, config: formConfig, resetForm, clearValidates, handleEvents }
}
