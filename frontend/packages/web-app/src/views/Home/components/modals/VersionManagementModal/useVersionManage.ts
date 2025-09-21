import { NiceModal } from '@rpa/components'
import { useAsyncState } from '@vueuse/core'
import { Button, message } from 'ant-design-vue'
import dayjs from 'dayjs'
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
  const { state: versionLst, isLoading: spinning, executeImmediate } = useAsyncState(() => getVersionLst<versionMap[]>({ robotId: props.robotId }), [])

  const hasEditing = computed(() => versionLst.value.some(item => item.versionNum === 0))

  function getVersionDes(versionNum: number | string) {
    return versionNum === 0 ? '当前版本' : `版本 ${versionNum}`
  }

  // 判断当前是今天、昨天还是具体日期显示
  function getTimeDes(time) {
    if (dayjs(time).isSame(dayjs(), 'day')) {
      return `今天 ${dayjs(time).format('HH:mm')}`
    }
    if (dayjs(time).isSame(dayjs().subtract(1, 'day'), 'day')) {
      return `昨天 ${dayjs(time).format('HH:mm')}`
    }
    return dayjs(time).format('YYYY年MM月DD日 HH:mm')
  }

  const publish = debounce((item: versionMap) => {
    NiceModal.show(PublishModal, { robotId: item.robotId, onOk: () => executeImmediate() })
  }, 300)

  const recoverVersion = async (item: versionMap) => {
    await versionRecover({
      robotId: props.robotId,
      version: item.versionNum,
    })

    message.success('恢复编辑成功')
    executeImmediate()
  }

  const recoverEdit = debounce((item: versionMap) => {
    if (hasEditing.value) {
      const modal = GlobalModal.confirm({
        title: '当前版本未发布',
        content: '恢复版本前建议您发布当前版本，否则当前版本内容会被覆盖',
        footer: () => {
          return h(
            'div',
            { style: 'display: flex; justify-content: flex-end' },
            [
              h(Button, { onClick: () => { modal.destroy() }, style: 'margin-right: 10px' }, '取消'),
              h(Button, { onClick: () => { recoverVersion(item); modal.destroy() } }, '继续恢复'),
              h(Button, { onClick: () => { publish(item); modal.destroy() }, type: 'primary', style: 'margin-left: 10px' }, '去发版'),
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
      message.success('版本启用成功')
      await versionEnable({
        robotId: props.robotId,
        version: item.versionNum,
      })
      executeImmediate()
    }

    GlobalModal.confirm({
      title: '确认启用该版本？',
      okText: '确认',
      cancelText: '取消',
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
