<script setup lang="ts">
import { Timeline } from 'ant-design-vue'

defineProps<{
  sourceName?: string
  versionInfoList: any[]
  online?: number
}>()
</script>

<template>
  <section v-if="versionInfoList.length" class="px-6 py-5 pb-0 rounded-xl bg-[#000000]/[.03] dark:bg-[#FFFFFF]/[.03]">
    <div class="inline-flex items-center gap-[6px] font-semibold mb-4">
      <div class="inline-block w-[2px] h-[12px] bg-primary" />
      <span>源版本信息</span>
    </div>
    <div class="mb-5 text-[12px]">
      获取来源：{{ sourceName }}
    </div>
    <Timeline progress-dot size="small" direction="vertical">
      <Timeline.Item v-for="item in versionInfoList" :key="item.versionNum" :color="item.online === 1 ? 'blue' : 'grey'">
        <div class="flex items-center" :class="{ 'text-primary': item.online === 1 }">
          <span class="mr-5">版本{{ item.versionNum }}</span>
          <span class="mr-5">{{ item.createTime }}</span>
          <div v-if="item.online === 1" class="px-2 py-[2px] bg-[#5D59FF]/[.1] rounded text-[12px]">
            当前获取版本
          </div>
        </div>
      </Timeline.Item>
    </Timeline>
  </section>
</template>
