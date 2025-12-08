<script setup lang="ts" >
import { ref, h } from 'vue'
import { Form, Input, Checkbox, Select, Textarea, message } from 'ant-design-vue'
import type { FormInstance } from 'ant-design-vue'
import type { FieldSchema } from '../../schemas/factories.tsx'
import PhoneCode from './PhoneCode.vue'
import type { FormConfig } from '../../schemas/factories.tsx'
import { Icon as RpaIcon } from '../../../Icon'

interface Props<T = any> {
  config: FormConfig
  modelValue?: T
  loading?: boolean
  sendCaptcha?: (phone: string) => Promise<void>
  handleEvents?: (event: string, ...args: any[]) => void
}

const { modelValue, loading, config, handleEvents, sendCaptcha } = defineProps<Props>()

const emit = defineEmits<{
  submit: [value: any]
}>()

const formRef = ref<FormInstance>()
const codeInputRefs = ref<Record<string, InstanceType<typeof PhoneCode>>>({})

const validateFields = async (fieldNames?: string[]) => {
  try {
    if (fieldNames && fieldNames.length > 0) {
      await formRef.value?.validateFields(fieldNames)
      return true
    } else {
      await formRef.value?.validate()
      return true
    }
  } catch (error) {
    throw error
  }
}

// 重置表单
const resetFields = () => {
  formRef.value?.resetFields()
  Object.values(codeInputRefs.value).forEach(ref => {
    ref?.resetForm()
  })
}

const clearValidates = () => {
  formRef.value?.clearValidate()
}

const handleSendCaptcha = async (field: FieldSchema) => {
  await validateFields([field.relationKey || 'phone'])      // 校验不通过会抛错
  await sendCaptcha?.(modelValue[field.relationKey || 'phone'])       // 只有校验通过才走到这里
  codeInputRefs.value[field.key]?.startCountdown()
  message.success('验证码发送成功')
}

defineExpose({
  formRef,
  resetFields,
  clearValidates,
  validateFields,
})
</script>

<template>  
  <Form
    ref="formRef"
    :model="modelValue"
    :layout="config.layout || 'vertical'"
    :label-col="config.labelCol || { span: 0 }"
    :wrapper-col="config.wrapperCol || { span: 24 }"
    class="dynamic-form h-full"
  >
    <template v-for="field in config.fields" :key="field.key">
      <Form.Item
        :name="field.key"
        :rules="field.rules"
        :class="`form-item-${field.type} form-item-${field.key}`"
      >      
        <Input
          v-if="field.type === 'input'"
          v-model:value="modelValue[field.key]"
          :placeholder="field.placeholder"
          autocomplete="new-password"
          size="large"
          v-bind="field.props"
          @blur="(e:Event) => modelValue[field.key] = (e.target as HTMLInputElement).value.trim()"
        />
        <Input.Password
          v-else-if="field.type === 'password'"
          v-model:value="modelValue[field.key]"
          autocomplete="new-password"
          :placeholder="field.placeholder"
          size="large"
          @blur="(e:Event) => modelValue[field.key] = (e.target as HTMLInputElement).value.trim()"
          v-bind="field.props"
          :iconRender="(visible: boolean) => h(RpaIcon, {
              name: visible ? 'password-eye' : 'password-eye-closed'
            })
          "
        />
        <PhoneCode
          v-else-if="field.type === 'captcha'"
          :ref="(el: any) => { if (el) codeInputRefs[field.key] = el }"
          v-model="modelValue[field.key]"
          :placeholder="field.placeholder"
          v-bind="field.props"
          :send-captcha="() => handleSendCaptcha(field)"
        />
        <Textarea
          v-else-if="field.type === 'textarea'"
          v-model:value="modelValue[field.key]"
          :placeholder="field.placeholder"
          @blur="(e:Event) => modelValue[field.key] = (e.target as HTMLInputElement).value.trim()"
          v-bind="field.props"
        />
        <Select
          v-else-if="field.type === 'select'"
          v-model:value="modelValue[field.key]"
          :placeholder="field.placeholder"
          v-bind="field.props"
          :options="field.options"
        />          
        <Checkbox
          v-else-if="field.type === 'checkbox'"
          v-model:checked="modelValue[field.key]"
          v-bind="field.props"
        >          
          <component 
            v-if="field.customRender" 
            :is="field.customRender({
              field,
              value: modelValue[field.key],
              formData: modelValue,
              validate: async () => {
                try {
                  await validateFields([field.key])
                  return true
                } catch {
                  return false
                }
              },
              handleEvents,
              loading
            })" 
          />
        </Checkbox>
        <template v-else-if="field.type === 'slot'">
          <component 
            v-if="field.customRender" 
            :is="field.customRender({
              field,
              value: modelValue[field.key],
              formData: modelValue,
              validate: async () => {
                try {
                  await validateFields([field.key])
                  return true
                } catch {
                  return false
                }
              },
              handleEvents,
              loading
            })" 
          />
        </template>
      </Form.Item>
    </template>

    <slot name="actions">
      <component
        v-if="config.actionsRender"
        :is="() => config.actionsRender!({
          formData: modelValue,
          validate: async () => {
            try {
              await validateFields()
              return true
            } catch {
              return false
            }
          },
          handleEvents,
          loading,
        })"
      />
    </slot>
  </Form>
</template>

<style scoped>
.dynamic-form {
  width: 100%;
}

:deep(.ant-input-number) {
  width: 100%;
}
</style>