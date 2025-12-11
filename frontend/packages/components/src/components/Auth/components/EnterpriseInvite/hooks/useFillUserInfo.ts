import { reactive, ref } from 'vue'
import type { EnterpriseInvitFormData } from '../../../interface'
import { createEnterpriseInviteSetPasswordFormConfig } from '../../../schemas/enterpriseInvite'

export type FillUserInfoEmitEvent = 'submit' | 'back'

export function useFillUserInfo(
  emit: ((e: 'submit', data: EnterpriseInvitFormData) => void) &
        ((e: 'back') => void)
) {
  const formRef = ref()

  const formData = reactive<EnterpriseInvitFormData>({
    password: '',
    confirmPassword: '',
    loginName: '',
  })

  const config = createEnterpriseInviteSetPasswordFormConfig(formData)

  const handleSubmit = async () => {
    try {
      await formRef.value?.validateFields()
      emit('submit', formData)
    } catch (e) {
      console.error('完善信息表单校验失败', e)
    }
  }

  const handleEvents = (event: string) => {
    if (event === 'submit') return handleSubmit()
    if (event === 'back') return emit('back')
  }

  return { formRef, formData, config, handleEvents }
}