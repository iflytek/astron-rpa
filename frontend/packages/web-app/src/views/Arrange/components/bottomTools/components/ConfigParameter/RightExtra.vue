<script lang="ts" setup>
import { useAsyncState } from '@vueuse/core'
import { Input } from 'ant-design-vue'

import { useProcessStore } from '@/stores/useProcessStore.ts'

import { injectConfigParameter } from './useConfigParameter.ts'

const { searchText, isQuoted, findQuoted, toggleQuoted } = injectConfigParameter()
const processStore = useProcessStore()

const { isLoading, execute } = useAsyncState(processStore.createParameter, undefined, { immediate: false })
</script>

<template>
  <template v-if="isQuoted">
    <div class="flex items-center h-[32px] px-[20px] bg-[#000000]/[.03] dark:bg-[#FFFFFF]/[.03] rounded-[6px]">
      <span class="text-[12px] select-none">查找引用</span>
      <a-divider type="vertical" class="h-4 border-s-[#000000]/[.16] dark:border-s-[#FFFFFF]/[.16]" />
      <rpa-hint-icon name="chevron-left" class="text-[12px]" @click="() => toggleQuoted(false)">
        <template #suffix>
          <span class="ml-1">返回</span>
        </template>
      </rpa-hint-icon>
      <rpa-hint-icon name="refresh-current-page" class="ml-[20px] text-[12px]" @click="findQuoted()">
        <template #suffix>
          <span class="ml-1">刷新列表</span>
        </template>
      </rpa-hint-icon>
    </div>
  </template>
  <template v-else>
    <rpa-hint-icon
      name="python-package-plus"
      :disabled="isLoading"
      class="text-[12px]"
      enable-hover-bg
      @click="execute()"
    >
      <template #suffix>
        <span class="ml-1">新增参数</span>
      </template>
    </rpa-hint-icon>
    <Input
      v-model:value="searchText"
      placeholder="搜索参数"
      class="text-xs ml-2 h-6 w-[180px]"
    >
      <template #suffix>
        <rpa-icon name="search" />
      </template>
    </Input>
  </template>
</template>

<style lang="scss" scoped>
:deep(.ant-input) {
  background-color: transparent;
}
</style>
