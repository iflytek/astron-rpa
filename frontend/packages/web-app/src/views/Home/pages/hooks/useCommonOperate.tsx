import { ExclamationCircleOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import { Button, message } from 'ant-design-vue'
import { h } from 'vue'

import $loading from '@/utils/globalLoading'

import { releaseCheck, releaseCheckWithPublish } from '@/api/market'
import { startExecutor } from '@/api/resource'
import GlobalModal from '@/components/GlobalModal/index.ts'
import { VIEW_ALL, VIEW_OTHER, VIEW_OWN } from '@/constants/resource'
import { windowManager } from '@/platform'
import { useRunlogStore } from '@/stores/useRunlogStore'
import { useRunningStore } from '@/stores/useRunningStore'
import useUserSettingStore from '@/stores/useUserSetting.ts'
import type { AnyObj, Fun } from '@/types/common'
import { LogModal, TaskReferInfoModal } from '@/views/Home/components/modals'

// 当前tab值
function tabValue(item: string) {
  let viewType = VIEW_ALL
  switch (item) {
    case VIEW_ALL:
      viewType = VIEW_ALL
      break
    case VIEW_OWN:
      viewType = VIEW_OWN
      break
    default:
      viewType = VIEW_OTHER
      break
  }
  return viewType
}

function getCookie(name: string) {
  const arr = document.cookie.match(new RegExp(`(^| )${name}=([^;]*)(;|$)`))
  if (arr != null)
    return unescape(arr[2])
  return null
}

// 运行
export async function handleRun(editObj: AnyObj) {
  $loading.open({ msg: '加载中' })
  // 获取日志窗口隐藏和录屏配置数据
  try {
    await startExecutor({
      project_id: editObj.robotId,
      exec_position: editObj.exec_position || 'PROJECT_LIST',
      jwt: getCookie('jwt'),
      recording_config: JSON.stringify(
        useUserSettingStore().userSetting.videoForm,
      ),
      hide_log_window:
        useUserSettingStore().userSetting.commonSetting?.hideLogWindow || false,
      project_name: editObj.robotName,
      open_virtual_desk: editObj.open_virtual_desk || false,
    })
    message.info('开始运行')
    windowManager.minimizeWindow()
    useRunningStore().setRunning('run')
    useRunningStore().setRunProjectId(editObj.robotId)
  }
  catch (error) {
    console.error(error)
  }

  $loading.close()
}

export function useCommonOperate() {
  function handleCheck({ type = 'modal', record }) {
    NiceModal.show(LogModal, {
      record,
      type: type as 'modal' | 'drawer',
      onClearLogs: () => useRunlogStore().clearLogs(),
    })
  }

  function handleDeleteConfirm(content: any, cb: Fun) {
    return new Promise((resolve) => {
      GlobalModal.confirm({
        title: '删除',
        icon: h(ExclamationCircleOutlined),
        content,
        okType: 'danger',
        onOk: () => {
          cb && cb()
          resolve(true)
        },
        onCancel: () => {
          console.log('Cancel')
        },
      })
    })
  }

  function useApplicationConfirm(content: any, cb: Fun) {
    return new Promise((resolve) => {
      GlobalModal.confirm({
        title: '提示',
        content,
        onOk: () => {
          cb && cb()
          resolve(true)
        },
        onCancel: () => {
          console.log('Cancel')
        },
        centered: true,
        keyboard: false,
      })
    })
  }

  function applicationReleaseCheck(
    checkParams: { robotId: string, version: string | number, source?: string },
    applicationCallback: (data?: any) => void,
    callback?: () => void,
    cancelCallback?: () => void,
  ) {
    const checkFn
      = checkParams.source === 'publish' ? releaseCheckWithPublish : releaseCheck
    checkFn({ robotId: checkParams.robotId, version: checkParams.version })
      .then((res) => {
        if (res.code === '000000') {
          const needApplication = !!res.data
          if (!needApplication) {
            callback && callback()
            return
          }

          // 首次上架申请通过后，未发版的前提下再次分享至其他团队市场，不需要再次发起申请
          const content
            = checkParams.source === 'publish'
              ? '企业管理员开启了上架前审核，审核通过后方可分享至应用市场，是否同时发起上架申请？'
              : '企业管理员开启了上架前审核，审核通过后方可分享至应用市场，请确认是否发起申请？'
          GlobalModal.confirm({
            title: '提示',
            content,
            onOk: () => applicationCallback(res.data),
            onCancel: () => cancelCallback && cancelCallback(),
          })
        }
      })
      .catch(() => {
        cancelCallback && cancelCallback()
      })
  }

  function openTaskReferInfoModal(taskReferInfoList: Array<AnyObj>) {
    NiceModal.show(TaskReferInfoModal, { taskReferInfoList })
  }

  function getSituationContent(
    source: string,
    situation: number,
    taskReferInfoList: Array<AnyObj>,
  ) {
    switch (situation) {
      case 1:
        return '机器人删除后不可恢复，确认删除么？'
      case 2:
        return `删除后执行器列表页中的机器人也将被删除，确认删除么？`
      case 3:
        return (
          <div>
            <div>{`${source === 'design' ? '删除后执行器列表页中的机器人也将被删除' : '机器人删除后不可恢复'}，确认删除么？`}</div>
            <p style="color: #aaa; font-size: 14px;margin: 10px 0 0 0;">{`检测到该机器人被${taskReferInfoList[0].taskName}等计划任务引用，继续删除会同时解除计划任务中的引用关系，当计划任务仅存在一个引用关系时，计划任务也会被删除。`}</p>
            <Button
              type="link"
              style="padding: 0;"
              onClick={() => openTaskReferInfoModal(taskReferInfoList)}
            >
              查看机器人的引用关系表
            </Button>
          </div>
        )
      default:
        break
    }
  }
  return {
    tabValue,
    handleCheck,
    handleDeleteConfirm,
    applicationReleaseCheck,
    useApplicationConfirm,
    getSituationContent,
  }
}
