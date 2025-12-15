<script setup lang="ts">
import { RichTextPreview } from '@rpa/components'
import { TypographyLink } from 'ant-design-vue'
import { computed } from 'vue'

import { getBaseURL } from '@/api/http/env'

export interface InfoInterface {
  robotName: string
  versionNum: number
  filePath: string
  fileName: string
  introduction: string
  useDescription: string
  videoName?: string
  videoPath?: string
}

const props = defineProps<{ data: InfoInterface }>()

const filePath = computed(() => new URL(`${props.data.filePath}`, getBaseURL()).toString())
</script>

<template>
  <section class="px-6 py-5 rounded-xl bg-[#000000]/[.03] dark:bg-[#FFFFFF]/[.03]">
    <div class="inline-flex items-center gap-[6px] font-semibold mb-4">
      <div class="inline-block w-[2px] h-[12px] bg-primary" />
      <span>{{ $t('basicInformation') }}</span>
    </div>
    <a-descriptions
      layout="vertical"
      size="middle"
      :colon="false"
    >
      <a-descriptions-item :label="$t('projectName')" :span="1">
        {{ data.robotName }}
      </a-descriptions-item>
      <a-descriptions-item :label="$t('common.versionNumber')" :span="1">
        v{{ data.versionNum }}
      </a-descriptions-item>
      <a-descriptions-item :label="$t('attachmentDownload')" :span="1">
        <TypographyLink v-if="filePath && data.fileName" :href="filePath" target="_blank">
          <div class="flex">
            <rpa-icon name="paper-clip-outlined" size="22" class="relative mt-[2px] mr-2 text-text-tertiary" />
            <span>{{ data.fileName }}</span>
          </div>
        </TypographyLink>
        <span v-else>--</span>
      </a-descriptions-item>
      <a-descriptions-item :label="$t('common.intro')" :span="3">
        <a-tooltip :title="data.introduction || $t('noDescription')" class="text-[12px] line-clamp-2 text-ellipsis" placement="topLeft">
          {{ data.introduction || $t('noDescription') }}
        </a-tooltip>
      </a-descriptions-item>
      <a-descriptions-item v-if="data.videoPath" :label="$t('videoDirection')" :span="3">
        <video :src="data.videoPath" loop controls class="w-full" />
      </a-descriptions-item>
      <a-descriptions-item :label="$t('useDirection')" :span="3">
        <RichTextPreview :content="data.useDescription || $t('noDescription-1')" class="text-[12px]" />
      </a-descriptions-item>
    </a-descriptions>
  </section>
</template>

<style lang="scss" scoped>
:deep(.ant-descriptions-item-label) {
  font-size: 12px;
  color: var(--color-text-secondary);
}

:deep(.ant-descriptions-item-content) {
  font-size: 12px;
}
</style>
