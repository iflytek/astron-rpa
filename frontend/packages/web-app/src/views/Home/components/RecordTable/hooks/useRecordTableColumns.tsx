import { Icon } from '@rpa/components'
import { Button, Tooltip } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'

import { getDurationText } from '@/utils/dayjsUtils'

import { utilsManager } from '@/platform'
import StatusCircle from '@/views/Home/components/StatusCircle.vue'
import { useCommonOperate } from '@/views/Home/pages/hooks/useCommonOperate.tsx'

import useRecordOperation from './useRecordOperation.tsx'

export default function useRecordTableColumns(props?: { robotId?: string, taskId?: string }, refreshHomeTable?: () => void) {
  const translate = useTranslation()
  const { batchDelete } = useRecordOperation(refreshHomeTable)
  const { handleCheck } = useCommonOperate()
  const columns = [
    props.robotId
      ? null
      : {
          title: translate.t('robotName'),
          dataIndex: 'robotName',
          key: 'robotName',
          ellipsis: true,
        },
    props.robotId
      ? null
      : {
          title: '版本',
          dataIndex: 'robotVersion',
          key: 'robotVersion',
          width: 60,
          ellipsis: true,
        },
    (props.robotId || props.taskId)
      ? null
      : {
          title: '任务名称',
          dataIndex: 'taskName',
          key: 'taskName',
          ellipsis: true,
          customRender: ({ record }) => {
            return record.taskName || '--'
          },
        },
    {
      title: translate.t('startTime'),
      dataIndex: 'startTime',
      key: 'startTime',
      ellipsis: true,
      sorter: true,
    },
    {
      title: translate.t('endTime'),
      dataIndex: 'endTime',
      key: 'endTime',
      ellipsis: true,
      sorter: true,
    },
    {
      title: '执行时长',
      key: 'executeTime',
      dataIndex: 'executeTime',
      customRender: ({ record }) => getDurationText(record.executeTime),
    },
    {
      title: translate.t('result'),
      dataIndex: 'result',
      key: 'result',
      ellipsis: true,
      width: 100,
      customRender: ({ record }) => {
        return <StatusCircle type={String(record.result)} />
      },
    },
    {
      title: translate.t('operate'),
      dataIndex: 'oper',
      key: 'oper',
      width: 120,
      customRender: ({ record }) => {
        return (
          <div class="operation">
            <Tooltip title="日志详情" placement="bottom">
              <Button
                type="link"
                size="small"
                class="cursor-pointer outline-none p-[5px] text-[initial] hover:!text-primary"
                onClick={() => handleCheck({ type: !props.robotId ? 'drawer' : 'modal', record })}
              >
                <Icon name="log" size="16px" />
              </Button>
            </Tooltip>
            <Tooltip title="视频播放" placement="bottom">
              <Button
                type="link"
                size="small"
                class="cursor-pointer outline-none p-[5px] text-[initial] hover:!text-primary"
                disabled={!(record?.videoExist === '0')} // '0': 本地存在 '1': 本地不存在
                onClick={() => utilsManager.playVideo(record.videoLocalPath)}
              >
                <Icon name="video-play" size="16px" />
              </Button>
            </Tooltip>
            <Tooltip title="删除">
              <Button
                type="link"
                size="small"
                class="cursor-pointer outline-none p-[5px] text-[initial] hover:!text-primary"
                onClick={() => batchDelete([record.executeId])}
              >
                <Icon name="market-del" size="16px" />
              </Button>
            </Tooltip>
          </div>
        )
      },
    },
  ]

  return { columns: columns.filter(i => i) }
}
