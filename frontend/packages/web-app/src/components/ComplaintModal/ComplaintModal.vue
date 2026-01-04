<script lang="ts" setup>
import { NiceModal } from '@rpa/components'
import { createReusableTemplate } from '@vueuse/core'
import type { UploadFile, UploadProps } from 'ant-design-vue'
import { message, Upload } from 'ant-design-vue'
import type { Rule } from 'ant-design-vue/es/form'
import to from 'await-to-js'
import { isEmpty } from 'lodash-es'
import { computed, reactive, ref } from 'vue'

import { aiFeedback } from '@/api/common'
import { uploadFile } from '@/api/resource'
import { useUserStore } from '@/stores/useUserStore'

const modal = NiceModal.useModal()
const { userNameState } = useUserStore()

interface ICheckboxOption {
  label: string
  tooltip: string
}

interface IFormData {
  contentSafety: string[]
  functionalDefect: string[]
  description: string
  attachments: UploadFile[]
}

// 内容安全类
const CONTENT_OPTIONS: ICheckboxOption[] = [
  {
    label: '生成违法/违规信息',
    tooltip: '包括但不限于政治敏感、暴力、色情等违反法律法规的内容',
  },
  {
    label: '生成歧视/偏见内容',
    tooltip: '基于种族、性别、宗教等的歧视性言论',
  },
  {
    label: '生成不道德/有害建议',
    tooltip: '可能导致人身伤害或财产损失的建议',
  },
  {
    label: '侵犯他人知识产权',
    tooltip: '未经授权使用他人的文字、代码等',
  },
]

// 功能缺陷类
const DEFECT_OPTIONS: ICheckboxOption[] = [
  {
    label: '生成流程代码错误，无法执行',
    tooltip: '生成的代码存在语法错误或逻辑错误，无法正常运行',
  },
  {
    label: '理解指令有误，答非所问',
    tooltip: '未能正确理解用户的问题或指令，回答内容与问题无关',
  },
  {
    label: '生成结果不完整或逻辑混乱',
    tooltip: '回答内容不完整，或存在逻辑矛盾',
  },
  {
    label: '性能问题（响应过慢、超时）',
    tooltip: '响应时间超过20秒，或出现超时错误',
  },
]

const [DefineTemplate, ReuseTemplate] = createReusableTemplate<{ options: ICheckboxOption[] }>()

const formRef = ref()

const formData = reactive<IFormData>({
  contentSafety: [],
  functionalDefect: [],
  description: '',
  attachments: [],
})

const rules = computed<Record<string, Rule[]>>(() => {
  const categories = [...formData.contentSafety, ...formData.functionalDefect]

  const validateCategorie = async () => {
    const values = [...formData.contentSafety, ...formData.functionalDefect]
    return isEmpty(values) ? Promise.reject(new Error('请选择问题类型')) : Promise.resolve()
  }

  return {
    description: [{ required: true }],
    contentSafety: [{ required: isEmpty(categories) || !isEmpty(formData.contentSafety), validator: validateCategorie }],
    functionalDefect: [{ required: isEmpty(categories) || !isEmpty(formData.functionalDefect), validator: validateCategorie }],
  }
})

const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const maxSize = 5 * 1024 * 1024 // 5MB
  if (file.size > maxSize) {
    message.error('文件大小不能超过 5MB')
    // 返回 Upload.LIST_IGNORE 来阻止文件被添加到列表
    return Upload.LIST_IGNORE
  }
  // 返回 false 阻止自动上传，但允许文件添加到列表（手动上传）
  return false
}

async function handleSubmit() {
  await formRef.value.validate()

  // 上传附件
  const imageIds = await Promise.all(formData.attachments.map(async (item) => {
    // 避免重复提交
    if (item.status === 'success') {
      return item.response as string
    }

    item.status = 'uploading'
    const [error, fileId] = await to(uploadFile(
      { file: item.originFileObj },
      {
        onUploadProgress: (event) => {
          item.percent = Math.round((event.loaded * 100) / event.total)
        },
      },
    ))
    item.status = error ? 'error' : 'success'
    item.response = fileId

    return fileId
  }))

  // 判断所有文件是否全部上传
  const widthErrorFile = formData.attachments.some(item => item.status !== 'success')
  if (widthErrorFile) {
    return
  }

  const [error] = await to(aiFeedback({
    username: userNameState.state,
    categories: JSON.stringify({
      内容安全类: formData.contentSafety,
      功能缺陷类: formData.functionalDefect,
    }),
    description: formData.description,
    imageIds: imageIds.filter(Boolean),
  }))

  error ? message.error('提交失败，请稍后重试') : message.success('举报已受理，感谢您的反馈')
}
</script>

<template>
  <a-modal v-bind="NiceModal.antdModal(modal)" title="举报AI生成内容" width="600px" @ok="handleSubmit">
    <div class="text-text-secondary mb-4">
      请选择问题类型并描述具体情况
    </div>

    <a-divider />

    <DefineTemplate v-slot="{ options }">
      <div v-for="item in options" :key="item.label" class="flex items-center">
        <a-checkbox :value="item.label">
          {{ item.label }}
        </a-checkbox>
        <a-tooltip :title="item.tooltip">
          <rpa-icon name="atom-form-tip" />
        </a-tooltip>
      </div>
    </DefineTemplate>

    <a-form ref="formRef" layout="vertical" :model="formData" :rules="rules">
      <a-form-item label="内容安全类" name="contentSafety">
        <a-checkbox-group v-model:value="formData.contentSafety" class="grid grid-cols-2 gap-3">
          <ReuseTemplate :options="CONTENT_OPTIONS" />
        </a-checkbox-group>
      </a-form-item>
      <a-form-item label="功能缺陷类" name="functionalDefect">
        <a-checkbox-group v-model:value="formData.functionalDefect" class="grid grid-cols-2 gap-3">
          <ReuseTemplate :options="DEFECT_OPTIONS" />
        </a-checkbox-group>
      </a-form-item>
      <a-form-item label="问题描述" name="description">
        <a-textarea
          v-model:value="formData.description"
          :rows="4"
          :maxlength="500"
          show-count
          placeholder="请具体描述问题（如生成的内容情况、问题发生场景）"
        />
      </a-form-item>
      <a-form-item>
        <a-upload
          v-model:file-list="formData.attachments" accept="image/*" :before-upload="beforeUpload" :max-count="3"
          multiple
        >
          <a-button class="text-xs">
            上传图片附件
          </a-button>
        </a-upload>
      </a-form-item>
    </a-form>
  </a-modal>
</template>
