import { message } from 'ant-design-vue'
import { debounce } from 'lodash-es'
import { ref, watch } from 'vue'

import { utilsManager } from '@/platform'
import useUserSettingStore, { DEFAULT_FORM } from '@/stores/useUserSetting'

export function useVideoConfig() {
  const isEnable = ref(false)
  const videoRef = ref(null)
  const videoForm = ref<RPA.VideoFormMap | null>(null)

  const handleOpenFile = async () => {
    const result = await utilsManager.showDialog({ file_type: 'folder' })
    if (result[0]) {
      videoForm.value.filePath = result[0]
    }
  }

  const handleSwitchChange = () => {
    videoForm.value.enable = isEnable.value
  }

  const saveVideoGet = async () => {
    const userPath = await utilsManager.getUserPath()
    videoForm.value = useUserSettingStore().userSetting.videoForm || DEFAULT_FORM
    isEnable.value = videoForm.value?.enable || false
    if (!videoForm.value?.filePath) {
      const result = await utilsManager.pathJoin([userPath, 'logs', 'recording'])
      videoForm.value.filePath = result
    }
  }
  saveVideoGet()

  const saveVideoSet = debounce(() => {
    if (!videoForm.value.fileClearTime) {
      message.warning('视频清理时间不能为空')
      videoForm.value.fileClearTime = 7
      return
    }
    videoForm.value.enable = isEnable.value
    const newSetting = { videoForm: videoForm.value }
    useUserSettingStore().saveUserSetting(newSetting)
  }, 500)

  watch(
    videoForm,
    (_, oldVal) => oldVal && saveVideoSet(),
    { deep: true },
  )

  return {
    isEnable,
    videoRef,
    videoForm,
    handleOpenFile,
    handleSwitchChange,
  }
}
