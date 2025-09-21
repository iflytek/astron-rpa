<script setup lang="ts">
import { provide, ref } from 'vue'

import { TEAMMARKETS } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import BaseInfo from '@/views/Home/components/TeamMarket/MarketManage/BaseInfo.vue'
import UserTable from '@/views/Home/components/TeamMarket/MarketManage/UserTable.vue'

function goPage() {
  useRoutePush({ name: TEAMMARKETS })
}

const isOnlyUser = ref(false)
provide('isOnlyUser', {
  isOnlyUser,
  setOnlyUser: (value: boolean) => {
    isOnlyUser.value = value
  },
})
</script>

<template>
  <div class="TeamMarketManage bg-[#FFFFFF] dark:bg-[#FFFFFF]/[.04]">
    <rpa-hint-icon name="chevron-left" enable-hover-bg @click="goPage">
      <template #suffix>
        <span class="text-[12px] leading-3">{{ $t('goBack') }}</span>
      </template>
    </rpa-hint-icon>
    <BaseInfo />
    <UserTable class="mt-4" />
  </div>
</template>

<style lang="scss" scoped>
.TeamMarketManage {
  height: calc(100% - 40px);
  margin: 20px 20px 20px 0;
  padding: 20px;
  border-radius: 16px;
}

:deep(.ant-table) {
  background: transparent;

  .ant-table-cell::before {
    display: none;
  }
}

:deep(.nTable-header_btns) {
  button {
    margin-top: 0 !important;
  }
}
</style>
