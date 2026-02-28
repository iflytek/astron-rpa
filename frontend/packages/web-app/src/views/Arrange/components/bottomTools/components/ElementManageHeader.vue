<script lang="ts" setup>
import type { Ref } from 'vue'
import { inject } from 'vue'

import { useCvStore } from '@/stores/useCvStore.ts'

import { useGroupManager } from './hooks/useGroup'

type ElementType = 'common' | 'cv'

const { placeholder, elementType } = defineProps({
  placeholder: {
    type: String,
    default: '',
  },
  elementType: {
    type: String,
    validator: (value) => {
      return value === 'common' || value === 'cv'
    },
    default: 'common', // | 'cv'
  },
})

const collapsed = inject<Ref<boolean>>('collapsed')
const searchText = inject<Ref<string>>('searchText')
const moduleType = inject<Ref<string>>('moduleType')
const refresh = inject<Ref<boolean>>('refresh')
const unUseNum = inject<Ref<number>>('unUseNum')

const useGroup = useGroupManager()

function handleRefresh() {
  refresh.value = !refresh.value
}

function toggleCollapsed() {
  collapsed.value = !collapsed.value
}

function toggleModuleType(type: string) {
  moduleType.value = type
  if (moduleType.value === 'default')
    useCvStore().setQuotedItem()
}

function addGroup() {
  useGroup.addGroup(elementType as ElementType)
}
</script>

<template>
  <div class="text-[12px] flex justify-end items-center">
    <!-- 默认header -->
    <template v-if="moduleType === 'default'">
      <slot name="btns" />
      <a-input
        v-model:value="searchText"
        class="ml-2 w-[180px] h-[24px] text-[12px] rounded-[3px]"
        :placeholder="placeholder || (elementType === 'cv' ? $t('cvPick.searchImage') : $t('elementManager.searchElement'))"
      >
        <template #suffix>
          <rpa-icon name="search" />
        </template>
      </a-input>
      <rpa-hint-icon
        name="expand-bottom"
        :title="collapsed ? $t('common.collapseAll') : $t('common.expandAll')"
        class="ml-[12px]" :class="[collapsed ? 'rotate-180' : 'rotate-0']"
        enable-hover-bg
        @click="toggleCollapsed"
      />
      <a-dropdown class="cursor-pointer opacity-80">
        <template #overlay>
          <a-menu>
            <a-menu-item key="1" class="!text-[12px]" @click="addGroup">
              {{ $t('elementManager.createGroup') }}
            </a-menu-item>
            <a-menu-item key="2" class="!text-[12px]" @click="toggleModuleType('unuse')">
              {{ $t('viewUnusedElements') }}
            </a-menu-item>
          </a-menu>
        </template>
        <rpa-hint-icon name="app" enable-hover-bg class="ml-2" />
      </a-dropdown>
    </template>
    <!-- 查找引用、查看未使用 header -->
    <template v-else>
      <div class="flex items-center h-[32px] px-[20px] bg-[#000000]/[.03] dark:bg-[#FFFFFF]/[.03] rounded-[6px]">
        <span class="text-[12px] select-none">
          <template v-if="moduleType === 'unuse'">
            {{ $t('unusedElementsWithCount', { count: unUseNum }) }}
          </template>
          <template v-if="moduleType === 'quoted'">
            {{ $t('searchReference') }}
          </template>
        </span>
        <a-divider type="vertical" class="h-4 border-s-[#000000]/[.16] dark:border-s-[#FFFFFF]/[.16]" />
        <rpa-hint-icon name="chevron-left" class="text-[12px]" @click="toggleModuleType('default')">
          <template #suffix>
            <span class="ml-1">{{ $t('goBack') }}</span>
          </template>
        </rpa-hint-icon>
        <rpa-hint-icon name="refresh-current-page" class="ml-[20px] text-[12px]" @click="handleRefresh">
          <template #suffix>
            <span class="ml-1">{{ $t('refreshList') }}</span>
          </template>
        </rpa-hint-icon>
      </div>
    </template>
  </div>
</template>
