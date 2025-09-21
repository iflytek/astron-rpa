<script lang="ts" setup>
import { computed, inject, onMounted } from 'vue'
import type { Ref } from 'vue'

type Position = 'top' | 'left' | 'right' | 'bottom'

interface Tab {
  name: string
  value: PropertyKey
  size?: string | number
}

interface TabsContext {
  activeTab: Ref<Tab['value']>
  position: Ref<Position>
  registerTab: (tab: Tab) => void
}

const props = defineProps<Tab>()

const context = inject<TabsContext>('tabsContext')
const isActive = computed(() => context?.activeTab.value === props.value)

onMounted(() => {
  if (!context)
    return
  const { name, value, size } = props
  context?.registerTab({ name, value, size })
})
</script>

<template>
  <div v-if="isActive" class="custom-tab-panel">
    <slot />
  </div>
</template>
