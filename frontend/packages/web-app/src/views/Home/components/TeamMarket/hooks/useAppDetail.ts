import { ref } from 'vue'

import { getAllClassification, getAppDetails } from '@/api/market'
import { fromIcon } from '@/components/PublishComponents/utils'

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

  async function getAppDetailsInfo() {
    const categoryRes = await getAllClassification()
    const appDetailRes = await getAppDetails(params)
    const category = categoryRes.data.find(i => i.id === appDetailRes.data.category)?.name
    appDetail.value = {
      ...params,
      ...appDetail.value,
      ...appDetailRes.data,
      category,
      icon: fromIcon(appDetailRes.data.url || appDetailRes.data.iconUrl).icon,
      color: fromIcon(appDetailRes.data.url || appDetailRes.data.iconUrl).color,
    }
  }

  getAppDetailsInfo()

  return appDetail
}
