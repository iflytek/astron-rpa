<script setup lang="ts">
import NormalTable from '@/components/NormalTable/index.vue'

import { useComponentTableOption } from './hooks/ComponentManagement'

const { tableOption, tableRef } = useComponentTableOption()
</script>

<template>
  <NormalTable ref="tableRef" :option="tableOption" />
</template>
