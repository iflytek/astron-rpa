<script setup lang="ts">
import { computed } from 'vue';
import { useAppConfigStore } from '@/stores/useAppConfig'

const appConfigStore = useAppConfigStore()

const handleClick = () => appConfigStore.showUpdaterModal()

const needUpdate = computed(() => appConfigStore.updaterState.couldUpdate && appConfigStore.updaterState.downloaded)
</script>

<template>
  <a-tooltip v-if="needUpdate" title="点击查看新版本">
    <div class="w-[22px] h-[22px] rounded-3xl bg-primary flex items-center justify-center cursor-pointer" @click="handleClick">
      <rpa-icon name="arrow-up" class="w-[14px] h-[14px] text-white" />
    </div>
  </a-tooltip>
</template>
