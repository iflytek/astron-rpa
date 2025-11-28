<script lang="ts" setup>
import { computed, inject, onMounted, watch } from 'vue'

import type { Tab, TabsContext } from './types'

const props = withDefaults(defineProps<Tab>(), {
  show: true,
})

const context = inject<TabsContext>('tabsContext')
const isActive = computed(() => context?.activeTab.value === props.value)

onMounted(() => context?.registerTab(props))

watch(() => props.show, (newVal) => {
  context?.updateTab(props.value, { show: newVal })
})
</script>

<template>
  <div v-if="isActive && show" class="custom-tab-panel">
    <slot />
  </div>
</template>
