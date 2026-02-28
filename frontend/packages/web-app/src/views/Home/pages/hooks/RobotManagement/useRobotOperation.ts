import { NiceModal } from '@rpa/components'
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'

import { deleteRobot, getRobotLst, isRobotInTask, updateRobot } from '@/api/robot'
import { RobotConfigTaskModal } from '@/components/RobotConfigTaskModal'
import { ActuatorRobotDetailModal } from '@/components/RobotDetail'
import { McpConfigModal } from '@/views/Home/components/modals/index'
import { useRobotUpdate } from '@/views/Home/components/TeamMarket/hooks/useRobotUpdate'
import { useCommonOperate } from '@/views/Home/pages/hooks/useCommonOperate.tsx'

export default function useRobotOperation(homeTableRef, refreshHomeTable, refreshWithDelete) {
  const { handleDeleteConfirm, getSituationContent } = useCommonOperate()
  const { getInitUpdateIds } = useRobotUpdate('robot', homeTableRef)
  const { t } = useTranslation()

  async function getTableData(params) {
    const data = await getRobotLst(params)
    getInitUpdateIds(data.records)
    return data
  }

  function onSelectChange(selectedIds: string[]) {
    console.log(selectedIds)
  }
  function importRobot() {
    console.log('importRobot')
  }
  function handleToConfig(record) {
    NiceModal.show(RobotConfigTaskModal, {
      robotId: record.robotId,
    })
  }
  function openRobotDetailModal(record) {
    NiceModal.show(ActuatorRobotDetailModal, {
      robotId: record.robotId,
      version: record.version,
    })
  }
  function openMcpConfigModal(record) {
    NiceModal.show(McpConfigModal, { record })
  }

  // 删除
  async function handleDeleteRobot(editObj) {
    const { robotId } = editObj
    const data = await isRobotInTask({ robotId })
    if (data) {
      let { situation, taskReferInfoList, robotId } = data
      taskReferInfoList = taskReferInfoList?.filter((item, index, self) =>
        index === self.findIndex(t => t.taskName === item.taskName),
      )
      const confirm = await handleDeleteConfirm(getSituationContent('execute', situation, taskReferInfoList))
      if (!confirm) {
        return
      }
      await deleteRobot({
        robotId,
        situation,
        taskIds: taskReferInfoList?.map(item => item.taskId).join(',') || '',
      })
      message.success(t('common.deleteSuccess'))
      refreshWithDelete()
    }
  }

  async function handleRobotUpdate(record) {
    await updateRobot({ robotId: record.robotId })
    message.success(t('common.updateSuccess'))
    refreshHomeTable()
  }

  function expiredTip(record) {
    const expired = record.usePermission === 0
    if (expired) {
      message.warning(t('market.insufficientPermissionApplyInMarket'))
    }
    return expired
  }

  return {
    getTableData,
    onSelectChange,
    importRobot,
    handleToConfig,
    openRobotDetailModal,
    openMcpConfigModal,
    handleDeleteRobot,
    handleRobotUpdate,
    expiredTip,
  }
}
