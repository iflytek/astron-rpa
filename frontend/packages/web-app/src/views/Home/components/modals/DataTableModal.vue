<script setup lang="ts">
import { NiceModal } from '@rpa/components'

import type { AnyObj } from '@/types/common'

import ReadonlyDataTable from './ReadonlyDataTable.vue'

const props = defineProps<{ record: AnyObj }>()

const modal = NiceModal.useModal()
</script>

<template>
  <a-drawer
    v-bind="NiceModal.antdDrawer(modal)"
    :title="`数据表格 - ${props.record.robotName}`"
    :width="628"
  >
    <ReadonlyDataTable :data-table-path="props.record.dataTablePath" />
  </a-drawer>
</template>
