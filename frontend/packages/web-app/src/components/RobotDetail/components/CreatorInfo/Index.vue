<script setup lang="ts">
import dayjs from 'dayjs'

defineProps<{
  creatorName: string
  createTime: string
}>()
</script>

<template>
  <section class="px-6 py-5 rounded-xl bg-[#000000]/[.03] dark:bg-[#FFFFFF]/[.03]">
    <div class="inline-flex items-center gap-[6px] font-semibold mb-4">
      <div class="inline-block w-[2px] h-[12px] bg-primary" />
      <span>创建者信息</span>
    </div>
    <a-descriptions layout="vertical" size="middle" :colon="false">
      <a-descriptions-item label="创建者" :span="1">
        {{ creatorName }}
      </a-descriptions-item>
      <a-descriptions-item label="创建时间" :span="1">
        {{ dayjs(createTime).format("YYYY-MM-DD HH:mm:ss") }}
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
