import { reactive } from 'vue'

import StatusCircle from '@/views/Home/components/StatusCircle.vue'

import useTaskRecordOperation from './useTaskRecordOperation'

export default function useTaskRecordOption(taskId) {
  const { getTableData, handleExpandedRowRender } = useTaskRecordOperation()

  const tableOption = reactive({
    refresh: false, // 控制表格数据刷新
    getData: getTableData,
    tableProps: { // 表格配置，即antd中的Table组件的属性
      columns: [
        {
          title: '序号',
          dataIndex: 'id',
          key: 'id',
          align: 'center',
        },
        {
          title: '执行次数',
          key: 'count',
          dataIndex: 'count',
          ellipsis: true,
          customRender: ({ record }) => `第${record.count}次`,
        },
        {
          title: '开始时间',
          key: 'startTime',
          dataIndex: 'startTime',
        },
        {
          title: '结束时间',
          key: 'endTime',
          dataIndex: 'endTime',
        },
        {
          title: '执行结果',
          key: 'result',
          dataIndex: 'result',
          customRender: ({ record }) => {
            return <StatusCircle type={`${record.result}`} />
          },
        },
      ],
      rowKey: 'id',
      expandedRowRender: handleExpandedRowRender,
    },
    params: { // 绑定的表单配置的数据
      taskId,
    },
  })
  return tableOption
}
