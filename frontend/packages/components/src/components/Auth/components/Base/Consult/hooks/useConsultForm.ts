import { reactive, ref } from 'vue'

import type { ConsultFormData } from '../../../../interface'
import { generateFormData } from '../../../../schemas/factories'
import { consultFormConfig } from '../../../../schemas/loginRegister'

export type RegisterEmitEvent = 'submit'

export function useConsultForm(
  opts: { consultEdition?: string, consultType?: string } | null,
  emit: ((e: 'submit', data: any) => void),
) {
  const formRef = ref()

  const formConfig = consultFormConfig(
    (opts?.consultType as 'renewal' | 'consult') ?? 'consult',
    (opts?.consultEdition as 'professional' | 'enterprise') ?? 'professional',
  )

  const initialData = (): ConsultFormData =>
    generateFormData(formConfig)
  const formData = reactive<ConsultFormData>(initialData())

  Object.assign(formData, initialData())

  const handleSubmit = async () => {
    try {
      await formRef.value?.validateFields()
      emit('submit', formData)
    }
    catch (e) {
      console.error(`咨询表单校验失败`, e)
    }
  }

  const resetForm = () => {
    Object.assign(formData, initialData())
    formRef.value?.resetFields()
  }

  const handleEvents = (event: string) => {
    if (event === 'submit')
      return handleSubmit()
  }

  return { formRef, formData, config: formConfig, resetForm, handleEvents }
}
