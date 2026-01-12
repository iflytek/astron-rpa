import { spawn } from 'node:child_process'
import fs from 'node:fs/promises'

import logger from './log'
import { d7zrPath } from './path'

export function extract7z(archivePath: string, outputDir: string) {
  logger.info(`Using 7zr at: ${d7zrPath}`)
  if (process.platform !== 'win32') {
    archivePath = archivePath.replace(/\\/g, '/')
    outputDir = outputDir.replace(/\\/g, '/')
  }
  return new Promise<void>((resolve, reject) => {
    const process = spawn(d7zrPath, ['x', archivePath, `-o${outputDir}`, '-y'])

    process.stderr.on('data', (data) => {
      const error = data.toString()
      logger.error(`解压错误: ${error}`)
    })

    process.on('close', (code) => {
      if (code === 0) {
        logger.info(`${archivePath} 解压完成`)
        resolve()
      }
      else {
        logger.error(`解压失败，退出码: ${code}`)
        reject(new Error(`解压失败，退出码: ${code}`))
      }
    })
  })
}

export async function rename(oldPath: string, newPath: string) {
  await fs.rename(oldPath, newPath)
  return newPath
}
