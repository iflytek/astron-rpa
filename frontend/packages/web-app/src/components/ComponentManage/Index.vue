<script lang="ts" setup>
import { NiceModal } from '@rpa/components'
import { computed, ref, watch } from 'vue'
import { useAsyncState } from '@vueuse/core'
import { Empty } from 'ant-design-vue'
import { SearchOutlined } from '@ant-design/icons-vue'
import { isEmpty } from 'lodash-es'
import { message } from 'ant-design-vue'

import { getComponentManageList, getMarketComponentList } from '@/api/robot'
import { APPLICATIONMARKET } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import { useProcessStore } from '@/stores/useProcessStore'

import Panel from './Panel.vue'

const props = defineProps<{ robotId: string, robotVersion: number }>()

const modal = NiceModal.useModal()
const processStore = useProcessStore()
const activeTab = ref<string[]>(['market'])
const searchKeyword = ref('')
const ALL_MARKETS_KEY = 'all' // 全部市场的标识
const selectedMarketId = ref<string>(ALL_MARKETS_KEY) // 选中的团队市场ID，默认选择全部

// 自建组件列表
const { state: componentList, execute: executeCustom } = useAsyncState(() => getComponentManageList(props.robotId, props.robotVersion), [])

// 团队市场列表 - 返回的是 List<IPage<AppInfoVo>>，每个 IPage 对应一个团队市场
const { state: marketPages, execute: executeMarket } = useAsyncState(async () => {
  const res = await getMarketComponentList({
    pageNo: 1,
    pageSize: 1000,
    appName: searchKeyword.value.trim() || undefined,
    appType: 'component', // 组件类型
  })
  if (Array.isArray(res.data)) {
    return res.data as RPA.IPage<RPA.AppInfoVo>[]
  }
  return []
}, [])

// 将 AppInfoVo 转换为 ComponentManageItem 格式
function convertAppInfoToComponentManageItem(appInfo: RPA.AppInfoVo): RPA.ComponentManageItem {
  return {
    componentId: appInfo.resourceId,
    appId: appInfo.appId, // 应用ID，用于安装和移除操作
    icon: appInfo.iconUrl || '',
    name: appInfo.appName,
    introduction: appInfo.appIntro || '',
    version: appInfo.appVersion || 1,
    blocked: appInfo.obtainStatus === 0 ? 1 : 0,
    isLatest: appInfo.resourceIsLatest || 0,
    latestVersion: appInfo.resourceLatestVersion || appInfo.appVersion || 1,
    marketId: appInfo.marketId,
    allowOperate: appInfo.allowOperate,
  }
}

// 团队市场分组数据
const marketGroups = computed(() => {
  if (!Array.isArray(marketPages.value) || marketPages.value.length === 0) {
    return []
  }
  
  return marketPages.value.map((page: RPA.IPage<RPA.AppInfoVo>, index: number) => {
    const firstRecord = page.records?.[0]
    const marketName = firstRecord?.marketName || `团队市场${index + 1}`
    const marketId = firstRecord?.marketId || `market-${index}`
    
    return {
      key: marketId,
      name: marketName,
      components: (page.records || []).map(convertAppInfoToComponentManageItem),
    }
  })
})

// 初始化时保持选择"全部"
watch(marketGroups, (groups) => {
  if (groups.length > 0 && selectedMarketId.value === '') {
    selectedMarketId.value = ALL_MARKETS_KEY
  }
}, { immediate: true })

// 当前选中的市场组件列表
const currentMarketComponents = computed(() => {
  if (activeTab.value[0] !== 'market' || !selectedMarketId.value) {
    return []
  }
  // 如果选择"全部"，返回所有市场的组件
  if (selectedMarketId.value === ALL_MARKETS_KEY) {
    return marketGroups.value.flatMap(group => group.components)
  }
  // 否则返回选中市场的组件
  const selectedGroup = marketGroups.value.find(g => g.key === selectedMarketId.value)
  return selectedGroup?.components || []
})

// 团队市场下拉选项
const marketOptions = computed(() => {
  const options = [
    { label: '全部', value: ALL_MARKETS_KEY },
    ...marketGroups.value.map(group => ({
      label: group.name,
      value: group.key,
    })),
  ]
  return options
})

const filteredList = computed(() => {
  if (activeTab.value[0] === 'market') {
    // 团队市场：返回当前选中市场的组件列表
    return currentMarketComponents.value
  } else {
    // 自建组件
    let list = componentList.value || []
    if (searchKeyword.value.trim()) {
      list = list.filter(item => 
        item.name.toLowerCase().includes(searchKeyword.value.toLowerCase().trim())
      )
    }
    return list
  }
})

watch(activeTab, () => {
  if (activeTab.value[0] === 'market') {
    executeMarket()
    // 重置选中市场为"全部"
    selectedMarketId.value = ALL_MARKETS_KEY
  } else {
    executeCustom()
  }
  searchKeyword.value = ''
})

function handleSearch() {
  if (activeTab.value[0] === 'market') {
    executeMarket()
  }
}

function handleRefresh() {
  if (activeTab.value[0] === 'market') {
    executeMarket()
  } else {
    executeCustom()
  }
  processStore.componentTree.execute()
}

async function handleJumpToMarket() {
  try {
    modal.hide()
    await processStore.saveProject()
    message.success('保存成功')
    useRoutePush({ name: APPLICATIONMARKET })
  }
  catch (err) {
    message.error('保存成功')
  }
}
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    :title="$t('moduleManagement')"
    width="1138px"
    :keyboard="false"
    :mask-closable="false"
    :footer="null"
    destroy-on-close
    centered
  >
    <div class="flex gap-4 h-[520px]">
      <div class="w-[160px]">
        <a-menu
          v-model:selected-keys="activeTab"
          mode="vertical"
        >
          <a-menu-item key="market">
            团队市场
          </a-menu-item>
          <a-menu-item key="custom">
            自建组件
          </a-menu-item>
        </a-menu>
      </div>

      <div class="flex-1 flex flex-col overflow-auto">
        <div class="flex items-center gap-4 mb-4">
          <a-input
            v-model:value="searchKeyword"
            placeholder="请输入组件名称"
            allow-clear
            class="max-w-[480px]"
            @press-enter="handleSearch"
            @blur="handleSearch"
          >
            <template #prefix>
              <SearchOutlined />
            </template>
          </a-input>
          
          <!-- 团队市场下拉选择器 -->
          <a-select
            v-if="activeTab[0] === 'market'"
            v-model:value="selectedMarketId"
            :options="marketOptions"
            placeholder="请选择团队市场"
            class="w-[200px]"
          />
        </div>

        <!-- 组件列表 -->
        <div class="flex-1 overflow-y-auto">
          <a-empty
            v-if="isEmpty(filteredList)"
            :image="Empty.PRESENTED_IMAGE_SIMPLE"
          >
            <template v-if="activeTab[0] === 'market' && isEmpty(marketGroups)" #description>
              <div>当前不存在团队市场，请先至<a-button type="link" class="p-0" @click="handleJumpToMarket">应用市场</a-button>创建或加入一个团队市场</div>
            </template>
          </a-empty>
          <div v-else class="component-grid">
            <Panel
              v-for="item in filteredList"
              :key="item.componentId"
              :data="item"
              :robot-id="robotId"
              :robot-version="robotVersion"
              @refresh="handleRefresh"
            />
          </div>
        </div>
      </div>
    </div>
  </a-modal>
</template>

<style lang="scss" scoped>
.component-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}
</style>
