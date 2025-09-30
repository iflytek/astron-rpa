import { Icon, NiceModal } from '@rpa/components'
import { Button, message, Tooltip } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import type { Ref } from 'vue'
import { computed, h, ref } from 'vue'

import $loading from '@/utils/globalLoading'

import { getTeams } from '@/api/market'
import { delectProject, isInTask } from '@/api/project'
import { PublishModal } from '@/components/PublishComponents'
import { fromIcon } from '@/components/PublishComponents/utils'
import { DesignerRobotDetailModal } from '@/components/RobotDetail'
import { ARRANGE } from '@/constants/menu'
import { ROBOT_EDITING } from '@/constants/resource'
import { useRoutePush } from '@/hooks/useCommonRoute'
import type { AnyObj } from '@/types/common'
import { CopyModal, RenameModal, VersionManagementModal } from '@/views/Home/components/modals/index'
import OperMenu from '@/views/Home/components/OperMenu.vue'
import { ShareRobotModal } from '@/views/Home/components/ShareRobotModal'
import StatusCircle from '@/views/Home/components/StatusCircle.vue'
import { PENDING } from '@/views/Home/components/TeamMarket/config/market'
import type { resOption } from '@/views/Home/types'

import { handleRun, useCommonOperate } from '../useCommonOperate'

