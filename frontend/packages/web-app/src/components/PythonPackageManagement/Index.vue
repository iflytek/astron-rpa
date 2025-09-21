<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'

import { usePythonPackageStore } from '@/stores/usePythonPackageStore'

import PyHeader from './components/PyHeader.vue'
import PyTable from './components/PyTable.vue'
import { usePythonLoading } from './hooks/usePythonLoading'

const pythonPackageStore = usePythonPackageStore()

usePythonLoading()

pythonPackageStore.updatePythonList()

const sidebarWide = ref(false)

onBeforeUnmount(() => {
  pythonPackageStore.reset()
})
</script>

<template>
  <div class="pythonDependence bg-[#fff] dark:bg-[#1d1d1d]" :class="[sidebarWide ? 'w-[620px]' : 'w-80']">
    <PyHeader v-model:sidebar-wide="sidebarWide" />
    <PyTable />
  </div>
</template>

<style lang="scss">
.pythonDependence {
  height: 100%;
  position: relative;
  padding: 12px 16px;
  --table-head-default: rgba(0, 0, 0, 0.45);
  --table-body-default: rgba(0, 0, 0, 0.85);

  .dark & {
    --table-head-default: rgba(255, 255, 255, 0.45);
    --table-body-default: rgba(255, 255, 255, 0.85);
  }
}
</style>
