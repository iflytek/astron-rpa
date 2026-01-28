<template>
  <div class="flex flex-col gap-2 h-full">
    <div>
      <a-button type="primary" @click="addVoucher">
        {{ $t('settingCenter.voucherManage.createVoucher') }}
      </a-button>
    </div>
    <div>{{ $t('settingCenter.voucherManage.tips') }}</div>
    <NormalTable ref="currTableRef" :option="tableOption" />
  </div>
</template>

<script setup lang="ts">
import { h, reactive, ref } from 'vue'
import type { ColumnsType } from 'ant-design-vue/es/table'
import { useTranslation } from 'i18next-vue'
import { DeleteOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'

import NormalTable from '@/components/NormalTable/index.vue'
import type { TableOption } from '@/types/normalTable'
import GlobalModal from '@/components/GlobalModal'

import _VoucherModal from './VoucherModal.vue'

const VoucherModal = NiceModal.create(_VoucherModal)

const { t } = useTranslation()
const currTableRef = ref(null)

interface IVoucher {
  id: string
  name: string
  value: string
}

const data: IVoucher[] = [
  {
    id: '1',
    name: 'username',
    value: 'admin',
  },
  {
    id: '2',
    name: 'password',
    value: '123456',
  },
]

const columns: ColumnsType = [
  {
    title: t('voucherName'),
    dataIndex: 'name',
    key: 'name',
    align: 'left',
    width: 80,
    ellipsis: true,
  },
  {
    title: t('password'),
    dataIndex: 'password',
    key: 'password',
    width: 120,
    ellipsis: true,
    customRender: () => "*******",
  },
  {
    title: t('operate'),
    dataIndex: 'oper',
    key: 'oper',
    align: 'center',
    width: 60,
    customRender: ({ record }) => h(DeleteOutlined, { onClick: () => deleteApiKey(record) }),
  },
]

const tableOption = reactive<TableOption>({
  refresh: true,
  getData: () => Promise.resolve({ records: data, total: data.length }),
  params: {},
  tableProps: {
    columns,
    rowKey: 'id',
    scroll: { y: 180 },
    size: 'small',
  },
})

function deleteApiKey(row: IVoucher) {
  GlobalModal.confirm({
    title: t('settingCenter.voucherManage.deleteVoucherConfirm'),
    onOk: () => {},
    centered: true,
    keyboard: false,
  })
}

function addVoucher() {
  NiceModal.show(VoucherModal, {
    onRefresh: () => refreshTable(),
  })
}

function refreshTable() {
  currTableRef.value?.fetchTableData()
}
</script>
