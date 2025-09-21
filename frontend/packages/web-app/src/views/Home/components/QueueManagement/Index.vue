<!-- @format -->

<script setup>
import { Drawer } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { defineEmits, onBeforeUnmount, ref } from 'vue'

import NormalTable from '@/components/NormalTable/index.vue'

import useQueueTable from './useQueueTable.tsx'

defineOptions({
  name: 'QueueModal',
})
const emit = defineEmits(['cancel'])
const { t } = useTranslation()
const showModal = ref(true)
const { tableOption, queueTableRef, intervalRefresh } = useQueueTable()
const interval = intervalRefresh()
function cancel() {
  showModal.value = false
  interval.clear()
}
function afterClose(show) {
  show === false && emit('cancel')
}
onBeforeUnmount(() => {
  interval.clear()
})
</script>

<template>
  <Drawer
    v-model:open="showModal"
    :title="t('queueList')"
    class="queueModal"
    placement="right"
    :width="900"
    :footer="null"
    @after-open-change="afterClose"
    @cancel="cancel"
  >
    <NormalTable ref="queueTableRef" :option="tableOption" />
  </Drawer>
</template>

<style lang="scss">
.queueModal {
  height: 100vh;
  position: absolute;
  right: 0px;
  top: 0px;
  padding-bottom: 0px;
  .ant-modal-content {
    height: 100%;
    .ant-modal-header {
      padding-left: 32px;
    }
    .ant-modal-close {
      position: absolute;
      left: 24px;
      top: 22px;
    }
    .ant-modal-body {
      height: calc(100% - 55px);
    }
  }
}
</style>
