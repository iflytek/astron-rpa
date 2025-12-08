import { reactive, ref } from 'vue'

export type AuthFormEmitEvent = Record<string, any>

export function useDynamicForm<
  TData extends Record<string, any>,
  E extends AuthFormEmitEvent
>(
  config: any,                                 // 表单配置
  initialData: () => TData,                   // 初始数据
  emit: E,                                    // 业务层 emit（交叉重载）
  options: {                                // 可选
    remember?: boolean;                      // 是否带 remember 字段
  } = {}
) {
  const formRef = ref()

  const formData = reactive<TData>(initialData())

  const handleSubmit = async () => {
    try {
      await formRef.value?.validateFields()
      ;(emit as any)('submit', formData)
    } catch (e) {
      console.error('表单校验失败', e)
    }
  }

  const resetForm = () => {
    Object.assign(formData, initialData())
    formRef.value?.resetFields()
  }

  const emitEvent = (event: string, ...args: any[]) => {
    if (event === 'submit') return handleSubmit()
    if (event === 'sendCode') {
      const phone = (formData as any).phone
      if (phone) (emit as any)('sendCode', phone)
      return
    }
    ;(emit as any)(event, ...args)
  }

  return { formRef, formData, config, resetForm, emitEvent }
}