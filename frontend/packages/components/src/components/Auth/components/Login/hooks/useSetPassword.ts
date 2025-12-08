import { reactive, ref } from 'vue'
import type { SetPasswordFormData } from '../../../interface'
import { createSetPasswordFormConfig } from '../../../schemas/loginRegister'

/* 事件重载签名 */
export type SetPasswordEmitEvent = 'submit' | 'switchToLogin'

export function useSetPassword(
  emit: ((e: 'submit', data: SetPasswordFormData) => void) &
        ((e: 'switchToLogin') => void)
) {
  const formRef = ref()

  const formData = reactive<SetPasswordFormData>({
    password: '',
    confirmPassword: '',
  })

  const config = createSetPasswordFormConfig(formData)

  const handleSubmit = async () => {
    try {
      await formRef.value?.validateFields()
      emit('submit', formData)
    } catch (e) {
      console.error('设置密码表单校验失败', e)
    }
  }

  const emitEvent = (event: string) => {
    if (event === 'submit') return handleSubmit()
    if (event === 'switchToLogin') return emit('switchToLogin')
  }

  return { formRef, formData, config, emitEvent }
}