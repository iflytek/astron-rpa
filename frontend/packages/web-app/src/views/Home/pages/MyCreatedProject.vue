<script setup lang="ts">
import NormalTable from '@/components/NormalTable/index.vue'
import { VIEW_OWN } from '@/constants/resource'
import { Auth } from '@rpa/components/auth'

import useProjectTableOption from './hooks/ProjectManagement/useProjectTableOption'

const { homeTableRef, consultRef, tableOption } = useProjectTableOption(VIEW_OWN)
</script>

<template>
  <NormalTable ref="homeTableRef" :option="tableOption" />
  <Auth.Consult ref="consultRef" :trigger="'modal'"/>
</template>
