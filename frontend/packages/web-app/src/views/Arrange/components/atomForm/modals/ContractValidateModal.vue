<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import type { ColumnsType } from 'ant-design-vue/es/table'

const props = defineProps<{
  dataList: Array<{ key: string, name: string, content: string }>
}>()

const modal = NiceModal.useModal()

const columns: ColumnsType = [{
  title: '要素名',
  dataIndex: 'name',
  key: 'name',
  width: 150,
  ellipsis: true,
}, {
  title: '抽取原文内容',
  key: 'content',
  dataIndex: 'content',
  ellipsis: true,
}]
</script>

<template>
  <a-modal
    v-bind="NiceModal.antdModal(modal)"
    title="抽取内容"
    class="validateModal"
    :footer="null"
    :width="500"
    :scroll="{ y: 300 }"
    centered
  >
    <a-table
      row-key="key"
      :columns="columns"
      :data-source="props.dataList"
      :pagination="false"
      size="small"
    />
  </a-modal>
</template>

<style lang="scss">
.validateModal {
  .ant-modal-body {
    height: 300px;
  }
}
</style>
