<script setup lang="tsx">
import type { ColumnsType } from 'ant-design-vue/es/table/interface'
import { useTranslation } from 'i18next-vue'
import { computed, ref } from 'vue'

import { usePythonPackageStore } from '@/stores/usePythonPackageStore'

import { useManagePython } from '../hooks/useManagePython'

const { t } = useTranslation()
const pythonPackageStore = usePythonPackageStore()

const { upgradeModal, uninstallModal } = useManagePython()

const moreOpts = [
  {
    key: 'edit',
    text: t('upgrade'),
    clickFn: id => upgradeModal([id]),
  },
  {
    key: 'del',
    text: t('uninstall'),
    clickFn: id => uninstallModal([id]),
  },
]

const columns: ColumnsType = [
  {
    title: t('packageName'),
    dataIndex: 'packageName',
    key: 'packageName',
    align: 'left',
    ellipsis: true,
  },
  {
    title: t('packageVersion'),
    dataIndex: 'packageVersion',
    key: 'packageVersion',
    align: 'left',
    width: 60,
    ellipsis: true,
  },
  {
    title: t('operate'),
    dataIndex: 'oper',
    key: 'oper',
    align: 'center',
    width: 100,
    customRender: ({ record }) => (
      <div class="menu">
        {moreOpts.map(op => (
          <a class="oper-btn" key={op.key} onClick={() => op.clickFn(record.id)}>
            {op.text}
          </a>
        ))}
      </div>
    ),
  },
]

const searchValue = ref('')

const dataSource = computed(() => {
  if (!searchValue.value) {
    return pythonPackageStore.pythonPackageList
  }

  return pythonPackageStore.pythonPackageList.filter(item =>
    item.packageName.toLowerCase().includes(searchValue.value.toLowerCase()),
  )
})
</script>

<template>
  <a-input
    v-model:value="searchValue"
    allow-clear
    class="flex-1 mb-3 leading-[22px]"
    :placeholder="$t('common.enter')"
  >
    <template #prefix>
      <rpa-icon name="search" class="dark:text-[rgba(255,255,255,0.25)]" />
    </template>
  </a-input>
  <a-table
    size="small"
    :data-source="dataSource"
    :columns="columns"
    :pagination="{ pageSize: 4, size: 'small' }"
    :row-key="(record) => record.id"
    :total="dataSource.length"
    :row-class-name="() => 'tableRow'"
  />
</template>

<style lang="scss">
.pythonDependence {
  height: 100%;
  position: relative;

  &_spin {
    position: absolute;
    top: 45%;
    left: 45%;
  }

  .ant-table-thead > tr > th {
    font-size: 12px;
    color: var(--table-head-default);
    background: transparent;
  }

  .ant-table-tbody > tr > td {
    font-size: 14px;
    color: var(--table-body-default);
  }

  .ant-table-thead > tr > th,
  .ant-table-tbody > tr > td {
    padding: 14px 16px;
  }

  .ant-table-pagination.ant-pagination {
    margin-bottom: 0;
  }

  .oper-btn {
    color: $color-primary;
    margin-right: 6px;
  }
}
</style>
