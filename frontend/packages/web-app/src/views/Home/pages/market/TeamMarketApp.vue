<script setup lang="ts">
import { computed, watch } from 'vue'

import NormalTable from '@/components/NormalTable/index.vue'
import { useMarketStore } from '@/stores/useMarketStore'
import CardsShow from '@/views/Home/components/TeamMarket/CardsShow.vue'
import CreateMarket from '@/views/Home/components/TeamMarket/CreateMarket.vue'
import { useCardsApp } from '@/views/Home/components/TeamMarket/hooks/useCardsApp.ts'

const { homePageListRef, refreshHomeTable, cardsOption, getMembersByTeam, getAppCategory } = useCardsApp()
const marketStore = useMarketStore()

function updateCheckNum(data) {
  // 更新列表中特定应用的查看数
  homePageListRef.value.tableData.forEach((item) => {
    if (item.appId === data.appId) {
      item.checkNum = data.checkNum
    }
  })
}

const hasMarkets = computed(() => {
  return marketStore.activeMarket?.marketId && marketStore.markets[0]?.children.length > 0
})

getAppCategory()

watch(() => marketStore.activeMarket?.marketId, (val) => {
  if (val) {
    getMembersByTeam(val)
    cardsOption.params.marketId = marketStore.activeMarket?.marketId
    refreshHomeTable()
  }
}, { immediate: true })
</script>

<template>
  <div class="h-[calc(100%-40px)] bg-[#fff] dark:bg-[rgba(255,255,255,0.04)] rounded-[16px] p-4 m-5 ml-0 ">
    <NormalTable v-if="hasMarkets" ref="homePageListRef" :option="cardsOption">
      <template #default="{ loading, tableData, height }">
        <CardsShow
          :class="`absolute w-full h-[${height}px] overflow-y-auto`"
          :loading="loading"
          :data-source="tableData"
          @update-check-num="updateCheckNum"
          @refresh-home-table="refreshHomeTable"
        />
      </template>
    </NormalTable>
    <CreateMarket v-else />
  </div>
</template>
