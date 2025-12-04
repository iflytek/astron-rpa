import { reactive, ref, onMounted } from 'vue'
import type { LoginFormData, LoginMode } from '../../../interface'
import { generateFormData } from '../../../schemas/factories'
import { accountLoginFormConfig, phoneLoginFormConfig } from '../../../schemas/loginRegister'
import { getRememberUser } from '../../../utils/remember'

export type LoginEmitEvent =
  | 'submit'
  | 'switchToRegister'
  | 'forgetPassword'
  | 'sendCaptcha'

export function useLoginForm<M extends LoginMode>(
  mode: M,
  emit: ((e: 'submit', data: any, mode: M) => void) &
        ((e: 'switchToRegister') => void) &
        ((e: 'forgetPassword') => void) &
        ((e: 'sendCaptcha', phone: string) => void)
) {
  const formRef = ref()

  const initialData = (): LoginFormData =>
    (mode === 'PASSWORD'
      ? generateFormData(accountLoginFormConfig, { remember: false })
      : generateFormData(phoneLoginFormConfig))  as LoginFormData

  const formData = reactive<LoginFormData>(initialData())

  const handleSubmit = async () => {
    try {
      await formRef.value?.validateFields()
      emit('submit', formData, mode)
    } catch (e) {
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
    if (event === 'submit') return handleSubmit()
    if (event === 'switchToRegister') return emit('switchToRegister')
    if (event === 'forgetPassword') return emit('forgetPassword')
    if (event === 'sendCaptcha'){
      return emit('sendCaptcha', formData.phone ?? '')
    }
  }

  const config = mode === 'PASSWORD' ? accountLoginFormConfig : phoneLoginFormConfig

  onMounted(() => {
    const remembered = getRememberUser()
    if (mode === 'PASSWORD' && remembered) {
      formData.phone = remembered.phone
      formData.password  = remembered.password
      formData.remember  = true
    }
  })

  return { formRef, formData, config, resetForm, clearValidates, handleEvents }
}