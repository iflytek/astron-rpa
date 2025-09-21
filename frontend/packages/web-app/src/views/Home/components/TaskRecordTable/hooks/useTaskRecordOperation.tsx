/** @format */

import { message, Table } from 'ant-design-vue'
import dayjs from 'dayjs'
import { computed, ref } from 'vue'

import { delTaskExecute, getTaskExecuteLst } from '@/api/record'
import { checkVideoPaths } from '@/api/setting'
import useRecordTableColumns from '@/views/Home/components/RecordTable/hooks/useRecordTableColumns.tsx'

import type { resOption } from '../../../types'

export default function useTastRecordOperation(refreshHomeTable?: () => void) {
  const selectedRowKeys = ref<string[]>([])
  const rowSelection = computed(() => {
    return {
      onChange: (keys: string[], _selectedRows: any[]) => {
        console.log('选中的行', keys)
        selectedRowKeys.value = keys
      },
      selectedRowKeys: selectedRowKeys.value,
    }
  })

  function batchDelete(selected: string[]) {
    const selectedKeys = Array.isArray(selected) ? selected : selectedRowKeys.value
    if (selectedKeys.length === 0) {
      message.warning('请至少选择一条记录')
    }
    delTaskExecute({ taskExecuteIdList: selectedKeys }).then((res) => {
      message.success(res.data || '删除成功')
      selectedRowKeys.value = []
      refreshHomeTable()
    })
  }

  function getTableData(params) {
    return new Promise((resolve) => {
      const paramsObj = {
        ...params,
        startDate: params.timeRange ? `${dayjs(params.timeRange[0]).format('YYYY-MM-DD')} 00:00:00` : '',
        endDate: params.timeRange ? `${dayjs(params.timeRange[1]).format('YYYY-MM-DD')} 23:59:59` : '',
      }
      delete paramsObj.timeRange
      getTaskExecuteLst(paramsObj).then((res: resOption) => {
        const { data } = res
        if (data) {
          const { total, records } = data
          /**
           * 检查视频是否本地存在
           */
          const videoPaths = Array.from(new Set(records.flatMap(i => (i.robotExecuteRecordList || []).filter(item => item.videoLocalPath).map(item => item.videoLocalPath))))
          if (videoPaths.length <= 0) {
            resolve({
              records,
              total,
            })
          }
          checkVideoPaths({ videoPaths })
            .then((result) => {
              const exist = result?.data?.exist
              if (exist && exist?.length > 0) {
                const newRecords = records.map((record) => {
                  record.robotExecuteRecordList = record.robotExecuteRecordList.map((item) => {
                    item.videoExist = exist.includes(item.videoLocalPath) ? '0' : '1' // 0存在 1不存在
                    return item
                  })
                  return record
                })
                resolve({
                  records: newRecords,
                  total,
                })
              }
              else {
                resolve({
                  records,
                  total,
                })
              }
            })
            .catch(() => {
              resolve({
                records,
                total,
              })
            })
        }
      })
    })
  }

  function handleExpandedRowRender({ record }) {
    const { columns } = useRecordTableColumns({ taskId: record.taskId })

    const innerColumns = [
      { width: '32px' }, // 用于占位上层复选框位置，保持父表格和子表格列对齐
      { width: '50px', title: '', key: 'expand', dataIndex: 'expand' }, // 用于占位上层展开按钮位置,保持父表格和子表格列对齐
      ...columns,
    ]
    return (
      <Table
        size="small"
        rowKey="recordId"
        columns={innerColumns}
        dataSource={record.robotExecuteRecordList}
        pagination={false}
      />
    )
  }

  return {
    getTableData,
    rowSelection,
    batchDelete,
    handleExpandedRowRender,
  }
}
