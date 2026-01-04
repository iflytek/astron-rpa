<script setup lang="ts">
import { reactiveComputed } from '@vueuse/core'
import { sum } from 'lodash-es'
import { computed, provide, ref, shallowRef, watch } from 'vue'

import { BOTTOM_BOOTLS_HEIGHT_SIZE_MIN } from '@/constants'
import { useProcessStore } from '@/stores/useProcessStore'
import { useRunningStore } from '@/stores/useRunningStore'

import { useProvideConfigParameter } from './components/ConfigParameter/useConfigParameter.ts'
import { useCVManager } from './components/CvManager/useCVManager.ts'
import { useProvideDataSheetStore } from './components/DataSheet/useDataSheet'
import { useDebugLog } from './components/DebugLog/useDebugLog.ts'
import { useElementManager } from './components/ElementManager/useElementManager.ts'
import { useLog } from './components/Log/useLog.ts'
import { useSubProcessUse } from './components/SubProcessSearch/useSubProcessUse'
import type { TabConfig } from './types'

const props = defineProps<{ height: number }>()
const collapsed = defineModel('collapsed', { type: Boolean, default: false })

console.log('BottomTools props.height', props.height)

// 创建并提供 configParameter 实例
const { config: configParamsTabConfig } = useProvideConfigParameter()
const { dataSheetConfig } = useProvideDataSheetStore()

const processStore = useProcessStore()

const initTabs = reactiveComputed(() => [
  useLog(),
  useElementManager(),
  useCVManager(),
  configParamsTabConfig,
  dataSheetConfig,
])

const tabs = shallowRef<TabConfig[]>(initTabs)
const activeKey = ref(tabs.value[0].key)
const searchText = ref('')
const moduleType = ref('default')

// 内容的最大高度
const contentHeight = computed(() => {
  return Math.max(props.height, BOTTOM_BOOTLS_HEIGHT_SIZE_MIN) - 46 - 8 // 减去 tab 高度和 margin-bottom
})

// provide 元素管理/图片管理
provide('collapsed', ref(false)) // 展开折叠
provide('searchText', searchText) // 搜索文本
provide('moduleType', moduleType) // 展示模块类型 moduleType: 'default' | 'unuse'-未使用 | 'quoted'-被引用
provide('refresh', ref(true)) // 刷新
provide('unUseNum', ref(0)) // 未使用元素数量
provide('activeTab', activeKey) // 未使用元素数量
provide('logTableHeight', contentHeight)

const activeTab = computed<TabConfig>(() => tabs.value.find(tab => tab.key === activeKey.value))
const searchSubProcessTotal = computed(() => {
  return sum(processStore.searchSubProcessResult.map(pItem => pItem.nodes?.length || 0))
})

function expand(bool: boolean) {
  collapsed.value = bool
  moduleType.value = 'default' // 切换 tab 时重置模块类型
}

watch(() => useRunningStore().running, (val) => {
  if (['run', 'debug'].includes(val)) {
    expand(false)
  }
  if (val === 'run') {
    activeKey.value = 'logs'
  }
  if (val === 'debug') {
    tabs.value = [...tabs.value, useDebugLog()]
    activeKey.value = 'debugLog'
  }
  else {
    tabs.value = tabs.value.filter(tab => tab.key !== 'debugLog')
    activeKey.value = tabs.value[0].key
  }
})

watch(() => processStore.searchSubProcessId, (val) => {
  if (val) {
    tabs.value = [useSubProcessUse()]
    activeKey.value = tabs.value[0].key
    expand(false)
  }
  else {
    tabs.value = initTabs
    activeKey.value = tabs.value[0].key
    expand(true)
  }
})

// 切换流程时，重置底部工具栏的标签页
watch(() => processStore.activeProcessId, () => {
  const initTabKeys = initTabs.map(item => item.key)
  const otherTabs = tabs.value.filter(tab => !initTabKeys.includes(tab.key))
  tabs.value = [...initTabs, ...otherTabs]
})
</script>

<template>
  <section class="text-xs bottom-tools bg-[#FFFFFF] dark:bg-[#FFFFFF]/[.12] rounded-lg">
    <a-tabs v-model:active-key="activeKey" class="text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)] right-tab-close-area" size="small" @tab-click="() => expand(false)">
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
      <a-tab-pane v-for="item in tabs" :key="item.key">
        <template #tab>
          <span class="flex items-center">
            <rpa-icon :name="item.icon" width="16px" height="16px" class="mr-1" />
            {{ $t(item.text) }}
            <span v-if="activeKey === 'subProcessSearch'" class="ml-1">{{ searchSubProcessTotal }}</span>
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
