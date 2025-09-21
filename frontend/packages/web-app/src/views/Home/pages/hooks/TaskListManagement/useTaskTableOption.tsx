/** @format */

import { ClockCircleOutlined, SearchOutlined } from '@ant-design/icons-vue'
import { Icon } from '@rpa/components'
import { Button, Switch, Tooltip } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { reactive } from 'vue'

import type { TaskTrigger } from '@/types/schedule'

import { TASK_TYPE, TASK_TYPE_OPTION, WEEK_MAP_EN } from '../../../config/task'

import { useTaskOperation } from './useTaskOperation'

export function useTaskTableOption() {
  const { t } = useTranslation()

  const { getTableData, viewQueue, handleNewTask, handleEditTask, openSheculedTaskList, handleDeleteTask, handleEnableTask, handleRunTask, taskListTableRef, hideQueue, showQueue } = useTaskOperation()

  const weekRender = (value: any[]) => {
    const sortWeek = value.sort()
    const weeks = sortWeek.map(item => t(`weekOptions.${WEEK_MAP_EN[item]}`)).join('、')
    return weeks
  }

  const conditionInfoRender = (record) => {
    try {
      const taskJson = JSON.parse(record.taskJson) as TaskTrigger
      switch (record.taskType) {
        case TASK_TYPE.TASK_TIME:
          if (taskJson.frequency_flag === 'advance') {
            return t('taskCondition.advance', { cron_expression: taskJson.cron_expression })
          }
          if (taskJson.frequency_flag === 'regular') {
            return t('taskCondition.regular', { time_expression: taskJson.time_expression })
          }
          if (taskJson.frequency_flag === 'minutes') {
            return t('taskCondition.minutes', { minutes: taskJson.minutes })
          }
          if (taskJson.frequency_flag === 'hours') {
            return t('taskCondition.hours', { hours: taskJson.hours, minutes: taskJson.minutes })
          }
          if (taskJson.frequency_flag === 'days') {
            return t('taskCondition.days', { hours: taskJson.hours, minutes: taskJson.minutes })
          }
          if (taskJson.frequency_flag === 'weeks') {
            return t('taskCondition.weeks', { weeks: weekRender(taskJson.weeks), hours: taskJson.hours, minutes: taskJson.minutes })
          }
          if (taskJson.frequency_flag === 'months') {
            return t('taskCondition.months', { months: taskJson.months, weeks: weekRender(taskJson.weeks), hours: taskJson.hours, minutes: taskJson.minutes })
          }
          break
        case TASK_TYPE.TASK_MANUAL:
          return t('taskCondition.manual')
        case TASK_TYPE.TASK_FILE:
          return t('taskCondition.file', { directory: taskJson.directory })
        case TASK_TYPE.TASK_HOTKEY:
          return t('taskCondition.hotKey', { shortcuts: taskJson.shortcuts.join(' + ') })
        case TASK_TYPE.TASK_MAIL:
          return t('taskCondition.mail', { interval_time: taskJson.interval_time })
        default:
          return t('taskCondition.unknown')
      }
    }
    catch (error) {
      console.error(`conditionInfoRender: ${error}`)
    }
  }
  const excuteConditionRender = ({ record }) => {
    const taskType = t(`taskTypeOption.${record.taskType}`)
    const taskInfo = conditionInfoRender(record)
    return (
      <div>
        <div class="flex items-center h-6 text-sm">
          <span class="font">{ taskType }</span>
          {
            record.taskType === TASK_TYPE.TASK_TIME
              ? <Button class="p-0 ml-2 flex items-center" type="link" icon={<ClockCircleOutlined />} disabled={!record.enable} onClick={() => openSheculedTaskList(record)}></Button>
              : null
          }
        </div>
        <Tooltip title={taskInfo}>
          <div class="text-xs text-text-secondary truncate max-w-[200px]">{ taskInfo }</div>
        </Tooltip>
      </div>
    )
  }
  const taskOperationRender = ({ record }) => {
    record.enable = !!record.enable // 后端传不了布尔值，只能传整数，所以这里转换一下
    return (
      <div class="operation flex items-center gap-5 text-base">
        {record.taskType === 'manual'
          ? (
              <Tooltip title={t('run')}>
                <Button
                  size="small"
                  class="!p-0 flex items-center justify-center border-none bg-transparent"
                  onClick={() => { handleRunTask(record) }}
                >
                  <Icon name="play-circle-stroke" size="16px" class="min-w-[28px] inline outline-none" />
                </Button>
              </Tooltip>
            )
          : (
              <Tooltip title={t('enableOrDisable')}>
                <Switch
                  v-model:checked={record.enable}
                  size="small"
                  loading={record.enableLoading}
                  onChange={() => {
                    handleEnableTask(record)
                  }}
                />
              </Tooltip>
            )}
        <Tooltip title={t('edit')}>
          <Button
            size="small"
            class="!p-0 flex items-center justify-center border-none bg-transparent"
            onClick={() => { handleEditTask(record) }}
          >
            <Icon name="projedit" size="16px" class="inline outline-none" />
          </Button>
        </Tooltip>
        <Tooltip title={t('delete')}>
          <Button
            size="small"
            class="!p-0 flex items-center justify-center border-none bg-transparent"
            onClick={() => { handleDeleteTask(record) }}
          >
            <Icon name="market-del" size="16px" class="inline outline-none" />
          </Button>
        </Tooltip>
      </div>
    )
  }
  const tableOption = reactive({
    tableCellHeight: 62, // 单元格高度
    refresh: false, // 控制表格数据刷新
    getData: getTableData,
    formList: [
      {
        componentType: 'input',
        bind: 'name',
        placeholder: t('taskNamePlaceholder'),
        prefix: <SearchOutlined />,
      },
      {
        componentType: 'select',
        bind: 'taskType',
        span: 24,
        placeholder: t('taskTypePlaceholder'),
        options: [
          {
            label: t('all'),
            value: '',
          },
          ...TASK_TYPE_OPTION.map((i) => {
            return {
              label: t(`taskTypeOption.${i.value}`),
              value: i.value,
            }
          }),
        ],
        // hidden: true,
      },
    ],
    buttonList: [
      // 表格上方的按钮配置
      {
        label: t('checkQueue'),
        action: 'execute_cloud_schedule_queue',
        clickFn: viewQueue,
        type: 'default',
        hidden: false,
      },
      {
        label: t('addTask'),
        action: 'execute_cloud_schedule_create',
        clickFn: handleNewTask,
        type: 'primary',
        hidden: false,
      },

    ],
    tableProps: {
      // 表格配置，即antd中的Table组件的属性
      columns: [
        {
          title: t('taskName'),
          dataIndex: 'name',
          key: 'name',
          ellipsis: true,
        },
        {
          title: t('robot'),
          dataIndex: 'robotNames',
          key: 'robotNames',
          ellipsis: true,
          customRender: ({ record }) => {
            return <Tooltip title={record.robotNames}>{ record.robotNames }</Tooltip>
          },
          width: 240,
        },
        {
          title: t('created'),
          dataIndex: 'createTime',
          key: 'createTime',
          ellipsis: true,
          // sorter: (a, b) => a - b,
        },
        {
          title: t('excuteCondition'),
          dataIndex: 'taskType',
          key: 'taskType',
          ellipsis: true,
          width: 240,
          customRender: ({ record }) => {
            return excuteConditionRender({ record })
          },
        },
        {
          title: t('operate'),
          dataIndex: 'oper',
          key: 'oper',
          width: 140,
          customRender: ({ record }) => {
            return taskOperationRender({ record })
          },
        },
      ],
      rowKey: 'taskId',
      size: 'middle',
      customRow: (record) => {
        return {
          onDblclick: () => { // 双击行
            handleEditTask(record)
          },
        }
      },
    },
    params: {
      // 绑定的表单配置的数据
      // taskSelect: 'all',
      name: '',
    },
  })
  return { tableOption, taskListTableRef, hideQueue, showQueue }
}
