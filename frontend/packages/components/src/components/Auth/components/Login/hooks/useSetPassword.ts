import { reactive, ref } from 'vue'

import type { InviteInfo, LoginFormData } from '../../../interface'
import { createSetPasswordFormConfig } from '../../../schemas/loginRegister'

export type SetPasswordEmitEvent = 'submit' | 'back'

export function useSetPassword(
  inviteInfo: InviteInfo | null,
  emit: ((e: 'submit', data: LoginFormData) => void)
    & ((e: 'back') => void),
) {
  const formRef = ref()

  const formData = reactive<LoginFormData>({
    password: '',
    confirmPassword: '',
  })

  const config = createSetPasswordFormConfig(formData, !!inviteInfo)

  const handleSubmit = async () => {
    try {
      await formRef.value?.validateFields()
      emit('submit', formData)
    }
    catch (e) {
      console.error('设置密码表单校验失败', e)
    }
  }

  const handleEvents = (event: string) => {
    if (event === 'submit')
      return handleSubmit()
    if (event === 'back')
      return emit('back')
  }

  return { formRef, formData, config, handleEvents }
}
