<script setup lang="ts">
import { ref } from 'vue'

import NormalTable from '@/components/NormalTable/index.vue'

import type { TaskFormState } from '../../types/index.ts'

import useTaskRecordOption from './hooks/useTaskRecordOption.tsx'

defineOptions({
  name: 'TaskRecordModal',
})

const props = defineProps<{
  open: boolean
  options: TaskFormState
}>()
const emit = defineEmits(['cancel'])

const tableOption = useTaskRecordOption(props.options.taskId)

const openModal = ref(props.open)
const options = ref(props.options)
</script>

<template>
  <a-modal
    v-model:open="openModal"
    :title="options.name"
    class="modal-taskRecordModal"
    :width="960"
    :after-close="() => emit('cancel')"
    :footer="null"
    centered
    @cancel="() => openModal = false"
  >
    <NormalTable :option="tableOption" />
  </a-modal>
</template>

<style lang="scss">
.modal-taskRecordModal {
  .ant-modal-content {
    min-height: 400px;
  }
}
</style>
