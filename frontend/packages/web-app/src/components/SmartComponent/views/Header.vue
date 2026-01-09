<script lang="ts" setup>
import { useRouteBack } from '@/hooks/useCommonRoute'

import { useSmartComp } from '../hooks'

const emit = defineEmits<{
  (evt: 'open-version-manage', e: boolean)
}>()

const { editingSmartComp, saveSmartComp } = useSmartComp()

async function handleConfirm() {
  if (editingSmartComp.value) {
    await saveSmartComp()
  }
  useRouteBack()
}
</script>

<template>
  <div class="h-[58px] flex justify-between items-center px-4 py-2 bg-[#FFFFFF] dark:bg-[#FFFFFF]/[.08] rounded-lg">
    <section class="flex items-center gap-2">
      <rpa-hint-icon name="chevron-left" enable-hover-bg @click="useRouteBack()" />
      <rpa-icon name="magic-wand" size="20" class="text-primary" />
      <div class="flex flex-col">
        <span class="font-medium">{{ editingSmartComp?.title || '智能组件' }}</span>
        <span v-if="editingSmartComp" class="text-[12px] text-text-tertiary">组件由 AI 生成</span>
      </div>
      <a-tooltip v-if="editingSmartComp?.comment" :title="editingSmartComp?.comment">
        <rpa-icon name="info" size="16" class="text-text-secondary" />
      </a-tooltip>
    </section>

    <section class="flex items-center gap-2">
      <rpa-hint-icon name="git-fork" enable-hover-bg @click="emit('open-version-manage', true)">
        <template #suffix>
          <span class="ml-2">版本管理</span>
        </template>
      </rpa-hint-icon>
      <a-divider type="vertical" class="h-4 border-s-[#000000]/[.16] dark:border-s-[#FFFFFF]/[.16]" />
      <a-button @click="useRouteBack()">
        取消
      </a-button>
      <a-button type="primary" @click="handleConfirm()">
        确定
      </a-button>
    </section>
  </div>
</template>
