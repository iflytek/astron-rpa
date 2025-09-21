<script setup lang="ts">
import NormalTable from '@/components/NormalTable/index.vue'

import { useApiKeyManage } from './useApiKeyManage'

const { currTableRef, tableOption } = useApiKeyManage()
</script>

<template>
  <NormalTable ref="currTableRef" :option="tableOption" />
</template>
