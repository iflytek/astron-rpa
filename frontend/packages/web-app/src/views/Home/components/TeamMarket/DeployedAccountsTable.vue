<script setup lang="ts">
import { HintIcon, useTheme } from '@rpa/components'
import { h, reactive } from 'vue'

import { getDeployedAccounts } from '@/api/market'
import { NormalTable, type TableOption } from '@/components/NormalTable'

import type { cardAppItem } from '../../types/market'

interface deployAccountsMap {
  id: string
  creatorId: string
  name: string
  createTime: string
  appVersion: string
  isCreator: boolean | string | number
}

const props = defineProps<{
  allowSelect: boolean
  record: cardAppItem
}>()
const emit = defineEmits(['selectedIds'])

const { colorTheme } = useTheme()

const tableOption = reactive<TableOption>({
  refresh: false,
  page: false,
  getData: getDeployedAccounts,
  formListAlign: 'right',
  formList: [
    {
      componentType: 'input',
      bind: 'realName',
      // label: '名称',
      placeholder: '请输入名称',
      allowClear: true,
      size: 'middle',
      prefix: h(HintIcon, { name: 'search' }),
    },
  ],
  tableProps: {
    columns: [
      {
        title: '终端账号',
        dataIndex: 'name',
        key: 'name',
        ellipsis: true,
      },
      {
        title: '部署时间',
        dataIndex: 'createTime',
        key: 'createTime',
        ellipsis: true,
      },
      {
        title: '部署版本',
        dataIndex: 'appVersion',
        key: 'appVersion',
        ellipsis: true,
        customRender: ({ record }) => `版本${record.appVersion}`,
      },
    ],
    rowKey: 'id',
    scroll: { y: 120 },
    size: 'small',
    rowSelection: props.allowSelect
      ? {
          onChange: onSelectChange,
          getCheckboxProps: (record: deployAccountsMap) => ({
            disabled: record.isCreator,
            name: record.name,
          }),
        }
      : null,
  },
  params: {
    realName: '',
    appId: props.record.appId,
    marketId: props.record.marketId,
  },
})

function onSelectChange(_selectedIds: string[], selectedRows: deployAccountsMap[]) {
  const creatorIds = selectedRows.filter(item => !item.isCreator).map(item => item.creatorId)
  emit('selectedIds', creatorIds)
}
</script>

<template>
  <div class="deployed-accounts-table" :class="[colorTheme]">
    <div class="h-[300px]">
      <NormalTable :option="tableOption">
        <template #headerPrefix>
          <span class="font-bold">已部署账号</span>
        </template>
      </NormalTable>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.deployed-accounts-table {
  max-height: 400px;
  margin-top: 16px;
}

:deep(.nTable-header_btns) {
  justify-content: flex-start !important;

  .ant-btn {
    padding: 0;
    font-weight: bold;
    font-size: 14px;
  }
}

:deep(.ant-table) {
  background: transparent;
}

:deep(.ant-table-thead > tr > th) {
  background: #f3f3f7;
}

:deep(.ant-table-content) {
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.16);
}

.dark {
  :deep(.ant-table-thead > tr > th) {
    background: rgba(255, 255, 255, 0.08);
  }

  :deep(.ant-table-content) {
    border: 1px solid rgba(255, 255, 255, 0.16);
  }
}
</style>
