import { NiceModal } from '@rpa/components'
import { message } from 'ant-design-vue'

import { deleteRobot, getRobotLst, isRobotInTask, updateRobot } from '@/api/robot'
import { RobotConfigTaskModal } from '@/components/RobotConfigTaskModal'
import { ActuatorRobotDetailModal } from '@/components/RobotDetail'
import { useRobotUpdate } from '@/views/Home/components/TeamMarket/hooks/useRobotUpdate'
import { useCommonOperate } from '@/views/Home/pages/hooks/useCommonOperate.tsx'

import type { resOption } from '../../../types'

export default function useRobotOperation(homeTableRef, refreshHomeTable) {
  const { handleDeleteConfirm, getSituationContent } = useCommonOperate()
  const { getInitUpdateIds } = useRobotUpdate('robot', homeTableRef)

  function getTableData(params) {
    return new Promise((resolve) => {
      getRobotLst(params).then((res: resOption) => {
        const { data } = res
        if (data) {
          const { total, records } = data
          getInitUpdateIds(records)
          resolve({ records, total })
        }
      })
    })
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
  // 删除
  function handleDeleteRobot(editObj) {
    const { robotId } = editObj
    isRobotInTask({ robotId }).then((result: resOption) => {
      const { data } = result
      if (data) {
        let { situation, taskReferInfoList, robotId } = data
        taskReferInfoList = taskReferInfoList?.filter((item, index, self) =>
          index === self.findIndex(t => t.taskName === item.taskName),
        )
        handleDeleteConfirm(getSituationContent('execute', situation, taskReferInfoList), () => {
          deleteRobot({
            robotId,
            situation,
            taskIds: taskReferInfoList?.map(item => item.taskId).join(',') || '',
          }).then(() => {
            message.success('删除成功')
            refreshHomeTable()
          })
        })
      }
    })
  }
  function handleRobotUpdate(record) {
    updateRobot({
      robotId: record.robotId,
    }).then(() => {
      message.success('更新成功')
      refreshHomeTable()
    })
  }

  function expiredTip(record) {
    const expired = record.usePermission === 0
    if (expired) {
      message.warning('权限不足，请至应用市场申请使用')
    }
    return expired
  }
  return {
    getTableData,
    onSelectChange,
    importRobot,
    handleToConfig,
    openRobotDetailModal,
    handleDeleteRobot,
    handleRobotUpdate,
    expiredTip,
  }
}
