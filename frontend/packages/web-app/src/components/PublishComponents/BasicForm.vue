<script setup lang="ts">
import { Col, Divider, Form, Input, Row, Textarea } from 'ant-design-vue'
import type { Rule } from 'ant-design-vue/es/form'
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

async function validateName(_rule: Rule, value: string) {
  if (value) {
    const res = await checkRobotName({
      name: value,
      robotId: props.robotId,
    })

    // eslint-disable-next-line prefer-promise-reject-errors
    return res.data ? Promise.reject('机器人名称已存在') : Promise.resolve()
  }

  return Promise.resolve()
}

function validateAttachment(_rule: Rule, value: Attachment[]) {
  if (value.find(it => it.status !== 'success')) {
    // eslint-disable-next-line prefer-promise-reject-errors
    return Promise.reject('请上传成功的文件')
  }

  return Promise.resolve()
}

const formRef = ref()
const formState = defineModel<Partial<FormState>>()
const rules: Record<string, Rule[]> = {
  name: [
    { required: true, message: '请输入机器人名称' },
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
          基本信息
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
            label="机器人名称"
            class="flex-1"
            required
          >
            <Input v-model:value="formState.name" class="text-[12px]" />
          </Form.Item>
        </div>
        <Form.Item
          name="introduction"
          label="机器人简介"
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
          label="使用说明"
        >
          <RichTextEditor
            v-model:value="formState.useDescription"
            placeholder="请输入使用说明..."
            class="text-[12px]"
          />
        </Form.Item>

        <Row class="h-[90px]">
          <Col :span="12">
            <Form.Item
              name="appendix"
              label="附件"
              tooltip="单次仅支持上传一个附件，大小不超过 50M"
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
              label="视频说明"
              tooltip="单次仅支持上传一个视频，大小不超过 200M，支持扩展名：mp4、mov、wmv、avi..."
              :label-col="{ span: 8 }"
              :wrapper-col="{ span: 16 }"
            >
              <AttachmentUpload
                v-model:value="formState.video"
                title="上传视频"
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
          版本说明
        </div>
        <Form.Item name="version" class="currVersion">
          <template #label>
            当前版本：<span class="text-text">版本{{ formState.version }}</span>
          </template>
        </Form.Item>
        <Form.Item
          name="updateLog"
          label="更新日志"
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
