/** @format */

import { DownOutlined, UpOutlined } from '@ant-design/icons-vue'
import { Tooltip } from 'ant-design-vue'
import { reactive, ref } from 'vue'

import useRecordOperation from './useRecordOperation.tsx'
import useRecordTableColumns from './useRecordTableColumns.tsx'

export default function useRecordTableOption(props?: { robotId: string }) {
  const homeTableRef = ref(null)
  function refreshHomeTable() {
    if (homeTableRef.value) {
      homeTableRef.value?.fetchTableData()
    }
  }
  const { columns } = useRecordTableColumns(props, refreshHomeTable)
  const { rowSelection, getTableData, batchDelete } = useRecordOperation(refreshHomeTable)

  const tableOption = reactive({
    refresh: false, // 控制表格数据刷新
    formList: props.robotId
      ? []
      : [
          {
            componentType: 'input',
            bind: 'robotName',
            placeholder: '请输入机器人名称',
          },
          {
            componentType: 'datePicker',
            bind: 'timeRange',
          },
          {
            componentType: 'select',
            bind: 'result',
            placeholder: '请选择执行状态',
            options: [
              {
                label: '全部状态',
                value: '',
              },
              {
                label: '成功',
                value: 'robotSuccess',
              },
              {
                label: '失败',
                value: 'robotFail',
              },
              {
                label: '中止',
                value: 'robotCancel',
              },
              {
                label: '正在执行',
                value: 'robotExecute',
              },
            ],
            isTrim: true,
          },
        ],
    buttonList: [
      {
        label: '批量删除',
        action: '',
        clickFn: batchDelete,
        hidden: false,
      },
    ],
    getData: getTableData,
    tableProps: {
      // 表格配置，即antd中的Table组件的属性
      columns,
      rowKey: 'executeId',
      size: 'middle',
      rowSelection,
      expandIcon: ({ expanded, onExpand, record }) => {
        return record.children
          ? (
              <Tooltip title={expanded ? '收起' : '展开'}>
                <span
                  class="mr-2"
                  onClick={(e) => {
                    e.stopPropagation()
                    onExpand(record, e)
                  }}
                >
                  {expanded ? <UpOutlined /> : <DownOutlined />}
                </span>
              </Tooltip>
            )
          : (
              <span class="mr-2"></span>
            )
      },
    },
    params: {
      // 绑定的表单配置的数据
      robotName: '',
      robotId: props.robotId || '',
    },
  })
  return {
    homeTableRef,
    tableOption,
  }
}
