<script setup lang="ts">
import { computed, toValue } from 'vue'

import { BOTTOM_BOOTLS_HEIGHT_SIZE_MIN } from '@/constants'

import { useProvideToolsStore } from './store'

const props = defineProps<{ height: number }>()
const collapsed = defineModel('collapsed', { type: Boolean, default: false })

const { moduleType, activeKey, activeTab, tabs } = useProvideToolsStore()

// 内容的最大高度
const contentHeight = computed(() => {
  return Math.max(props.height, BOTTOM_BOOTLS_HEIGHT_SIZE_MIN) - 46 - 8 // 减去 tab 高度和 margin-bottom
})

function expand(bool: boolean) {
  collapsed.value = bool
  moduleType.value = 'default' // 切换 tab 时重置模块类型
}
</script>

<template>
  <section class="text-xs bottom-tools bg-[#FFFFFF] dark:bg-[#FFFFFF]/[.12] rounded-lg">
    <a-tabs
      v-model:active-key="activeKey"
      class="text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)] right-tab-close-area"
      size="small"
      @tab-click="() => expand(false)"
    >
      <template #rightExtra>
        <div class="flex items-center">
          <template v-if="!collapsed">
            <component :is="activeTab.rightExtra" />
          </template>
          <rpa-hint-icon
            v-if="!activeTab.hideCollapsed"
            name="caret-down-small"
            :title="collapsed ? '展开' : '收起'"
            class="ml-1"
            :class="[collapsed ? '-rotate-180' : 'rotate-0']"
            enable-hover-bg
            @click="() => expand(!collapsed)"
          />
        </div>
      </template>
      <a-tab-pane v-for="item in tabs" :key="item.key" class="z-0">
        <template #tab>
          <span class="flex items-center">
            <rpa-icon :name="item.icon" width="16px" height="16px" class="mr-1" />
            {{ $t(toValue(item.text)) }}
          </span>
        </template>
        <component :is="item.component" :height="contentHeight" />
      </a-tab-pane>
    </a-tabs>
  </section>
</template>

<style lang="scss" scoped>
.search-input {
  font-size: 12px;
  width: 230px;
  height: 22px;
  overflow: hidden;
}

.icon-close {
  font-size: 12px;
  color: #666;
  cursor: pointer;
  &:hover {
    color: #000;
  }
}

:deep(.search-input .ant-input) {
  height: 21px;
  font-size: 12px;
}

:deep(.search-input .ant-btn-sm) {
  height: 22px;
  font-size: 12px;
}

:deep(.search-input .anticon) {
  vertical-align: middle;
}

:deep(.ant-tabs .ant-tabs-extra-content) {
  height: 24px;
  margin-right: 16px;
}

:deep(.ant-tabs-small > .ant-tabs-nav .ant-tabs-tab) {
  margin-left: 16px;
  font-size: 12px;
}

:deep(.ant-tabs .ant-tabs-tab.ant-tabs-tab-active .ant-tabs-tab-btn) {
  font-weight: 600;
  color: inherit;
}

:deep(.ant-tabs > .ant-tabs-nav) {
  margin-bottom: 8px;
  height: 46px;
}

:deep(.ant-tabs-extra-content) {
  display: flex;
  align-items: center;
}

:deep(.ant-tabs .ant-tabs-tabpane) {
  padding: 0 8px;
}

:deep(.cv-pick-btn) {
  margin-right: 8px;
}

:deep(.vxe-table--render-wrapper) {
  background-color: transparent !important;
}

:deep(.vxe-table--header-wrapper) {
  background-color: transparent !important;
}

:deep(.vxe-table--body-wrapper) {
  background-color: transparent !important;
}
</style>
