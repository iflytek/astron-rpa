import { HintIcon, NiceModal } from '@rpa/components'
import { message } from 'ant-design-vue'
import type { ColumnsType } from 'ant-design-vue/es/table/interface'
import dayjs from 'dayjs'
import { useTranslation } from 'i18next-vue'
import { h, reactive, ref } from 'vue'

import { deleteAPI, getApis } from '@/api/setting'
import GlobalModal from '@/components/GlobalModal/index.ts'
import type { resOption } from '@/views/Home/types'

import { NewApiModal } from './modals'

interface DataType {
  id: number | string
  api_key: string
  name: string
  createTime: string
  oper: string
}

export function useApiKeyManage() {
  const { t } = useTranslation()

  const currTableRef = ref(null)
  function refreshHomeTable() {
    if (currTableRef.value) {
      currTableRef.value?.fetchTableData()
    }
  }

  const columns: ColumnsType = [
    {
      title: t('name'),
      dataIndex: 'name',
      key: 'name',
      align: 'left',
      ellipsis: true,
    },
    {
      title: 'Key',
      dataIndex: 'api_key',
      key: 'api_key',
      align: 'left',
      ellipsis: true,
    },
    {
      title: t('common.createDate'),
      dataIndex: 'createTime',
      key: 'createTime',
      width: 120,
      ellipsis: true,
      customRender: ({ record }) => dayjs(record.createTime).format('YYYY-MM-DD'),
    },
    {
      title: t('operate'),
      dataIndex: 'oper',
      key: 'oper',
      align: 'center',
      width: 60,
      customRender: ({ record }) => h(HintIcon, { name: 'market-del', class: 'anticon', onClick: () => deleteApiKey(record) }),
    },
  ]
  const tableOption = reactive({
    refresh: true,
    getData: getTableData,
    buttonListAlign: 'right',
    buttonList: [{
      label: t('settingCenter.apiKeyManage.createApiKey'),
      clickFn: addApiKey,
      type: 'primary',
      hidden: false,
    }],
    tableProps: {
      columns,
      rowKey: 'id',
      scroll: { y: 180 },
      size: 'small',
    },
    params: {},
  })
  function getTableData(params) {
    return new Promise((resolve) => {
      getApis(params).then((res: resOption) => {
        const { data } = res
        if (data) {
          const { total, records } = data
          resolve({ records, total })
        }
      })
    })
  }
  function addApiKey() {
    NiceModal.show(NewApiModal, {
      onRefresh: () => refreshHomeTable(),
    })
  }
  function deleteApiKey(row: DataType) {
    GlobalModal.confirm({
      title: t('settingCenter.apiKeyManage.deleteApiKeyConfirm'),
      onOk: () => {
        deleteAPI({ id: row.id }).then(() => {
          message.success(t('deleteSuccess'))
          refreshHomeTable()
        })
      },
      centered: true,
      keyboard: false,
    })
  }

  return {
    currTableRef,
    tableOption,
    addApiKey,
  }
}
