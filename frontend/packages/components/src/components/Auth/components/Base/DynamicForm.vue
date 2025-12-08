<script setup lang="ts" >
import { ref } from 'vue'
import { Form, Input, Checkbox, Select, Textarea } from 'ant-design-vue'
import type { FormInstance } from 'ant-design-vue'
import type { FieldSchema } from '../../schemas/factories.tsx'
import PhoneCode from './PhoneCode.vue'
import type { FormConfig } from '../../schemas/factories.tsx'

interface Props<T = any> {
  config: FormConfig
  modelValue?: T
  emitEvent?: (event: string, ...args: any[]) => void
}

const {modelValue, config, emitEvent} = withDefaults(defineProps<Props>(), { })

const emit = defineEmits<{
  submit: [value: any]
  sendCode: [phone: string]
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
  // 重置所有验证码组件
  Object.values(codeInputRefs.value).forEach(ref => {
    ref?.resetForm()
  })
}

const handleSendCode = (field: FieldSchema, phone: string) => {
  emit('sendCode', phone)
}

defineExpose({
  formRef,
  resetFields,
  validateFields,
})
</script>

<template>  
  <Form
    ref="formRef"
    :model="modelValue"
    :layout="config.layout || 'vertical'"
    :label-col="config.labelCol || 0"
    :wrapper-col="config.wrapperCol || 24"
    class="dynamic-form relative"
  >
    <template v-for="field in config.fields" :key="field.key">
      <Form.Item
        :name="field.key"
        :rules="field.rules"
      >      
        <Input
          v-if="field.type === 'input'"
          v-model:value="modelValue[field.key]"
          :placeholder="field.placeholder"
          autocomplete="new-password"
          size="large"
          v-bind="field.props"
        />
        <Input.Password
          v-else-if="field.type === 'password'"
          v-model:value="modelValue[field.key]"
          autocomplete="new-password"
          :placeholder="field.placeholder"
          size="large"
          v-bind="field.props"
        />
        <PhoneCode
          v-else-if="field.type === 'code'"
          :ref="(el: InstanceType<typeof PhoneCode>) => { if (el) codeInputRefs[field.key] = el }"
          v-model="modelValue[field.key]"
          :phone="modelValue.phone"
          :placeholder="field.placeholder"
          v-bind="field.props"
          @send="(phone: string) => handleSendCode(field, phone)"
        />
        <Textarea
          v-else-if="field.type === 'textarea'"
          v-model:value="modelValue[field.key]"
          :placeholder="field.placeholder"
          v-bind="field.props"
        />
        <Select
          v-else-if="field.type === 'select'"
          v-model:value="modelValue[field.key]"
          :placeholder="field.placeholder"
          v-bind="field.props"
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
              emit: emitEvent
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
              emit: emitEvent
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
          emit: emitEvent
        })"
      />
    </slot>
  </Form>
</template>

<style scoped>
.dynamic-form {
  width: 100%;
}

:deep(.ant-form-item) {
  margin-bottom: 16px;
}

:deep(.ant-input-number) {
  width: 100%;
}
</style>