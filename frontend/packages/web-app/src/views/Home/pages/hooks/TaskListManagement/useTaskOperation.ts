import { NiceModal } from '@rpa/components'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { throttle } from 'lodash-es'
import { h, ref } from 'vue'

import $loading from '@/utils/globalLoading'

import { deleteTask, enableTask, getScheduleLst, manualTrigger, taskFutureTime } from '@/api/task'
import GlobalModal from '@/components/GlobalModal/index.ts'
import { windowManager } from '@/platform'
import { TaskEditModal } from '@/views/Home/components/TaskEditModal'
import { useCommonOperate } from '@/views/Home/pages/hooks/useCommonOperate.tsx'

import type { resOption } from '../../../types'

export function useTaskOperation() {
  const taskListTableRef = ref(null)
  const showQueue = ref(false)
  const { t } = useTranslation()
  const { handleDeleteConfirm } = useCommonOperate()
  const taskEditModal = NiceModal.useModal(TaskEditModal)

  function getTableData(params) {
    return new Promise((resolve) => {
      getScheduleLst(params).then(({ data }: resOption) => {
        if (data) {
          const { total, records } = data
          resolve({ records, total })
        }
      })
    })
  }

  const handleNewTask = throttle(
    () => {
      taskEditModal.show({
        taskId: '',
        onRefresh: () => taskListTableRef.value?.fetchTableData(),
      })
    },
    1500,
    { leading: true, trailing: false },
  )

  const handleEditTask = throttle(
    ({ taskId }) => {
      taskEditModal.show({
        taskId,
        onRefresh: () => taskListTableRef.value?.fetchTableData(),
      })
    },
    1500,
    { leading: true, trailing: false },
  )

  function handleDeleteTask(record) {
    handleDeleteConfirm(t('deleteTaskConfirm', { name: record.name }), () => {
      deleteTask({ taskId: record.taskId }).then(() => {
        message.success(t('deleteSuccess'))
        taskListTableRef.value?.fetchTableData()
      })
    })
  }

  const handleEnableTask = async (record) => {
    const { enable, taskId } = record
    await enableTask({ taskId, enable: enable ? 1 : 0 })
    taskListTableRef.value?.fetchTableData()
  }

  const openSheculedTaskList = throttle(async (record) => {
    const { data } = await taskFutureTime({ task_id: record.taskId, times: 5 })
    const nextTimes = data?.next_exec_times || []
    const timeList = nextTimes.length
      ? nextTimes.map((item, index) => h('p', `${index + 1}. ${item}`))
      : h('p', t('noScheduleTasks'))

    GlobalModal.info({
      title: t('aboutExecuteTime'),
      content: h('div', { class: `max-h-96 overflow-y-auto ${record.enable ? '' : 'text-gray-600'}` }, timeList),
      onOk() {
        console.log('ok')
      },
      centered: true,
      keyboard: false,
    })
  }, 1500, { leading: true, trailing: false })

  const handleRunTask = throttle(
    (record) => {
      $loading.open({
        msg: t('startingTask'),
        timeout: 5,
      })
      manualTrigger({ task_id: record.taskId }).then(() => {
        message.success(t('startTaskSuccess'))
        $loading.close()
        windowManager.minimizeWindow()
      }, () => {
        $loading.close()
      })
    },
    1500,
    { leading: true, trailing: false },
  )

  const viewQueue = () => {
    showQueue.value = true
  }
  const hideQueue = () => {
    showQueue.value = false
  }

  return {
    viewQueue,
    taskListTableRef,
    showQueue,
    hideQueue,
    getTableData,
    handleNewTask,
    handleEditTask,
    deleteTask,
    handleDeleteTask,
    handleEnableTask,
    openSheculedTaskList,
    handleRunTask,
  }
}
