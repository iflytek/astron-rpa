<script setup lang="ts">
import { Checkbox, Form, Input, Select, Textarea } from 'ant-design-vue'
import type { FormInstance } from 'ant-design-vue'
import { h, ref } from 'vue'

import { Icon as RpaIcon } from '../../../Icon'
import type { FormConfig } from '../../schemas/factories.tsx'

import PhoneCode from './PhoneCode.vue'

interface Props<T = any> {
  config: FormConfig
  modelValue?: T
  loading?: boolean
  handleEvents?: (event: string, ...args: any[]) => void
}

const { modelValue, loading, config, handleEvents } = defineProps<Props>()

const formRef = ref<FormInstance>()
const codeInputRefs = ref<Record<string, InstanceType<typeof PhoneCode>>>({})

async function validateFields(fieldNames?: string[]) {
  if (fieldNames && fieldNames.length > 0) {
    await formRef.value?.validateFields(fieldNames)
    return true
  }
  else {
    await formRef.value?.validate()
    return true
  }
}

// 重置表单
function resetFields() {
  formRef.value?.resetFields()
  Object.values(codeInputRefs.value).forEach((ref) => {
    ref?.resetForm()
  })
}

function clearValidates() {
  formRef.value?.clearValidate()
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
          v-bind="field.props"
          :icon-render="(visible: boolean) => h(RpaIcon, {
            name: visible ? 'password-eye' : 'password-eye-closed',
          })
          "
          @blur="(e:Event) => modelValue[field.key] = (e.target as HTMLInputElement).value.trim()"
        />
        <PhoneCode
          v-else-if="field.type === 'captcha'"
          :ref="(el: any) => { if (el) codeInputRefs[field.key] = el }"
          v-model="modelValue[field.key]"
          :placeholder="field.placeholder"
          :wrap-ref="formRef"
          :relation-key="field.relationKey"
          :send-captcha="field.sendCaptcha"
          v-bind="field.props"
        />
        <Textarea
          v-else-if="field.type === 'textarea'"
          v-model:value="modelValue[field.key]"
          :placeholder="field.placeholder"
          v-bind="field.props"
          @blur="(e:Event) => modelValue[field.key] = (e.target as HTMLInputElement).value.trim()"
        />
        <Select
          v-else-if="field.type === 'select'"
          v-model:value="modelValue[field.key]"
          :placeholder="field.placeholder"
          v-bind="field.props"
          :options="field.options"
          :get-popup-container="(triggerNode) => triggerNode.parentNode"
        />
        <Checkbox
          v-else-if="field.type === 'checkbox'"
          v-model:checked="modelValue[field.key]"
          v-bind="field.props"
        >
          <component
            :is="field.customRender({
              field,
              value: modelValue[field.key],
              formData: modelValue,
              validate: async () => {
                try {
                  await validateFields([field.key])
                  return true
                }
                catch {
                  return false
                }
              },
              handleEvents,
              loading,
            })"
            v-if="field.customRender"
          />
        </Checkbox>
        <template v-else-if="field.type === 'slot'">
          <component
            :is="field.customRender({
              field,
              value: modelValue[field.key],
              formData: modelValue,
              validate: async () => {
                try {
                  await validateFields([field.key])
                  return true
                }
                catch {
                  return false
                }
              },
              handleEvents,
              loading,
            })"
            v-if="field.customRender"
          />
        </template>
      </Form.Item>
    </template>

    <slot name="actions">
      <component
        :is="() => config.actionsRender!({
          formData: modelValue,
          validate: async () => {
            try {
              await validateFields()
              return true
            }
            catch {
              return false
            }
          },
          handleEvents,
          loading,
        })"
        v-if="config.actionsRender"
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
