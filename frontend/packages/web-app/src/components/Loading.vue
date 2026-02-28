<script setup lang="ts">
import { Loading } from '@rpa/components'
import type { LoadingProps } from '@rpa/components'
import { onBeforeUnmount, ref } from 'vue'

import BUS from '@/utils/eventBus'

const loadingRef = ref<InstanceType<typeof Loading>>()

function fn(params: LoadingProps) {
  loadingRef.value?.isLoading(params)
}

// Ensure we don't duplicate listeners if component is remounted
BUS.$off('isLoading', fn)
BUS.$on('isLoading', fn)

onBeforeUnmount(() => {
  BUS.$off('isLoading', fn)
})
</script>

<template>
  <Loading ref="loadingRef" />
</template>
