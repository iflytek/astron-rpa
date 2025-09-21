import { NiceModal } from '@rpa/components'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed, ref } from 'vue'

import { getTaskQueueList, removeTaskQueue } from '@/api/task'
import { QueueConfigModal } from '@/components/QueueConfigModal'
import { useCommonOperate } from '@/views/Home/pages/hooks/useCommonOperate.tsx'

export default function useQueueOperation() {
  const { handleDeleteConfirm } = useCommonOperate()
  const { t } = useTranslation()
  const selectedRowKeys = ref([])
  const queueTableRef = ref(null)

  const rowSelection = computed(() => {
    return {
      onChange: (keys: string[], _selectedRows: any[]) => {
        selectedRowKeys.value = keys
      },
      selectedRowKeys: selectedRowKeys.value,
    }
  })

  // 获取队列数据
  async function getTableData(params) {
    const { data } = await getTaskQueueList(params)
    const records = data?.current_tasks || []
    const total = data?.pagination.total || 0
    return {
      records,
      total,
    }
  }

  // 删除队列中的任务
  async function deleteQueueTask(record) {
    const confirm = await handleDeleteConfirm(t('deleteConfirm'), () => {})
    if (!confirm)
      return

    await removeTaskQueue({ unique_id: [record.unique_id] })
    message.success(t('deleteSuccess'))
    queueTableRef.value?.fetchTableData()
  }

  const batchDelete = async () => {
    if (selectedRowKeys.value.length === 0) {
      message.warning(t('selectOne'))
      return
    }
    const confirm = await handleDeleteConfirm(t('deleteConfirm'), () => {})
    console.log('confirm: ', confirm)
    if (!confirm)
      return

    await removeTaskQueue({ unique_id: selectedRowKeys.value })
    message.success(t('batchDeleteSuccess'))
    queueTableRef.value?.fetchTableData()
    selectedRowKeys.value = []
  }

  const queueSetting = async () => {
    NiceModal.show(QueueConfigModal, {
      onOk: () => queueTableRef.value?.fetchTableData(),
    })
  }

  const refreshQueueList = () => {
    queueTableRef.value?.fetchTableData()
  }

  const intervalRefresh = () => {
    const t = setInterval(() => queueTableRef.value?.fetchTableData(), 10 * 1000) // 每10秒刷新一次;
    return { clear: () => clearInterval(t) }
  }

  return {
    queueTableRef,
    rowSelection,
    deleteQueueTask,
    getTableData,
    batchDelete,
    queueSetting,
    refreshQueueList,
    intervalRefresh,
  }
}
