<script setup lang="ts">
import { EditOutlined } from '@ant-design/icons-vue'
import { useTheme } from '@rpa/components'
import { Descriptions } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'

import { useMarketStore } from '@/stores/useMarketStore'
import { MARKET_TYPE_PUBLIC, MARKET_USER_OWNER } from '@/views/Home/components/TeamMarket/config/market'
import { useBaseInfo } from '@/views/Home/components/TeamMarket/hooks/MarketManage/useBaseInfo'
import { useTeamUserTable } from '@/views/Home/components/TeamMarket/hooks/MarketManage/useTeamUserTable'

const { t } = useTranslation()
const { inputRef, teamMarketConfig, baseInfoData, setEditing, editMarket } = useBaseInfo()
const { leaveTeam, giveOwner, fireTeam } = useTeamUserTable()
const { isDark } = useTheme()

function openModal(key: string) {
  switch (key) {
    case 'leaveTeam':
      MARKET_USER_OWNER === useMarketStore().activeMarket.userType ? giveOwner() : leaveTeam()
      break
    case 'disbandTeam':
      fireTeam()
      break
    default:
      break
  }
}
</script>

<template>
  <div class="flex justify-between items-center my-[18px]">
    <span class="text-[20px] font-semibold">{{ $t('market.manageMarket') }}</span>
    <div class="flex items-center gap-2">
      <template
        v-for="subItem in (teamMarketConfig.find(item => item.type === 'buttons') as any).list"
        :key="subItem.key"
      >
        <a-tooltip v-if="subItem.type === 'button' && subItem.show(baseInfoData.userType, baseInfoData.marketType)" :title="t((subItem.tooltip || subItem.label || subItem.key) as string)">
          <a-button :type="subItem.btnType || 'default'" size="middle" class="mr-2" @click="openModal(subItem.key)">
            {{ t(subItem.label) }}
          </a-button>
        </a-tooltip>
      </template>
    </div>
  </div>
  <Descriptions
    class="market-base-info bg-[#000000]/[.03] dark:bg-[#FFFFFF]/[.03]"
    :title="t('basicInformation')"
    :column="6" layout="vertical"
    :label-style="{ color: isDark ? 'rgba(255, 255, 255, 0.65)' : 'rgba(0, 0, 0, 0.65)' }"
    :content-style="{ paddingRight: '10px' }"
  >
    <template v-for="(item) in teamMarketConfig">
      <Descriptions.Item v-if="item.type === 'input'" :key="item.key" :label="t(item.label)">
        <a-input
          v-if="item.isEditing"
          ref="inputRef"
          v-model:value.trim="baseInfoData[item.key]"
          size="small"
          :auto-focus="true"
          :max-length="20"
          @blur="editMarket(item)"
        />
        <template v-else>
          <a-tooltip :title="baseInfoData[item.key]" :mouse-enter-delay="1">
            <span class="line-clamp-2 elipsis">
              {{ baseInfoData[item.key] }}
            </span>
          </a-tooltip>
          <EditOutlined v-if="baseInfoData.marketType !== MARKET_TYPE_PUBLIC && baseInfoData.userType === MARKET_USER_OWNER" class="cursor-pointer ml-1" @click="setEditing(item)" />
        </template>
      </Descriptions.Item>
      <Descriptions.Item v-if="item.type === 'label'" :key="item.key" :label="t(item.label)">
        <span>{{ baseInfoData[item.key] }}</span>
      </Descriptions.Item>
    </template>
  </Descriptions>
</template>

<style lang="scss" scoped>
.market-base-info {
  height: 162px;
  border-radius: 10px;
  padding: 16px 20px;
  :deep(.ant-descriptions-item-container) {
    align-items: center;
  }
  :deep(.ant-descriptions-item-content) {
    align-items: center;
  }
  .truncate {
    display: inline-block;
    max-width: 300px;
    margin: 0 5px 5px 0;
    vertical-align: middle;
  }
}

:deep(.ant-descriptions-item) {
  padding-bottom: 10px !important;
}
</style>
