import { ref } from 'vue'

import { appendixDownload, cancelAppendixDownload } from '@/api/market'
import { utilsManager } from '@/platform'
import type { AppFileItem } from '@/views/Home/types/market'
import { AppFileStatus } from '@/views/Home/types/market'

const PROGRESS_SPEED = 10
export function useAppFileDownload() {
  const files = ref<Array<AppFileItem>>([])
  const setFiles = (fileList) => {
    files.value = fileList.map((item: any) => {
      const { appendixId, link } = item
      const tmpArr = link.split('/')
      const filename = tmpArr[tmpArr.length - 1]
      return {
        link,
        appendixId,
        filename,
        status: AppFileStatus.normal,
      }
    })
  }

  const progressTimers = {}
  const startProgress = (item) => {
    const { appendixId } = item
    item.status = AppFileStatus.downloading
    progressTimers[appendixId] && clearInterval(progressTimers[appendixId])
    progressTimers[appendixId] = setInterval(() => {
      if (item.percent >= 95) {
        item.percent = 95
      }
      else {
        item.percent += PROGRESS_SPEED
      }
    }, 1000)
  }

  const finishDownload = (item, status) => {
    clearInterval(progressTimers[item.appendixId])
    item.status = status
    if (status === AppFileStatus.success) {
      item.percent = 100
    }
  }

  const download = (item) => {
    item.percent = 0
    item.status = AppFileStatus.normal
    utilsManager.showDialog({
      title: '选择保存文件目录',
      properties: ['openDirectory'],
    }).then((res: any) => {
      startProgress(item)
      appendixDownload({
        appendixLink: item.link,
        savePath: res,
        resourceType: 'project',
      }).then(() => {
        finishDownload(item, AppFileStatus.success)
      }).catch(() => {
        finishDownload(item, AppFileStatus.exception)
      })
    })
  }

  const cancelDownload = (item) => {
    const { appendixId } = item
    if (item.status === AppFileStatus.downloading) {
      cancelAppendixDownload({}).then(() => {
        progressTimers[appendixId] && clearInterval(progressTimers[appendixId])
        item.status = AppFileStatus.cancled
      })
    }
  }

  return {
    files,
    setFiles,
    download,
    cancelDownload,
  }
}
