import type { Ref } from 'vue'
import { onBeforeUnmount, onMounted, ref } from 'vue'

import { getAppUpdateStatus } from '@/api/market'
import { getRobotUpdateStatus } from '@/api/robot'
import { useMarketStore } from '@/stores/useMarketStore'
import type { resOption } from '@/views/Home/types'

export function useRobotUpdate(type: string, tableRef: Ref) {
  const appIds = ref([])
  const robotIds = ref([])
  function getInitUpdateIds(records) {
    appIds.value.length = 0
    robotIds.value.length = 0
    appIds.value = records.filter(item => item.appId).map(robot => robot.appId)
    robotIds.value = records.filter(item => item.appId).map(robot => robot.robotId)
  }
  function handlePollingStatus() {
    if (appIds.value?.length > 0) {
      const FN = type === 'app' ? getAppUpdateStatus : getRobotUpdateStatus
      const params = {
        marketId: useMarketStore().activeMarket?.marketId,
        appIdListStr: appIds.value.join(','),
        robotIdListStr: type === 'robot' ? robotIds.value.join(',') : undefined,
      }
      FN(params).then((res: resOption) => {
        const { data } = res
        if (data) {
          data.forEach((item) => {
            const { appId: aId, robotId: rId, updateStatus: newStatus } = item
            tableRef.value?.value?.tableData.forEach((robot) => {
              const { updateStatus } = robot
              if (type === 'app') { // 处理市场下更新状态查询
                if (aId === robot.appId && updateStatus !== newStatus) {
                  robot.updateStatus = data
                }
              }
              if (type === 'robot') { // 处理执行器下更新状态查询
                if (rId === robot.robotId && aId === robot.appId && updateStatus !== newStatus) {
                  robot.updateStatus = data
                }
              }
            })
          })
        }
      })
    }
  }
  let timer = null
  onMounted(() => {
    timer = setInterval(() => {
      handlePollingStatus()
    }, 10000)
  })
  onBeforeUnmount(() => {
    clearInterval(timer)
  })
  return {
    getInitUpdateIds,
  }
}
