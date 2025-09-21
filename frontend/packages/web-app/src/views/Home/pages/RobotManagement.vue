<script setup lang="ts">
import NormalTable from '@/components/NormalTable/index.vue'

import RecordContainer from '../components/RecordContainer.vue'

import useRobotTableOption from './hooks/RobotManagement/useRobotTableOption.tsx'

const { homeTableRef, tableOption } = useRobotTableOption()
</script>

<template>
  <RecordContainer>
    <NormalTable ref="homeTableRef" :option="tableOption" />
  </RecordContainer>
</template>