export function useProjectOperate(homeTableRef?: Ref) {
  function refreshHomeTable() {
    if (homeTableRef.value) {
      homeTableRef.value?.fetchTableData()
    }
  }
  const { t } = useTranslation()
  const { handleDeleteConfirm, getSituationContent } = useCommonOperate()

  const currHoverId = ref('')

  const createColumns = computed(() => ([
    {
      title: t('projectName'),
      dataIndex: 'robotName',
      key: 'robotName',
      ellipsis: true,
      customRender: ({ record }) => (
        <div class="flex items-center gap-2 overflow-hidden w-full">
          <Tooltip title={`ID：${record.robotId}`}>
            <span class="truncate flex-1">{ record.robotName }</span>
          </Tooltip>
          {currHoverId.value === record.robotId && (
            <Tooltip title={t('rename')}>
              <Icon name="projedit" class="hover:text-primary cursor-pointer" onClick={() => handleRename(record)} />
            </Tooltip>
          )}
        </div>
      ),
    },
    {
      title: t('updated'),
      dataIndex: 'updateTime',
      key: 'updateTime',
      width: 150,
      ellipsis: true,
      sorter: true,
    },
    {
      title: t('common.publishStatus'),
      dataIndex: 'publishStatus',
      key: 'publishStatus',
      customRender: ({ record }) => <StatusCircle type={`${record.publishStatus}`} />,
    },
    {
      title: t('common.enabled'),
      dataIndex: 'version',
      key: 'version',
      customRender: ({ record }) => {
        const hasVersion = Number(record.version) !== 0
        const versionDes = hasVersion ? `V${record.version}` : '--'
        return (
          <span class="inline-flex gap-2 items-center">
            <span>{versionDes}</span>
            {hasVersion && (
              <Tooltip title={t('common.versionManagement')}>
                <Button onClick={() => versionManage(record)} size="small" class="!p-0 flex items-center justify-center border-none bg-transparent">
                  <Icon name="history" size="16px" />
                </Button>
              </Tooltip>
            )}
          </span>
        )
      },
    },
    {
      title: t('common.latestVersion'),
      dataIndex: 'latestVersion',
      key: 'latestVersion',
      ellipsis: true,
      customRender: ({ record }) => Number(record?.latestVersion) === 0 ? '--' : `V${record?.latestVersion}`,
    },
    {
      title: t('operate'),
      dataIndex: 'oper',
      key: 'oper',
      width: 150,
      customRender: ({ record }) => {
        return <OperMenu moreOpts={projectMoreOpts} baseOpts={projectBaseOpts} row={record} />
      },
    },
  ]))

  const projectBaseOpts = [
    {
      key: 'run',
      text: 'run',
      clickFn: (record) => { handleRun({ ...record, exec_position: 'PROJECT_LIST' }) },
      icon: h(<Icon name="play-circle-stroke" size="16px" />),
    },
    {
      key: 'edit',
      text: 'edit',
      clickFn: handleEdit,
      icon: h(<Icon name="projedit" size="16px" />),
    },
  ]

  const projectMoreOpts = [
    {
      key: 'createCopy',
      text: 'createCopy',
      icon: h(<Icon name="create-copy" size="16px" />),
      clickFn: createCopy,
    },
    {
      key: 'publish',
      text: 'release',
      icon: h(<Icon name="tools-publish" size="16px" />),
      clickFn: publish,
    },
    {
      key: 'share',
      text: 'common.share',
      icon: h(<Icon name="share" size="16px" />),
      clickFn: shareToMarket,
      disableFn: (row: AnyObj) => {
        return row.applicationStatus === PENDING
      },
      disableTip: 'designerManage.onShelfApplication',
    },
    {
      key: 'virtualRun',
      text: 'virtualDesktopRunning',
      icon: h(<Icon name="virtual-desktop" size="16px" />),
      clickFn: (record) => { handleRun({ ...record, exec_position: 'PROJECT_LIST', open_virtual_desk: true }) },
    },
    {
      key: 'detail',
      text: 'checkDetails',
      icon: h(<Icon name="robot" size="16px" />),
      clickFn: openDetailModal,
    },
    {
      key: 'del',
      text: 'delete',
      icon: h(<Icon name="market-del" size="16px" />),
      clickFn: handleDeleteProject,
    },
  ]

  // 编辑
  function handleEdit(editObj: AnyObj) {
    const { robotId, robotName, editEnable } = editObj
    if (!editEnable) {
      message.info('当前机器人未开放源码，无法进行编辑，升级账户后可获得编辑权限')
      return
    }
    useRoutePush({ name: ARRANGE, query: { projectId: robotId, projectName: robotName } })
  }

  // 创建副本
  function createCopy(editObj: AnyObj) {
    NiceModal.show(CopyModal, {
      robotId: editObj.robotId,
      robotName: editObj.robotName,
      onRefresh: () => refreshHomeTable(),
    })
  }

  // 重命名
  function handleRename(editObj: AnyObj) {
    NiceModal.show(RenameModal, {
      robotId: editObj.robotId,
      robotName: editObj.robotName,
      onRefresh: () => refreshHomeTable(),
    })
  }

  // 版本管理
  function versionManage(editObj: AnyObj) {
    NiceModal.show(VersionManagementModal, {
      robotId: editObj.robotId,
      onRefresh: () => refreshHomeTable(),
    })
  }

  // 发版
  function publish(editObj: AnyObj) {
    NiceModal.show(PublishModal, { robotId: editObj.robotId, onOk: () => refreshHomeTable() })
  }

  // 分享
  function shareToMarket(editObj: AnyObj) {
    if (editObj.publishStatus === ROBOT_EDITING) {
      message.info('机器人编辑中暂不支持分享')
      return
    }
    $loading.open({ msg: '加载中...' })
    getTeams().then((res: resOption) => {
      $loading.close()
      const { data } = res
      if (!(data && data.length > 0)) {
        message.warning('暂无团队，请先创建或加入团队')
        return
      }

      NiceModal.show(ShareRobotModal, {
        record: {
          ...editObj,
          icon: fromIcon(editObj.iconUrl).icon,
          color: fromIcon(editObj.iconUrl).color,
        },
        marketList: data.map(item => ({
          ...item,
          marketName: `${item.marketName} ID:${item.marketId}`,
        })),
        onRefresh: () => refreshHomeTable(),
      })
    }).finally(() => {
      $loading.close()
    })
  }

  function openDetailModal(editObj: AnyObj) {
    NiceModal.show(DesignerRobotDetailModal, {
      source: homeTableRef.value?.localOption?.params?.dataSource,
      robotId: editObj.robotId,
    })
  }

  // 删除
  function handleDeleteProject(editObj: AnyObj) {
    const { robotId } = editObj
    isInTask({ robotId }).then((result: resOption) => {
      const { data } = result
      if (data) {
        let { situation, taskReferInfoList, robotId } = data

        // 过滤掉taskReferInfoList 中taskName 相同的项
        taskReferInfoList = taskReferInfoList?.filter((item, index, self) =>
          index === self.findIndex(t => t.taskName === item.taskName),
        )
        handleDeleteConfirm(getSituationContent('design', situation, taskReferInfoList), () => {
          delectProject({
            robotId,
            situation,
            taskIds: taskReferInfoList?.map(item => item.taskId).join(',') || '',
          }).then(() => {
            message.success(t('common.deleteSuccess'))
            refreshHomeTable()
          })
        })
      }
    })
  }

  return {
    currHoverId,
    createColumns,
    projectBaseOpts,
    projectMoreOpts,
    handleEdit,
    createCopy,
    handleRename,
    versionManage,
    publish,
    shareToMarket,
    handleDeleteProject,
  }
}
