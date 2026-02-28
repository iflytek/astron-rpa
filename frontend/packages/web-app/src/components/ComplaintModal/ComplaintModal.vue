<script lang="ts" setup>
import { NiceModal } from '@rpa/components'
import { createReusableTemplate } from '@vueuse/core'
import type { UploadFile, UploadProps } from 'ant-design-vue'
import { message, Upload } from 'ant-design-vue'
import type { Rule } from 'ant-design-vue/es/form'
import to from 'await-to-js'
import { useTranslation } from 'i18next-vue'
import { isEmpty } from 'lodash-es'
import { computed, reactive, ref } from 'vue'

import { aiFeedback } from '@/api/common'
import { uploadFile } from '@/api/resource'
import { useUserStore } from '@/stores/useUserStore'

const modal = NiceModal.useModal()
const { t } = useTranslation()

interface ICheckboxOption {
  key: string
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
    key: 'illegal',
  },
  {
    key: 'discrimination',
  },
  {
    key: 'harmfulAdvice',
  },
  {
    key: 'ipInfringement',
  },
]

// 功能缺陷类
const DEFECT_OPTIONS: ICheckboxOption[] = [
  {
    key: 'codeError',
  },
  {
    key: 'misunderstood',
  },
  {
    key: 'incomplete',
  },
  {
    key: 'performance',
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
    return isEmpty(values) ? Promise.reject(new Error(t('complaintModal.selectIssueType'))) : Promise.resolve()
  }

  return {
    description: [{ required: true, message: t('complaintModal.enterIssueDescription') }],
    contentSafety: [{ required: isEmpty(categories) || !isEmpty(formData.contentSafety), validator: validateCategorie }],
    functionalDefect: [{ required: isEmpty(categories) || !isEmpty(formData.functionalDefect), validator: validateCategorie }],
  }
})

const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  if (!file.type.startsWith('image/')) {
    message.error(t('complaintModal.onlyImageAllowed'))
    return Upload.LIST_IGNORE
  }

  const maxSize = 5 * 1024 * 1024 // 5MB
  if (file.size > maxSize) {
    message.error(t('complaintModal.fileTooLarge', { size: 5 }))
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
    username: useUserStore().currentUserInfo?.name || useUserStore().currentUserInfo?.loginName,
    categories: JSON.stringify({
      内容安全类: formData.contentSafety,
      功能缺陷类: formData.functionalDefect,
    }),
    description: formData.description,
    imageIds: imageIds.filter(Boolean),
  }))

  if (error) {
    message.error(t('complaintModal.submitFailed'))
  }
  else {
    message.success(t('complaintModal.submitSuccess'))
    modal.hide()
  }
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :title="t('complaintModal.title')"
    :ok-text="t('submit')"
    :cancel-text="t('cancel')"
    width="600px"
    @ok="handleSubmit"
  >
    <div class="text-text-secondary mb-4">
      {{ t('complaintModal.subtitle') }}
    </div>

    <a-divider />

    <DefineTemplate v-slot="{ options }">
      <div v-for="item in options" :key="item.key" class="flex items-center">
        <a-checkbox :value="item.key">
          {{ t(`complaintModal.options.${item.key}.label`) }}
        </a-checkbox>
        <a-tooltip :title="t(`complaintModal.options.${item.key}.tooltip`)">
          <rpa-icon name="atom-form-tip" />
        </a-tooltip>
      </div>
    </DefineTemplate>

    <a-form ref="formRef" layout="vertical" :model="formData" :rules="rules" class="max-h-[60vh] overflow-y-auto">
      <a-form-item :label="t('complaintModal.contentSafety')" name="contentSafety">
        <a-checkbox-group v-model:value="formData.contentSafety" class="grid grid-cols-2 gap-3">
          <ReuseTemplate :options="CONTENT_OPTIONS" />
        </a-checkbox-group>
      </a-form-item>
      <a-form-item :label="t('complaintModal.functionalDefect')" name="functionalDefect">
        <a-checkbox-group v-model:value="formData.functionalDefect" class="grid grid-cols-2 gap-3">
          <ReuseTemplate :options="DEFECT_OPTIONS" />
        </a-checkbox-group>
      </a-form-item>
      <a-form-item :label="t('complaintModal.issueDescription')" name="description">
        <a-textarea
          v-model:value="formData.description"
          :rows="4"
          :maxlength="500"
          show-count
          :placeholder="t('complaintModal.issueDescriptionPlaceholder')"
        />
      </a-form-item>
      <a-form-item>
        <a-upload
          v-model:file-list="formData.attachments"
          accept="image/*"
          :before-upload="beforeUpload"
          :max-count="3"
          multiple
          list-type="picture"
        >
          <a-button class="text-xs">
            {{ t('complaintModal.uploadImageAttachments') }}
          </a-button>
        </a-upload>
      </a-form-item>
    </a-form>
  </a-modal>
</template>
