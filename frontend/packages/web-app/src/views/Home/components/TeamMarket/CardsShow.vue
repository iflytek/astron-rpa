<script setup lang="ts">
import { ClockCircleOutlined, EllipsisOutlined } from '@ant-design/icons-vue'
import { useTranslation } from 'i18next-vue'
import { computed, defineAsyncComponent } from 'vue'

import Avatar from '@/components/Avatar/Avatar.vue'
import { SECURITY_LEVEL_TEXT } from '@/views/Home/components/TeamMarket/config/market.ts'

import { useCardsShow } from './hooks/useCardsShow'

interface AppItem {
  appId: string
  appName: string
  appIntro: string
  marketId: string
  checkNum: number
  downloadNum: number
  iconUrl: string
  icon: string
  color: string
  allowOperate: number
  obtainStatus: number
  updateStatus: number
  expiryDateStr: string
  securityLevel: string
}

const props = defineProps<{
  dataSource: Array<AppItem>
  loading: boolean
}>()

const emits = defineEmits(['refreshHomeTable', 'updateCheckNum'])

const AppDetailDrawer = defineAsyncComponent(() => import('@/views/Home/components/TeamMarket/AppDetailDrawer.vue'))

const { t } = useTranslation()
const {
  appDrawerData,
  menus,
  showAppDrawer,
  closeAppDrawer,
  handleAppAchieve,
  menuItemClick,
} = useCardsShow(emits)

const appList = computed(() => props.dataSource)
const loading = computed(() => props.loading)
</script>

<template>
  <div class="cards-wrapper h-full">
    <div v-if="loading" class="cards-empty">
      <a-spin class="loading" />
    </div>
    <div v-else class="w-full h-full">
      <div v-if="appList.length > 0" class="grid gap-4" style="grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))">
        <div
          v-for="item in appList"
          :key="item.appId"
          :class="{ 'max-w-[356px]': appList.length === 1 }"
          class="card h-[165px] flex flex-col p-4 rounded-[12px] border border-[rgba(0,0,0,0.1)] dark:border-[rgba(255,255,255,0.16)] hover:bg-[#EFEFFF] dark:hover:bg-[#383764] cursor-pointer"
          @click="showAppDrawer(item)"
        >
          <div class="card_header flex-1 flex gap-4">
            <Avatar :robot-name="item.appName" :icon="item.icon" :color="item.color" class="ml-[2px] mt-[2px]" />
            <div class="flex-1 flex flex-col gap-[6px] overflow-hidden">
              <div class="flex items-center">
                <div class="flex-1 flex items-center whitespace-nowrap overflow-hidden">
                  <a-tooltip :title="item.appName" :mouse-enter-delay="1" placement="topLeft">
                    <div class="flex-1 overflow-hidden text-ellipsis text-[14px] text-[rgba(0,0,0,0.85)] dark:text-[#fff] font-medium mr-[4px]">
                      {{ item.appName }}
                    </div>
                  </a-tooltip>
                  <div v-if="item.obtainStatus === 1" class="px-1 h-[18px] leading-[18px] text-center rounded-[4px] bg-[rgb(243,243,247)] dark:bg-[rgba(255,255,255,0.08)] text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)] text-[12px]">
                    {{ t('common.obtained') }}
                  </div>
                  <div v-if="item.updateStatus === 1" class="px-1 h-[18px] leading-[18px] text-center rounded-[4px] bg-[rgb(243,243,247)] dark:bg-[rgba(255,255,255,0.08)] text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)] text-[12px]">
                    {{ t('common.hasUpdateVersion') }}
                  </div>
                </div>
                <a-tooltip v-if="item.securityLevel" :title="SECURITY_LEVEL_TEXT[item.securityLevel]" placement="top">
                  <rpa-icon class="inline-block ml-[4px]" :name="`market-${item.securityLevel}`" size="18px" />
                </a-tooltip>
              </div>
              <div class="card_desc text-[12px] line-clamp-2 leading-5 text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)] break-words">
                <a-tooltip :title="item.appIntro || t('noDescription')" :mouse-enter-delay="0.5">
                  {{ item.appIntro || t('noDescription') }}
                </a-tooltip>
              </div>
            </div>
          </div>
          <a-divider class="my-3" />
          <div class="card_footer flex justify-between items-center px-[2px]">
            <div class="card_info flex items-center gap-[10px] text-[12px] text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)] overflow-hidden">
              <a-tooltip :title="t('market.viewCount')" :mouse-enter-delay="1">
                <span class="flex items-center">
                  <rpa-icon name="eye" />
                  <span class="ml-[4px]">{{ item.checkNum }}</span>
                </span>
              </a-tooltip>
              <a-tooltip :title="t('market.obtainCount')" :mouse-enter-delay="1">
                <span class="flex items-center">
                  <rpa-icon name="download" />
                  <span class="ml-[1px]">{{ item.downloadNum }}</span>
                </span>
              </a-tooltip>
              <span v-if="item.expiryDateStr" class="flex items-center overflow-hidden">
                <ClockCircleOutlined />
                <span class="ml-[6px] overflow-hidden text-ellipsis"><span> {{ item.expiryDateStr }}</span></span>
              </span>
            </div>
            <div class="card_btn flex items-center">
              <a-dropdown v-if="item.allowOperate" :destroy-popup-on-hide="true" placement="top">
                <template #overlay>
                  <a-menu>
                    <a-menu-item v-for="menu in menus" :key="menu.key" :icon="menu.icon" @click="() => menuItemClick(menu.key, item)">
                      {{ menu.label }}
                    </a-menu-item>
                  </a-menu>
                </template>
                <EllipsisOutlined @click="(e: Event) => e.stopPropagation()" />
              </a-dropdown>
              <a-button
                :type="item.obtainStatus === 1 ? 'default' : 'primary'"
                :class="{ 'bg-[#F3F3F7] dark:bg-[#FFFFFF]/[.08]': item.obtainStatus === 1 }"
                size="middle"
                class="ml-[8px] flex justify-center items-center"
                @click="(e: Event) => { handleAppAchieve(e, item) }"
              >
                <div class="flex items-center gap-2">
                  <rpa-icon name="plus-square" />
                  <span>{{ item.obtainStatus === 1 ? t('common.reGet') : t('common.get') }}</span>
                </div>
              </a-button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="cards-empty">
        <a-empty />
      </div>
    </div>
    <AppDetailDrawer v-if="appDrawerData?.visible" :app-data="appDrawerData?.data" @close="(data) => { closeAppDrawer(data) }" />
  </div>
</template>

<style lang="scss" scoped>
.cards-wrapper {
  &::-webkit-scrollbar {
    width: 0;
  }
}
.cards-empty {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}
.cardsshow-overlay {
  width: 40px;
}
</style>
