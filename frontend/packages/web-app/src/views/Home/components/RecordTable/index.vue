<script setup>
import NormalTable from '@/components/NormalTable/index.vue'

import useRecordTableOption from './hooks/useRecordTableOption.tsx'

const props = defineProps({
  robotId: String,
})

const { homeTableRef, tableOption } = useRecordTableOption(props)
</script>

<template>
  <NormalTable ref="homeTableRef" :option="tableOption" />
</template>

<style lang="scss" scoped>
</style>
