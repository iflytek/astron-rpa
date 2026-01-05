import fs from 'node:fs'
import stream from 'node:stream'
import { promisify } from 'node:util'

import axios from 'axios'

import { toUnicode } from '../common'
/** @format */
import type { AxiosResponse } from '../types'

import { mainToRender } from './event'

const pipeline = promisify(stream.pipeline)
// let allDownloadCount = 0
// const downloadMap = {
//   '': 0
// }

export async function downloadWithAxiosProgress(url, outputPath) {
  // allDownloadCount++
  // downloadMap[url] = 0
  const writer = fs.createWriteStream(outputPath)
  // const startTime = Date.now()

  // let receivedBytes = 0
  // let totalBytes = 0
  // let lastProgress = 0

  const response: unknown = await axios({
    method: 'get',
    url,
    responseType: 'stream',
    onDownloadProgress: () => {
      const msg = `{"type":"sync","msg":{"msg":"${toUnicode('下载中')}","step": 50}}`
      mainToRender('scheduler-event', msg, undefined, true)
      // receivedBytes = progressEvent.loaded
      // totalBytes = progressEvent.total || totalBytes
      // showProgress(receivedBytes, totalBytes)
    },
  }).catch(() => {
    const msg = `{"type":"sync","msg":{"msg":"${toUnicode('下载失败')}","step":""}}`
    mainToRender('scheduler-event', msg, undefined, true)
  })

  const pipdata = (response as AxiosResponse).data
  await pipeline(pipdata, writer)

  // function showProgress(received, total) {
  //   const now = Date.now()
  //   if (now - lastProgress < 1000 && received < total) return
  //   lastProgress = now

  //   const percentage = total > 0 ? Math.floor((received / total) * 100) : '--'
  //   const speed = calculateSpeed(received)
  //   downloadMap[url] = percentage
  //   // 计算 downloadMap 中 每一项加权最终得出的 百分比 每一项占 1/allDownloadCount 的比例
  //   const weightedPercent = Object.values(downloadMap)
  //     .reduce((acc, curr) => acc + curr / allDownloadCount, 0)
  //     .toFixed(2)
  //   const msg = `{"type":"sync","msg":{"msg":"${toUnicode('下载中')}","step": ${weightedPercent}, "speed":"${speed}"}}`
  //   mainToRender('scheduler-event', msg, undefined, true)
  // }

  // function calculateSpeed(received) {
  //   const elapsed = (Date.now() - startTime) / 1000
  //   return `${formatBytes(received / elapsed)}/s`
  // }

  // function formatBytes(bytes) {
  //   if (bytes === 0) return '0 Bytes'
  //   const k = 1024
  //   const sizes = ['Bytes', 'KB', 'MB', 'GB']
  //   const i = Math.floor(Math.log(bytes) / Math.log(k))
  //   return `${Number.parseFloat((bytes / k ** i).toFixed(2))} ${sizes[i]}`
  // }
}

// axios 基础接口调用
export async function axiosRequest(url, method, data, headers) {
  const response = await axios({
    method,
    url,
    data,
    headers,
  })
  return response.data as AxiosResponse
}
