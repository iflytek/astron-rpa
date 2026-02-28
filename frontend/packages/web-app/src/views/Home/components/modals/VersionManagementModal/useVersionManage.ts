import { NiceModal } from '@rpa/components'
import { useAsyncState } from '@vueuse/core'
import { Button, message } from 'ant-design-vue'
import dayjs from 'dayjs'
import { useTranslation } from 'i18next-vue'
import { debounce } from 'lodash-es'
import { computed, h } from 'vue'

import { getVersionLst, versionEnable, versionRecover } from '@/api/project'
import GlobalModal from '@/components/GlobalModal/index.ts'
import { PublishModal } from '@/components/PublishComponents'

interface versionMap {
  robotId: string
  updateTime: string
  versionNum: number | string
  updateLog: string
  online: string
}

export default function useVersionManage(props) {
  const { t } = useTranslation()
  const { state: versionLst, isLoading: spinning, executeImmediate } = useAsyncState(() => getVersionLst<versionMap[]>({ robotId: props.robotId }), [])

  const hasEditing = computed(() => versionLst.value.some(item => item.versionNum === 0))

  function getVersionDes(versionNum: number | string) {
    return versionNum === 0 ? t('currentVersion') : t('versionWithNumber', { version: versionNum })
  }

  // 判断当前是今天、昨天还是具体日期显示
  function getTimeDes(time) {
    if (dayjs(time).isSame(dayjs(), 'day')) {
      return `${t('today')} ${dayjs(time).format('HH:mm')}`
    }
    if (dayjs(time).isSame(dayjs().subtract(1, 'day'), 'day')) {
      return `${t('yesterday')} ${dayjs(time).format('HH:mm')}`
    }
    return dayjs(time).format(t('common.dateTimeFormat'))
  }

  const publish = debounce((item: versionMap) => {
    NiceModal.show(PublishModal, { robotId: item.robotId, onOk: () => executeImmediate() })
  }, 300)

  const recoverVersion = async (item: versionMap) => {
    await versionRecover({
      robotId: props.robotId,
      version: item.versionNum,
    })

    message.success(t('versionManage.recoverEditSuccess'))
    executeImmediate()
  }

  const recoverEdit = debounce((item: versionMap) => {
    if (hasEditing.value) {
      const modal = GlobalModal.confirm({
        title: t('versionManage.currentVersionUnreleasedTitle'),
        content: t('versionManage.currentVersionUnreleasedContent'),
        footer: () => {
          return h(
            'div',
            { style: 'display: flex; justify-content: flex-end' },
            [
              h(Button, { onClick: () => { modal.destroy() }, style: 'margin-right: 10px' }, t('cancel')),
              h(Button, { onClick: () => { recoverVersion(item); modal.destroy() } }, t('versionManage.continueRecover')),
              h(Button, { onClick: () => { publish(item); modal.destroy() }, type: 'primary', style: 'margin-left: 10px' }, t('versionManage.goPublish')),
            ],
          )
        },
        closable: true,
        centered: true,
        keyboard: false,
      })
      return
    }
    recoverVersion(item)
  }, 300)

  const enableVersion = debounce((item: versionMap) => {
    const onOk = async () => {
      message.success(t('versionManage.enableVersionSuccess'))
      await versionEnable({
        robotId: props.robotId,
        version: item.versionNum,
      })
      executeImmediate()
    }

    GlobalModal.confirm({
      title: t('versionManage.confirmEnableVersion'),
      okText: t('confirm'),
      cancelText: t('cancel'),
      onOk,
      centered: true,
      keyboard: false,
    })
  }, 300)

  return {
    spinning,
    hasEditing,
    versionLst,
    getVersionDes,
    getTimeDes,
    publish,
    recoverEdit,
    enableVersion,
  }
}
