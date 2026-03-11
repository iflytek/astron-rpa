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

const props = defineProps<{ robotId: string }>()

const modal = NiceModal.useModal()
const processStore = useProcessStore()
const activeTab = ref<string[]>(['custom'])
const searchKeyword = ref('')
const activeKeys = ref<string[]>([]) // 展开的分组 keys

// 自建组件列表
const { state: componentList, execute: executeCustom } = useAsyncState(() => getComponentManageList(props.robotId), [])

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
    componentId: appInfo.resourceId || appInfo.appId,
    icon: appInfo.iconUrl || '',
    name: appInfo.appName,
    introduction: appInfo.appIntro || '',
    version: appInfo.resourceVersion || appInfo.appVersion || 1,
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

// 初始化时展开所有分组
watch(marketGroups, (groups) => {
  if (groups.length > 0) {
    activeKeys.value = groups.map(g => g.key)
  } else {
    activeKeys.value = []
  }
}, { immediate: true })

const filteredList = computed(() => {
  if (activeTab.value[0] === 'market') {
    // 团队市场已经在接口层面过滤，这里返回空数组，因为会通过分组显示
    return []
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
    activeKeys.value = []
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
    width="75%"
    class="max-w-[1138px]"
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

      <div class="flex-1 flex flex-col">
        <a-input
          v-model:value="searchKeyword"
          placeholder="请输入组件名称"
          allow-clear
          class="mb-4 w-[480px]"
          @press-enter="handleSearch"
          @blur="handleSearch"
        >
          <template #prefix>
            <SearchOutlined />
          </template>
        </a-input>

        <!-- 组件列表 -->
        <div class="flex-1 overflow-y-auto">
          <!-- 团队市场 -->
          <template v-if="activeTab[0] === 'market'">
            <a-empty
              v-if="isEmpty(marketGroups)"
              :image="Empty.PRESENTED_IMAGE_SIMPLE"
            >
              <template #description>
                <div>当前不存在团队市场，请先至<a-button type="link" class="p-0" @click="handleJumpToMarket">应用市场</a-button>创建或加入一个团队市场</div>
              </template>
            </a-empty>
            <a-collapse
              v-else
              v-model:active-key="activeKeys"
              :bordered="false"
            >
              <a-collapse-panel
                v-for="group in marketGroups"
                :key="group.key"
                :header="group.name"
              >
                <div class="grid grid-cols-3 gap-4">
                  <Panel
                    v-for="item in group.components"
                    :key="item.componentId"
                    :data="item"
                    :robot-id="robotId"
                    @refresh="handleRefresh"
                  />
                </div>
              </a-collapse-panel>
            </a-collapse>
          </template>

          <!-- 自建组件 -->
          <template v-else>
            <div
              :class="{ 'flex items-center justify-center': isEmpty(filteredList) }"
            >
              <a-empty
                v-if="isEmpty(filteredList)"
                :image="Empty.PRESENTED_IMAGE_SIMPLE"
              />
              <div v-else class="grid grid-cols-3 gap-4">
                <Panel
                  v-for="item in filteredList"
                  :key="item.componentId"
                  :data="item"
                  :robot-id="robotId"
                  @refresh="handleRefresh"
                />
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </a-modal>
</template>
