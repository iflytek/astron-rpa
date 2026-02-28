<script setup lang="ts">
import { DeleteOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import type { ColumnsType } from 'ant-design-vue/es/table'
import { useTranslation } from 'i18next-vue'
import { h, reactive, ref } from 'vue'

import { deleteCredential, getCredentialList } from '@/api/engine'
import GlobalModal from '@/components/GlobalModal'
import { NormalTable } from '@/components/NormalTable'
import type { TableOption } from '@/components/NormalTable'

import _VoucherModal from './VoucherModal.vue'

const VoucherModal = NiceModal.create(_VoucherModal)

const { t } = useTranslation()
const currTableRef = ref(null)

interface IVoucher {
  name: string
}

async function fetchList(params: { pageSize: number, pageNo: number }) {
  const list = await getCredentialList()
  return {
    records: list.slice((params.pageNo - 1) * params.pageSize, params.pageNo * params.pageSize),
    total: list.length,
  }
}

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
    customRender: () => '*******',
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
  getData: fetchList,
  params: {},
  tableProps: {
    columns,
    rowKey: 'name',
    scroll: { y: 180 },
    size: 'small',
  },
})

function deleteApiKey(row: IVoucher) {
  GlobalModal.confirm({
    title: t('settingCenter.voucherManage.deleteVoucherConfirm'),
    onOk: async () => {
      await deleteCredential(row.name)
      refreshTable()
    },
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

<template>
  <div class="flex flex-col gap-2 h-full overflow-hidden">
    <div>
      <a-button type="primary" @click="addVoucher">
        {{ $t('settingCenter.voucherManage.createVoucher') }}
      </a-button>
    </div>
    <div>{{ $t('settingCenter.voucherManage.tips') }}</div>
    <NormalTable ref="currTableRef" :option="tableOption" />
  </div>
</template>
