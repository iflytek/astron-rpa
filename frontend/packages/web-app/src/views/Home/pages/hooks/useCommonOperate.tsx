import { ExclamationCircleOutlined } from '@ant-design/icons-vue'
import { NiceModal } from '@rpa/components'
import { Button } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { h } from 'vue'
import type { JSX } from 'vue/jsx-runtime'

import i18next from '@/plugins/i18next'

import $loading from '@/utils/globalLoading'

import { releaseCheck, releaseCheckWithPublish } from '@/api/market'
import GlobalModal from '@/components/GlobalModal/index.ts'
import { VIEW_ALL, VIEW_OTHER, VIEW_OWN } from '@/constants/resource'
import { useRunlogStore } from '@/stores/useRunlogStore'
import { useRunningStore } from '@/stores/useRunningStore'
import type { AnyObj, Fun } from '@/types/common'
import { DataTableModal, LogModal, TaskReferInfoModal } from '@/views/Home/components/modals'

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

// 运行
export async function handleRun(editObj: AnyObj) {
  $loading.open({ msg: i18next.t('loading') })
  await useRunningStore().startSlice(editObj)
  $loading.close()
}

export function useCommonOperate() {
  const { t } = useTranslation()
  function handleOpenDataTable(record) {
    NiceModal.show(DataTableModal, { record })
  }

  function handleCheck({ type = 'modal', record }) {
    NiceModal.show(LogModal, {
      record,
      type: type as 'modal' | 'drawer',
      onClearLogs: () => useRunlogStore().clearLogs(),
    })
  }

  function handleDeleteConfirm(content: string | JSX.Element) {
    return new Promise<boolean>((resolve) => {
      GlobalModal.confirm({
        title: t('delete'),
        icon: h(ExclamationCircleOutlined),
        content,
        okType: 'danger',
        onOk: () => resolve(true),
        onCancel: () => resolve(false),
      })
    })
  }

  function useApplicationConfirm(content: any, cb: Fun) {
    return new Promise((resolve) => {
      GlobalModal.confirm({
        title: t('prompt'),
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
              ? t('market.releaseAuditPromptPublish')
              : t('market.releaseAuditPromptShare')
          GlobalModal.confirm({
            title: t('prompt'),
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
        return t('market.deleteAppNoRecoverConfirm')
      case 2:
        return t('market.deleteAlsoRemoveExecutorConfirm')
      case 3:
      {
        const contentPrefix = source === 'design'
          ? t('market.deleteAlsoRemoveExecutorPrefix')
          : t('market.deleteAppNoRecoverPrefix')
        return (
          <div>
            <div>{t('market.deleteConfirmWithPrefix', { prefix: contentPrefix })}</div>
            <p style="color: #aaa; font-size: 14px;margin: 10px 0 0 0;">{t('market.deleteTaskReferenceWarning', { taskName: taskReferInfoList[0].taskName })}</p>
            <Button
              type="link"
              style="padding: 0;"
              onClick={() => openTaskReferInfoModal(taskReferInfoList)}
            >
              {t('market.viewTaskReferences')}
            </Button>
          </div>
        )
      }
      default:
        break
    }
  }
  return {
    tabValue,
    handleCheck,
    handleDeleteConfirm,
    handleOpenDataTable,
    applicationReleaseCheck,
    useApplicationConfirm,
    getSituationContent,
  }
}
