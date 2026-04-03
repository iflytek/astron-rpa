<script setup lang="ts">
import { Form, InputNumber, Radio, Select, Switch } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed } from 'vue'

import { videoRunOption, videoTimeOption } from '../config'
import { useVideoConfig } from '../hooks/useVideoSetting'

import Card from './card.vue'

const { isEnable, videoRef, videoForm, handleOpenFile, handleSwitchChange } = useVideoConfig()
const { t } = useTranslation()

const runOptions = computed(() => videoRunOption.map(i => ({ ...i, label: t(i.label) })))
const timeOptions = computed(() => videoTimeOption.map(i => ({ ...i, label: t(i.label) })))
</script>

<template>
  <Card
    :title="$t('settingCenter.runRecord.enable')"
    :description="$t('settingCenter.runRecord.subtitle')"
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
        {{ $t('settingCenter.runRecord.autoRecord') }}
        <Select
          v-model:value="videoForm.scene"
          class="w-[120px] mx-2"
          :options="runOptions"
        />
        {{ $t('saveAtTime') }}
        <Select
          v-model:value="videoForm.cutTime"
          class="w-[120px] mx-2"
          :options="timeOptions"
        />
        {{ $t('videoSuffix') }}
      </div>
      <div class="flex items-center">
        {{ $t('videoFile') }}
        <Radio.Group v-model:value="videoForm.saveType" class="mx-2">
          <Radio :value="false">
            {{ $t('saveForever') }}
          </Radio>
          <Radio :value="true">
            <div class="inline-flex items-center">
              {{ $t('generate') }}
              <InputNumber
                v-model:value="videoForm.fileClearTime"
                class="mx-2"
                :min="1"
                :max="365"
              />
              {{ $t('autoDeleteAfterNDays') }}
            </div>
          </Radio>
        </Radio.Group>
      </div>
      <div class="flex items-center">
        {{ $t('videoFilePath') }}
        <a-input-search
          v-model:value="videoForm.filePath"
          class="w-[328px] mx-2"
          :enter-button="$t('choose')"
          @search="handleOpenFile"
        />
      </div>
    </div>
  </Form>
</template>
