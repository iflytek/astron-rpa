import { reactive, ref } from 'vue'

import type { InviteInfo, LoginFormData } from '../../../interface'
import { modifyPasswordFormConfig } from '../../../schemas/loginRegister'

export type SetPasswordEmitEvent = 'submit' | 'switchToLogin'

export function useModifyPassword(
  inviteInfo: InviteInfo | null,
  emit: ((e: 'submit', data: LoginFormData) => void)
    & ((e: 'switchToLogin') => void),
) {
  const formRef = ref()

  const formData = reactive<LoginFormData>({
    loginName: '',
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
  })

  const config = modifyPasswordFormConfig(formData, !!inviteInfo)

  const handleSubmit = async () => {
    try {
      await formRef.value?.validateFields()
      emit('submit', formData)
    }
    catch (e) {
      console.error('修改密码表单校验失败', e)
    }
  }

  const handleEvents = (event: string) => {
    if (event === 'submit')
      return handleSubmit()
    if (event === 'switchToLogin')
      return emit('switchToLogin')
  }

  return { formRef, formData, config, handleEvents }
}
