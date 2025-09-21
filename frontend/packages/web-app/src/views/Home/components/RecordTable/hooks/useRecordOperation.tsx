/** @format */

import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import { computed, ref } from 'vue'

import { delExecute, getExecuteLst } from '@/api/record'
import { checkVideoPaths } from '@/api/setting'

import type { resOption } from '../../../types'

export default function useRecordOperation(refreshHomeTable?: () => void) {
  const selectedRowKeys = ref<string[]>([])
  const rowSelection = computed(() => {
    return {
      onChange: (keys: string[], _selectedRows: any[]) => {
        selectedRowKeys.value = keys
      },
      selectedRowKeys: selectedRowKeys.value,
    }
  })
  function getTableData(params) {
    return new Promise((resolve) => {
      const paramsObj = {
        ...params,
        startTime: params.timeRange ? `${dayjs(params.timeRange[0]).format('YYYY-MM-DD')} 00:00:00` : '',
        endTime: params.timeRange ? `${dayjs(params.timeRange[1]).format('YYYY-MM-DD')} 23:59:59` : '',
      }
      delete paramsObj.timeRange
      getExecuteLst(paramsObj).then((res: resOption) => {
        const { data } = res
        if (data) {
          const { total, records } = data
          /**
           * 检查视频是否本地存在
           */
          const videoPaths = records.filter(item => item.videoLocalPath).map(item => item.videoLocalPath)
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
                const newRecords = records.map((item) => {
                  item.videoExist = exist.includes(item.videoLocalPath) ? '0' : '1' // 0存在 1不存在
                  return item
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

  function batchDelete(selected: string[]) {
    const selectedKeys = Array.isArray(selected) ? selected : selectedRowKeys.value
    if (selectedKeys.length === 0) {
      message.warning('请至少选择一条记录')
    }
    delExecute({ recordIds: selectedKeys }).then((res) => {
      message.success(res.data || '删除成功')
      selectedRowKeys.value = []
      refreshHomeTable()
    })
  }
  return {
    getTableData,
    batchDelete,
    rowSelection,
  }
}
