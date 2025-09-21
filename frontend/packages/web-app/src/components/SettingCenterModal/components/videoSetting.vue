<script setup lang="ts">
import { Form, InputNumber, Radio, Select, Switch } from 'ant-design-vue'

import { videoRunOption, videoTimeOption } from '../config'
import { useVideoConfig } from '../hooks/useVideoSetting'

import Card from './card.vue'

const { isEnable, videoRef, videoForm, handleOpenFile, handleSwitchChange } = useVideoConfig()
</script>

<template>
  <Card
    title="是否启用"
    description="视频形式记录机器人运行过程"
    class="h-[84px] px-[20px] py-[17px]"
  >
    <template #suffix>
      <Switch v-model:checked="isEnable" @change="handleSwitchChange" />
    </template>
  </Card>
  <Form
    v-if="isEnable"
    ref="videoRef"
    :model="videoForm"
    label-align="left"
    :colon="false"
  >
    <div class="space-y-6 py-6 px-5">
      <div class="flex items-center">
        自动录制机器人
        <Select
          v-model:value="videoForm.scene"
          class="w-[120px] mx-2"
          :options="videoRunOption"
        />
        时保存
        <Select
          v-model:value="videoForm.cutTime"
          class="w-[120px] mx-2"
          :options="videoTimeOption"
        />
        的视频
      </div>
      <div class="flex items-center">
        视频文件
        <Radio.Group v-model:value="videoForm.saveType" class="mx-2">
          <Radio :value="false">
            永久保存
          </Radio>
          <Radio :value="true">
            <div class="inline-flex items-center">
              生成
              <InputNumber
                v-model:value="videoForm.fileClearTime"
                class="mx-2"
                :min="1"
                :max="365"
              />
              天后，自动清除
            </div>
          </Radio>
        </Radio.Group>
      </div>
      <div class="flex items-center">
        视频文件保存地址
        <a-input-search
          v-model:value="videoForm.filePath"
          class="w-[328px] mx-2"
          enter-button="选择"
          @search="handleOpenFile"
        />
      </div>
    </div>
  </Form>
</template>
