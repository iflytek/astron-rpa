<script setup lang="ts">
import { EnterOutlined } from '@ant-design/icons-vue'
import { useEventBus, useEventListener, useFocusWithin } from '@vueuse/core'
import { computed, ref, watch } from 'vue'

import BUS from '@/utils/eventBus'

import { showTriggerInputKey } from '@/constants/eventBusKey'

import { PAGE_LEVEL_INDENT } from '../../config/flow.ts'
import { useRenderList } from '../flow/hooks/useRenderList.ts'

import { useSearch } from './hooks/useTriggerInput.ts'

const emits = defineEmits(['select'])
// 触发式插入，原子能力搜索及推荐
const { search, select, searchResult, getTitleTexts, onFocus } = useSearch(emits)

function closeSearch() {
  BUS.$emit('closeSearch') // 通知其他组件拾取已完成
}

const { insertItemLast, insertItemNext } = useRenderList()
const indent = computed(() => {
  const level = Math.max(insertItemLast.value?.level || 1, insertItemNext.value?.level || 1)
  return `${82 + (level - 1) * PAGE_LEVEL_INDENT}px`
})

const searchRef = ref()
const bus = useEventBus(showTriggerInputKey)
bus.on(() => searchRef.value.focus())

const { focused } = useFocusWithin(searchRef)
const { resetRenderList } = useRenderList()
const hasTrigger = ref(false)
useEventListener('mousedown', (e) => {
  if ((e.target as HTMLElement).classList.contains('addAtom-btn-icon')) {
    hasTrigger.value = true
  }
})
watch(focused, (newVal) => {
  if (newVal === false) {
    // 点击+按钮插入原子能力也会失焦，需要排除这种情况
    if (hasTrigger.value) {
      hasTrigger.value = false
    }
    else {
      resetRenderList()
    }
  }
})
</script>

<template>
  <div class="flex">
    <div class="indent-placeholder" :style="{ width: indent }" />
    <div class="trigger-input w-full forbid bg-[#F3F3F7] dark:bg-[#FFFFFF]/[.08]">
      <a-select
        ref="searchRef"
        class="trigger-input-select"
        popup-class-name="link-select"
        style="width: 100%"
        :value="[]"
        :open="focused"
        show-search
        mode="multiple"
        :placeholder="$t('enterRpaScriptName')"
        :auto-clear-search-value="true"
        :native-on-pointerdown="(e) => e.stopPropagation()"
        :filter-option="false"
        :virtual="false"
        @search="search"
        @select="select"
        @blur="closeSearch"
        @focus="onFocus"
      >
        <a-select-option
          v-for="option in searchResult"
          :key="option.parentKey + option.key"
          class="link-option"
          :value="option.key"
        >
          <div class="flex items-center">
            <rpa-icon :name="option.icon" size="14" class="mr-2" />
            <span
              v-for="i in getTitleTexts(option.title)"
              :class="{ 'text-primary': i.active }"
            >{{ i.text }}</span>
            <EnterOutlined />
          </div>
        </a-select-option>
      </a-select>
    </div>
  </div>
</template>

<style scoped lang="scss">
.indent-placeholder {
  flex: none;
}

.trigger-input {
  display: flex;
  position: relative;
  margin: 3px 8px;
  width: calc(100% - 82px);
  border-radius: 4px;
  &:hover,
  &:focus,
  &:active,
  &.active {
    background: rgba(93, 89, 255, 0.35);
  }
  &-select {
    :deep(.ant-select-selector) {
      background-color: transparent !important;
      border: none !important;
      box-shadow: none !important;
    }
  }
}
:global(.ant-select-dropdown.link-select) {
  width: 260px !important;
  min-width: 260px !important;
}
:global(.ant-select-dropdown.link-select .rc-virtual-list-scrollbar) {
  width: 4px !important;
}
// :global(.ant-select-dropdown.link-select .rc-virtual-list-scrollbar-thumb) {
//   background: #bbb !important;
// }
:global(.ant-select-dropdown.link-select .ant-select-item) {
  font-size: 12px !important;
}
:global(.ant-select-dropdown.link-select .ant-select-item-option-selected) {
  font-weight: normal;
}
:global(.ant-select-dropdown.link-select .ant-select-item .anticon-enter) {
  position: absolute;
  color: #c4c1c1;
  font-size: 12px;
  right: 10px;
  top: 12px;
}
:global(.ant-select-dropdown.link-select .ant-select-item-option-state) {
  display: none !important;
}
:global(.ant-select-dropdown.link-select .ant-select-item-option-selected:not(.ant-select-item-option-disabled)) {
  background: transparent !important;
}
:global(.ant-select-dropdown.link-select.ant-select-dropdown-empty) {
  display: none !important;
}
</style>
