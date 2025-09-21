<script setup lang="ts">
import NormalTable from '@/components/NormalTable/index.vue'
import { VIEW_OWN } from '@/constants/resource'

import useProjectTableOption from './hooks/ProjectManagement/useProjectTableOption'

const { homeTableRef, tableOption } = useProjectTableOption(VIEW_OWN)
</script>

<template>
  <NormalTable ref="homeTableRef" :option="tableOption" />
</template>
