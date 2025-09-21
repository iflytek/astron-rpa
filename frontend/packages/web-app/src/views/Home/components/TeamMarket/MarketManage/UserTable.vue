<script setup lang="ts">
import NormalTable from '@/components/NormalTable/index.vue'
import { useMarketStore } from '@/stores/useMarketStore'
import { MARKET_USER_ADMIN, MARKET_USER_OWNER } from '@/views/Home/components/TeamMarket/config/market'
import { useTeamUserTable } from '@/views/Home/components/TeamMarket/hooks/MarketManage/useTeamUserTable'

const { homeTableRef, tableOption } = useTeamUserTable()
</script>

<template>
  <div v-if="[MARKET_USER_ADMIN, MARKET_USER_OWNER].includes(useMarketStore().activeMarket?.userType)" class="w-full h-[calc(100%-225px-32px)] pr-5">
    <NormalTable ref="homeTableRef" :option="tableOption" />
  </div>
</template>

<style lang="scss" scoped>
</style>
