<script setup lang="ts">
import { Auth } from '@rpa/components/auth'

import NormalTable from '@/components/NormalTable/index.vue'
import { VIEW_OWN } from '@/constants/resource'

import useProjectTableOption from './hooks/ProjectManagement/useProjectTableOption'

const { homeTableRef, consultRef, tableOption } = useProjectTableOption(VIEW_OWN)
</script>

<template>
  <NormalTable ref="homeTableRef" :option="tableOption" />
  <Auth.Consult ref="consultRef" trigger="modal" />
</template>
