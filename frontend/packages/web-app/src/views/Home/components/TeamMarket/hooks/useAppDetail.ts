import { ref } from 'vue'

import { getAppDetails } from '@/api/market'
import { fromIcon } from '@/components/PublishComponents/utils'
import { ROBOT_TYPE_OPTIONS } from '@/views/Home/config'

export function useAppDetail(params: { marketId: string, appId: string }) {
  const appDetail = ref({
    appName: '',
    category: '',
    downloadNum: 0,
    checkNum: 0,
    creatorName: '',
    icon: '',
    color: '',
    introduction: '',
    videoPath: '',
    useDescription: '',
    // appendixShowList: [],
    fileName: '',
    filePath: '',
    versionInfoList: [],
  })
  getAppDetails(params).then((res) => {
    const category = ROBOT_TYPE_OPTIONS.find(i => i.value === res.data.category)?.label
    appDetail.value = {
      ...params,
      ...appDetail.value,
      ...res.data,
      category,
      icon: fromIcon(res.data.url || res.data.iconUrl).icon,
      color: fromIcon(res.data.url || res.data.iconUrl).color,
    }
  })
  return appDetail
}
