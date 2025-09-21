import { createInjectionState } from '@vueuse/core'
import { onBeforeMount, ref, shallowRef } from 'vue'

import { getMarketRobotDetail, getMyRobotDetail } from '@/api/robot'
import { VIEW_OWN } from '@/constants/resource'

import type { Version } from '../components/VersionTable/index.vue'

interface BasicContentData {
  createTime: string // 创建时间
  creatorName: string // 创建者姓名
  introduction: string // 简介
  name: string // 机器人姓名
  version: number // 版本号
  filePath: string // 文件路径
  fileName: string // 文件名
  videoName?: string // 视频名称
  videoPath?: string // 视频路径
  useDescription: string // 使用说明
  sourceName?: string // 来源
  versionList?: Version[] // 版本列表
}

const [useProvideBasicStore, useBasicStore] = createInjectionState((robotId: string, source: string) => {
  const loading = ref(false)
  const data = shallowRef<BasicContentData>(null)

  onBeforeMount(async () => {
    loading.value = true
    const apiFn = source === VIEW_OWN ? getMyRobotDetail : getMarketRobotDetail
    data.value = await apiFn(robotId)
    loading.value = false
  })

  return { loading, data }
})

export { useBasicStore, useProvideBasicStore }
