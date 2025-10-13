<script setup lang="ts">
import { RichTextPreview } from '@rpa/components'
import { useDark } from '@vueuse/core'
import { Badge, Drawer, Timeline, TypographyLink } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed } from 'vue'

// import AppFileDownload from '@/views/Home/components/TeamMarket/AppFileDownload.vue'
import { getBaseURL } from '@/api/http/env'
import Avatar from '@/components/Avatar/Avatar.vue'
import { useAppDetail } from '@/views/Home/components/TeamMarket/hooks/useAppDetail'

import type { cardAppItem } from '../../types/market'

const { appData } = defineProps({
  appData: {
    type: Object as () => cardAppItem,
  },
})
const emit = defineEmits(['close'])

const isDark = useDark()
const { t } = useTranslation()
const appDetail = useAppDetail({ marketId: appData.marketId, appId: appData.appId })

function handleCancel() {
  emit('close', appDetail.value)
}

const filePath = computed(() =>
  new URL(`${appDetail.value.filePath}`, getBaseURL()).toString(),
)

const videoPath = computed(() =>
  new URL(`${appDetail.value.videoPath}`, getBaseURL()).toString(),
)
</script>

<template>
  <Drawer
    class="appDetailDrawer"
    :open="true"
    :width="560"
    :title="t('applicationDetails')"
    :footer="null"
    @close="handleCancel"
  >
    <div class="flex flex-col gap-4" :class="{ dark: isDark }">
      <section class="panel flex gap-4">
        <Avatar :robot-name="appDetail.appName" :icon="appDetail.icon" :color="appDetail.color" />
        <div class="flex flex-col gap-2">
          <span class="text-[16px] font-medium">{{ appDetail.appName }}</span>
          <div class="flex gap-4">
            <div class="flex items-center gap-[6px] text-[#000000]/[.45] dark:text-[#FFFFFF]/[.45]">
              <rpa-icon name="eye" size="16" />
              <span class="text-[12px]">{{ appDetail.checkNum }}</span>
            </div>
            <div class="flex items-center gap-[6px] text-[#000000]/[.45] dark:text-[#FFFFFF]/[.45]">
              <rpa-icon name="download" size="16" />
              <span class="text-[12px]">{{ appDetail.downloadNum }}</span>
            </div>
          </div>
          <a-tooltip :title="appDetail.introduction || t('noDescription')" class="text-[12px] line-clamp-2 text-ellipsis" placement="topLeft">
            {{ appDetail.introduction || t('noDescription') }}
          </a-tooltip>
        </div>
      </section>

      <section class="panel">
        <div class="subtitle mb-4">
          基本信息
        </div>
        <a-descriptions
          layout="vertical"
          size="middle"
          :column="6"
          :colon="false"
          :label-style="{
            fontSize: '12px',
            color: isDark ? 'rgba(255, 255, 255, 0.65)' : 'rgba(0, 0, 0, 0.65)',
          }"
        >
          <a-descriptions-item label="创建者" :span="filePath && appDetail.fileName ? 2 : 3">
            {{ appDetail.creatorName }}
          </a-descriptions-item>
          <a-descriptions-item label="分类" :span="filePath && appDetail.fileName ? 2 : 3">
            {{ appDetail.category }}
          </a-descriptions-item>
          <a-descriptions-item v-if="filePath && appDetail.fileName" label="附件下载" :span="filePath && appDetail.fileName ? 2 : 3">
            <TypographyLink :href="filePath" target="_blank">
              <div class="flex">
                <rpa-icon name="paper-clip-outlined" size="22" class="relative mt-[2px] mr-2 text-[#000000]/[.45] dark:text-[#FFFFFF]/[.45]" />
                <span>{{ appDetail.fileName }}</span>
              </div>
            </TypographyLink>
          </a-descriptions-item>
          <a-descriptions-item v-if="appDetail.videoPath" label="视频说明" :span="6">
            <video controls>
              <source :src="videoPath" type="video/mp4">
              您的浏览器不支持 video 标签。
            </video>
          </a-descriptions-item>
          <a-descriptions-item label="使用说明" :span="6">
            <RichTextPreview :content="appDetail.useDescription || '暂无使用说明'" class="text-[12px]" />
          </a-descriptions-item>
        </a-descriptions>
      </section>

      <section class="panel !pb-0">
        <div class="subtitle mb-4">
          版本记录
        </div>
        <Timeline progress-dot size="small" direction="vertical">
          <Timeline.Item v-for="item in appDetail.versionInfoList" :key="item.versionNum">
            <div slot="title" class="ctitle">
              <div class="leftLabel font-medium">
                <span class="mr-5">版本{{ item.versionNum }}</span>
                <span class="mr-5">{{ item.createTime }}</span>
                <Badge v-if="item.online === 1" status="success" text="当前启用版本" />
              </div>
              <div class="description text-[#000000]/[.65] dark:text-[#FFFFFF]/[.65]">
                <a-tooltip :title="item.updateLog">
                  {{ item.updateLog || '暂无更新日志' }}
                </a-tooltip>
              </div>
            </div>
          </Timeline.Item>
        </Timeline>
      </section>
    </div>
  </Drawer>
</template>

<style lang="scss" scoped>
.panel {
  padding: 20px 24px;
  border-radius: 12px;
  background-color: rgba(#000000, 0.03);
}

.dark .panel {
  background-color: rgba(#ffffff, 0.03);
}

.subtitle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;

  &::before {
    content: '';
    display: inline-block;
    width: 2px;
    height: 12px;
    background-color: $color-primary;
  }
}
</style>
