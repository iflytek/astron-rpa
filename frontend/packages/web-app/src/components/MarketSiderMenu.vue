<script setup lang="ts">
import { PlusOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { checkMarketNum } from '@/api/market'
import { CreateTeamMarketModal } from '@/components/CreateTeamMarketModal'
import GlobalModal from '@/components/GlobalModal/index.ts'
import { COMMON_SIDER_WIDTH } from '@/constants'
import { TEAMMARKETMANAGE, TEAMMARKETS } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import { useMarketStore } from '@/stores/useMarketStore'
import { useUserStore } from '@/stores/useUserStore'

const userStore = useUserStore()

const { markets, setCurrentMarketItem } = useMarketStore()
const openKeys = ref([markets.find(item => item.active)?.key])

watch(
  () => useMarketStore().markets,
  (newMarkets) => {
    const key = newMarkets.find(item => item.active)?.key
    if (key && !openKeys.value.includes(key)) {
      openKeys.value.push(key)
    }
  },
  { immediate: true, deep: true },
)

const selectedKeys = computed(() => {
  const activeMenus = useMarketStore().markets.find(item => item.active)
  const activeMarket = useMarketStore().activeMarket
  return activeMarket ? [activeMarket.marketId] : [activeMenus?.key]
})

function menuClick(key: string, route?: string) {
  setCurrentMarketItem(key)
  useRoutePush({ name: route || TEAMMARKETS })
}

function jumpToTeamDetail(e, data: any) {
  e.stopPropagation()
  setCurrentMarketItem(data.marketId)
  useRoutePush({ name: TEAMMARKETMANAGE })
}

async function createTeam() {
  if (userStore.currentTenant?.tenantType === 'personal') {
    const res = await checkMarketNum()
    if (!res.data) {
      GlobalModal.warn({
        title: '提示',
        content: '个人版最多可创建3个团队市场，您已满额。',
        centered: true,
        keyboard: false,
        okText: '我知道了',
      })
      return
    }
  }
  NiceModal.show(CreateTeamMarketModal)
}

const marketId = useRoute()?.query?.marketId as string
useMarketStore().refreshTeamList(marketId)

watch(() => userStore.currentTenant?.id, (val) => {
  if (val) {
    useMarketStore().refreshTeamList()
  }
})
</script>

<template>
  <a-layout-sider :width="COMMON_SIDER_WIDTH" class="market-sider">
    <a-menu trigger-sub-menu-action="click" :selected-keys="selectedKeys" :open-keys="openKeys" mode="inline" class="marketList-container">
      <template v-for="marketsItem in markets">
        <div v-if="marketsItem.key === 'teamMarket'" :key="marketsItem.key" class="market-menu-item flex items-center justify-between h-[40px] leading-[40px]">
          <span class="inline-block dark:text-[#ffffffa6] text-[#000000a6]">{{ $t('teamMarkets') }}</span>
          <span class="inline-block text-primary text-[14px] cursor-pointer hover:opacity-95" @click.stop="createTeam">
            <PlusOutlined class="ml-2" />
            {{ $t("market.createTeam") }}
          </span>
        </div>
        <a-sub-menu v-if="marketsItem.children.length" :key="marketsItem.key" class="market-sub-menu">
          <template #title>
            <span class="menu-title">
              {{ $t(marketsItem.name) }}
            </span>
          </template>
          <a-menu-item v-for="item in marketsItem.children" :key="item.marketId" class="market-menu-item flex" @click="(e) => menuClick(item.marketId)">
            <a-tooltip placement="top" :title="item.marketName">
              <span class="text-ellipsis whitespace-nowrap overflow-hidden pr-[10px]">
                {{ $t(item.marketName) }}
              </span>
            </a-tooltip>
            <rpa-hint-icon name="setting" class="absolute right-[10px] top-[8px]" enable-hover-bg @click.stop="(e) => jumpToTeamDetail(e, item)" />
          </a-menu-item>
        </a-sub-menu>
        <template v-else>
          <a-menu-item :key="marketsItem.key" class="market-menu-item flex" @click="(e) => menuClick(marketsItem.key, marketsItem.route)">
            {{ $t(marketsItem.name) }}
          </a-menu-item>
        </template>
      </template>
    </a-menu>
  </a-layout-sider>
</template>

<style lang="scss">
.market-sider {
  padding: 20px;
  .ant-menu {
    background-color: transparent;
  }
  .ant-menu .ant-menu-submenu-arrow {
    left: 5px;
    width: 20px;
    height: 20px;
    border-radius: 4px;
    transform: translateY(-50%) !important;
    &::after,
    &::before {
      top: 50%;
      left: 50%;
      margin-left: -3px;
      margin-top: 1px;
      transition: none !important;
    }
  }
  .ant-menu-submenu-open.ant-menu-submenu-inline > .ant-menu-submenu-title > .ant-menu-submenu-arrow {
    &::after,
    &::before {
      margin-top: -3px;
    }
  }
  .ant-menu-submenu-title {
    margin-bottom: 2px !important;
    padding-left: 30px !important;
    width: 100%;
    height: 40px;
    line-height: 40px;
    margin: 0;
    border-radius: 8px;
    top: initial;
    color: initial !important;
    .ant-menu-title-content {
      &:hover {
        opacity: 0.95 !important;
        color: initial;
      }
    }
  }
  .ant-menu-item {
    // 菜单项
    width: 100%;
    height: 40px;
    line-height: 40px;
    margin: 0;
    padding: 16px !important;
    border-radius: 8px;
    text-align: left;
    padding-left: 30px !important;
    margin-bottom: 2px !important;
  }
  .ant-menu-root > .ant-menu-item {
    padding-left: 12px !important;
  }
  .ant-menu-root > .ant-menu-submenu {
    border-bottom: 1px solid rgba(#000000, 0.1);
    border-radius: 0 !important;
    margin-bottom: 12px;
    padding-bottom: 10px;
  }
  .ant-menu-inline {
    border-right: none;
    background: transparent !important;
  }
  .ant-menu-item-selected {
    color: initial;
  }
  .ant-menu-submenu-arrow {
    &:hover {
      background-color: rgba(#8482fe, 0.3);
    }
  }
}

.dark .market-sider {
  .ant-menu-root > .ant-menu-submenu {
    border-color: rgba(#ffffff, 0.1);
  }
}
</style>
