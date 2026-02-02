import { reactive, ref, watch } from 'vue'

import { generateFormData } from '../../../schemas/factories'
import { inviteUserInfoFormConfig } from '../../../schemas/loginRegister'

export type InviteUserInfoEmitEvent
  = | 'submit'
    | 'switchToLogin'

export function useInviteUserInfo(
  modelValue: { phone?: string, name?: string },
  emit: ((e: 'submit') => void)
    & ((e: 'switchToLogin') => void),
) {
  const formRef = ref()

  const config = inviteUserInfoFormConfig()
  const initialData = (): { phone?: string, name?: string } =>
    generateFormData(config)
  const formData = reactive<{ phone?: string, name?: string }>(initialData())

  const setFormData = (data: { phone?: string, name?: string }) => {
    Object.assign(formData, { ...data, agreement: true })
  }

  setFormData(modelValue)

  watch(() => modelValue, (newVal) => {
    setFormData(newVal)
  })

  const handleSubmit = async () => {
    emit('submit')
  }

  const handleEvents = (event: string) => {
    if (event === 'submit')
      return handleSubmit()
    if (event === 'switchToLogin')
      return emit('switchToLogin')
  }

  return { formRef, formData, config, handleEvents }
}
