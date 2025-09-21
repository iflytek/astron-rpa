<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import MarketSiderMenu from '@/components/MarketSiderMenu.vue'
import SiderMenu from '@/components/SiderMenu.vue'
import { APPLICATIONMARKET } from '@/constants/menu'

const route = useRoute()

const isMarket = computed(() => {
  return route.matched[0].name === APPLICATIONMARKET
})
</script>

<template>
  <div class="home-content flex h-full">
    <MarketSiderMenu v-if="isMarket" />
    <SiderMenu v-else />

    <div class="flex-1 relative">
      <router-view />
    </div>
  </div>
</template>

<style lang="scss" scoped>
:deep(.ant-menu-light.ant-menu-root.ant-menu-inline) {
  border-inline-end: none;
}

.home-content {
  padding-top: var(--headerHeight);
}
</style>
