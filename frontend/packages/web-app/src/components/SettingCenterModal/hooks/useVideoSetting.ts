import { message } from 'ant-design-vue'
import { debounce } from 'lodash-es'
import { ref, watch } from 'vue'

import { utilsManager } from '@/platform'
import useUserSettingStore, { DEFAULT_FORM } from '@/stores/useUserSetting'

export function useVideoConfig() {
  const isEnable = ref(false)
  const videoRef = ref(null)
  const videoForm = ref<RPA.VideoFormMap | null>(null)

  const handleOpenFile = () => {
    utilsManager.showDialog({ file_type: 'folder' }).then((res) => {
      if (res) {
        videoForm.value.filePath = res as string
      }
    })
  }
  const handleSwitchChange = () => {
    videoForm.value.enable = isEnable.value
  }
  const saveVideoGet = () => {
    utilsManager.getUserPath().then((userPath) => {
      videoForm.value = useUserSettingStore().userSetting.videoForm || DEFAULT_FORM
      isEnable.value = videoForm.value?.enable || false
      if (!videoForm.value?.filePath) {
        videoForm.value.filePath = `${userPath}logs\\recording`
        utilsManager.pathJoin([userPath, 'logs', 'recording']).then((result) => {
          videoForm.value.filePath = result as string
        })
      }
    })
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
