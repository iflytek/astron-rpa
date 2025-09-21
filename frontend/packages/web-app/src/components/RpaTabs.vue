<script setup lang="ts">
import { useVModel } from '@vueuse/core'

const props = defineProps<{
  value: string
  tabs: {
    name: string
    key: string
  }[]
}>()

const emits = defineEmits(['update:value', 'change'])
const currentTab = useVModel(props, 'value', emits)
function handleClick(tabKey: string) {
  currentTab.value = tabKey
  emits('change', tabKey)
}
</script>

<template>
  <div class="tabs w-full h-[32px] flex justify-between items-center rounded-[6px] p-[2px] bg-[rgba(0,0,0,0.04)] dark:bg-[rgba(255,255,255,0.04)] text-[14px]">
    <div v-for="tab in tabs" :class="`tabItem grow text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)] ${tab.key === currentTab ? 'bg-[#fff] dark:bg-[rgba(255,255,255,0.12)] text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)]' : ''}`" @click="handleClick(tab.key)">
      {{ tab.name }}
    </div>
  </div>
</template>

<style lang="scss" scoped>
.tabs {
  .tabItem {
    // width: 50%;
    height: 28px;
    line-height: 28px;
    font-size: $font-size-sm;
    border-radius: 6px;
    text-align: center;
    cursor: pointer;
  }
}
</style>
