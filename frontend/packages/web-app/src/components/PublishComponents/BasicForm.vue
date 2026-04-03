<script setup lang="ts">
import { Col, Divider, Form, Input, Row, Textarea } from 'ant-design-vue'
import type { Rule } from 'ant-design-vue/es/form'
import { useTranslation } from 'i18next-vue'
import { computed, ref } from 'vue'

import { uploadVideoFile } from '@/api/resource'
import { checkRobotName } from '@/api/robot'
import type { Attachment } from '@/components/AttachmentUpload/index.vue'
import AttachmentUpload from '@/components/AttachmentUpload/index.vue'
import RobotAvatarSelect from '@/components/Avatar/RobotAvatarSelect.vue'
import RichTextEditor from '@/components/RichTextEditor/index.vue'

import type { FormState } from './utils'

const props = defineProps({
  robotId: {
    type: String,
    required: true,
  },
})

const { t } = useTranslation()

async function validateName(_rule: Rule, value: string) {
  if (value) {
    const res = await checkRobotName({
      name: value,
      robotId: props.robotId,
    })

    return res.data ? Promise.reject(t('market.duplicateNameError')) : Promise.resolve()
  }

  return Promise.resolve()
}

function validateAttachment(_rule: Rule, value: Attachment[]) {
  if (value.find(it => it.status !== 'success')) {
    return Promise.reject(t('market.uploadSuccessFile'))
  }

  return Promise.resolve()
}

const formRef = ref()
const formState = defineModel<Partial<FormState>>()
const rules: Record<string, Rule[]> = {
  name: [
    { required: true, message: t('market.enterAppName') },
    { validator: validateName, trigger: 'blur' },
  ],
  appendix: [
    { validator: validateAttachment, trigger: 'blur' },
  ],
  video: [
    { validator: validateAttachment, trigger: 'blur' },
  ],
}

const validate = (): Promise<void> => formRef.value.validate()

defineExpose({ validate })

const isFirstVerison = computed(() => formState.value.version === 1)
</script>

<template>
  <Form
    ref="formRef"
    class="px-5"
    :model="formState"
    :rules="rules"
    label-align="right"
    layout="vertical"
    :colon="false"
  >
    <div class="flex flex-col">
      <div :class="isFirstVerison ? 'order-1' : 'order-3'">
        <div class="font-semibold text-[14px] leading-6 pb-3">
          {{ $t('basicInformation') }}
        </div>
        <div class="flex gap-6">
          <Form.Item>
            <RobotAvatarSelect
              v-model:icon="formState.icon"
              v-model:color="formState.color"
              :robot-name="formState.name"
            />
          </Form.Item>
          <Form.Item
            name="name"
            :label="$t('projectName')"
            class="flex-1"
            required
          >
            <Input v-model:value="formState.name" class="text-[12px]" />
          </Form.Item>
        </div>
        <Form.Item
          name="introduction"
          :label="$t('projectIntroduction')"
        >
          <Textarea
            v-model:value="formState.introduction"
            :placeholder="$t('common.enter')"
            :auto-size="{ minRows: 3 }"
            class="text-[12px]"
          />
        </Form.Item>

        <Form.Item
          name="useDescription"
          :label="$t('market.useDescription')"
        >
          <RichTextEditor
            v-model:value="formState.useDescription"
            :placeholder="$t('market.enterUseDescription')"
            class="text-[12px]"
          />
        </Form.Item>

        <Row class="h-[90px]">
          <Col :span="12">
            <Form.Item
              name="appendix"
              :label="$t('common.attachment')"
              :tooltip="$t('market.attachmentUploadTip')"
              :label-col="{ span: 6 }"
              :wrapper-col="{ span: 18 }"
            >
              <AttachmentUpload
                v-model:value="formState.appendix"
                :max-count="1"
                :max-size="50 * 1024"
              />
            </Form.Item>
          </Col>
          <Col :span="12">
            <Form.Item
              name="video"
              :label="$t('market.videoDescription')"
              :tooltip="$t('market.videoUploadTip')"
              :label-col="{ span: 8 }"
              :wrapper-col="{ span: 16 }"
            >
              <AttachmentUpload
                v-model:value="formState.video"
                :title="$t('market.uploadVideo')"
                :max-count="1"
                :max-size="200 * 1024"
                accept="video/*"
                :upload="uploadVideoFile"
              />
            </Form.Item>
          </Col>
        </Row>
      </div>

      <Divider class="order-2 bg-[rgba(0,0,0,0.10)] dark:bg-[rgba(255,255,255,0.16)] mb-[20px]" />

      <div :class="isFirstVerison ? 'order-3' : 'order-1'">
        <div class="font-semibold text-[14px] leading-6 pb-3">
          {{ $t('common.versionDescription') }}
        </div>
        <Form.Item name="version" class="currVersion">
          <template #label>
            {{ $t('currentVersion') }}：<span class="text-text">{{ $t('versionWithNumber', { version: formState.version }) }}</span>
          </template>
        </Form.Item>
        <Form.Item
          name="updateLog"
          :label="$t('common.updateLog')"
        >
          <Textarea
            v-model:value="formState.updateLog"
            :placeholder="$t('common.enter')"
            :auto-size="{ minRows: 3 }"
            class="text-[12px]"
          />
        </Form.Item>
      </div>
    </div>
  </Form>
</template>

<style lang="scss" scoped>
:deep(.ant-form-item) {
  margin-bottom: 12px;
}
.currVersion {
  :deep(.ant-form-item-control-input) {
    display: none;
  }
}

:deep(.ant-form-item-label > label) {
  color: $color-text-tertiary;
}
</style>
