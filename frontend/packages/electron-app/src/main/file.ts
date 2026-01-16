import Seven from 'node-7z'

import { d7zrPath } from './path'
import logger from './log'

export function extract7z(archivePath: string, outputDir: string, callback?: (percent: number) => void) {
  let prePercent: number = 0;

  return new Promise<void>((resolve, reject) => {
    const myStream = Seven.extractFull(archivePath, outputDir, {
      $progress: true,
      $bin: d7zrPath
    })

    myStream.on('progress', function (progress) {
      if (progress.percent === prePercent) return;

      prePercent = progress.percent;
      callback?.(prePercent)
    })

    myStream.on('end', function () {
      logger.info(`${archivePath} 解压完成`)
      resolve()
    })

    myStream.on('error', (error) => {
      logger.error(`解压错误: ${error}`)
      reject(error)
    })
  })
}
