import { exec, spawn } from 'node:child_process'
import fs from 'node:fs/promises'
import { join } from 'node:path'

import { toUnicode } from '../common'

import { mainToRender } from './event'
import { extract7z } from './file'
import logger from './log'
import { appWorkPath, confPath, pythonExe, resourcePath } from './path'
import { getMainWindow } from './window'
import { envJson } from './env'

process.on('uncaughtException', (err) => {
  logger.error(`uncaughtException: ${err.message}`)
})

/**
 * 检查 python envJson.SCHEDULER_NAME 是否正在运行
 */
export function checkPythonRpaProcess() {
  return new Promise((resolve, reject) => {
    // linux 上检测 python 进程中 命令行中包含 envJson.SCHEDULER_NAME 的进程
    if (process.platform !== 'win32') {
      exec(`ps aux | grep "${envJson.SCHEDULER_NAME}"`, (error, stdout) => {
        if (error) {
          return resolve(false)
        }
        const isRunning = stdout.trim() !== ''
        resolve(isRunning)
      })
    }
    else {
      exec('tasklist /v /fi "imagename eq python.exe"', (error, stdout) => {
        if (error) {
          return reject(error)
        }
        const isRunning = stdout.includes(envJson.SCHEDULER_NAME)
        resolve(isRunning)
      })
    }
  })
}

/**
 * 启动服务
 */
export async function startServer() {
  // 查看是否已经启动 envJson.SCHEDULER_NAME
  const isRunning = await checkPythonRpaProcess()
  if (isRunning) {
    logger.info(`${envJson.SCHEDULER_NAME} is running`)
    return
  }
  mainToRender('scheduler-event', `{"type":"sync","msg":{"msg":"${toUnicode('正在启动服务')}","step":51 }}`, undefined, true)

  const rpaSetup = spawn(pythonExe, ['-m', envJson.SCHEDULER_NAME, '--conf', confPath], { cwd: appWorkPath })
 
  rpaSetup.stdout?.on('data', (data) => {
    msgFilter(data.toString())
  })

  rpaSetup.stderr?.on('data', (data) => {
    logger.info(`${envJson.SCHEDULER_NAME} stderr: ${data.toString()}`)
  })

  rpaSetup.on('close', (code) => {
    if (code === 0) {
      logger.info(`${envJson.SCHEDULER_NAME} exited successfully.`)
    }
    else {
      logger.error(`${envJson.SCHEDULER_NAME} exited with error code: ${code}`)
    }
  })

  rpaSetup.on('error', (error) => {
    logger.error(`Failed to start ${envJson.SCHEDULER_NAME}: ${error.message}`)
  })
}

/**
 * 消息过滤器，处理从Python进程接收到的消息
 * @param msg - 从Python进程输出的原始消息字符串
 */
function msgFilter(msg: string) {
  // 匹配以 ||emit|| 开头的字符串
  const reg = /\|\|emit\|\|(.*)/
  const match = msg.match(reg)
  if (match) {
    // 发送到渲染进程
    const matchMsg = match[1].trim().replaceAll('"', '')
    const win = getMainWindow()
    win?.webContents.send('scheduler-event', matchMsg)
  }
}

/**
 * 检查资源目录中需要解压的Python包
 * @returns 需要解压的压缩包文件名数组
 */
async function checkNeedExtractPythonPackage() {
  if (process.platform === 'win32') {
    const fileNames = await fs.readdir(resourcePath)
    return fileNames.filter(fileName => fileName.endsWith('.7z'))
  }
  logger.info('No python package in resources for non-windows platform')
  return []
}

/**
 * 读取哈希文件内容
 * @param hashFilePath - 哈希文件路径（通常以.sha256.txt结尾）
 * @returns 哈希文件中的哈希值字符串
 */
async function readHashFile(hashFilePath: string): Promise<string> {
  try {
    const hashContent = await fs.readFile(hashFilePath, 'utf-8')
    return hashContent.trim()
  } catch (error) {
    logger.error(`读取hash文件失败: ${hashFilePath}`, error)
    throw error
  }
}

/**
 * 删除解压文件并记录日志
 * @param archivePath - 要删除的解压文件路径
 * @param reason - 删除原因（用于日志记录）
 */
async function deleteExtractedArchive(archivePath: string, reason: string): Promise<void> {
  try {
    await fs.rm(archivePath, { recursive: true, force: true })
    logger.info(`已删除解压文件: ${archivePath}，原因: ${reason}`)
  } catch (deleteError) {
    logger.error(`删除解压文件失败: ${archivePath}`, deleteError)
    throw deleteError
  }
}

/**
 * 处理需要重新解压的情况
 * @param packageFile - 包文件名
 * @param archivePath - 解压文件路径
 * @param reason - 重新解压的原因
 * @param deleteArchive - 是否需要删除现有文件
 * @param needExtractFiles - 需要重新解压的文件列表
 */
async function handleNeedExtract(
  packageFile: string,
  archivePath: string,
  reason: string,
  deleteArchive: boolean,
  needExtractFiles: string[]
): Promise<void> {
  if (deleteArchive) {
    try {
      await deleteExtractedArchive(archivePath, reason)
    } catch {
      // 错误已在deleteExtractedArchive中记录，继续执行
    }
  }
  needExtractFiles.push(packageFile)
}

/**
 * 检查单个文件是否需要重新解压
 * @param packageFile - 压缩包文件名
 * @param needExtractFiles - 需要解重新压的文件列表
 */
async function checkSingleFile(packageFile: string, needExtractFiles: string[]): Promise<void> {
  const archiveName = packageFile.replace('.7z', '')
  const archivePath = join(appWorkPath, archiveName)
  const hashFileName = `${packageFile}.sha256.txt`
  const resourceHashPath = join(resourcePath, hashFileName)
  const appWorkHashPath = join(appWorkPath, hashFileName)

  try {
    logger.info(`检查文件: ${packageFile}`)

    // 检查资源目录中的hash文件是否存在
    try {
      await fs.access(resourceHashPath)
    } catch {
      logger.warn(`资源目录hash文件不存在: ${hashFileName}`)
      await handleNeedExtract(packageFile, archivePath, '资源目录hash文件不存在', false, needExtractFiles)
      return
    }

    const [archiveExists, hashFileExists] = await Promise.all([
      fs.access(archivePath).then(() => true).catch(() => false),
      fs.access(appWorkHashPath).then(() => true).catch(() => false)
    ])

    if (!archiveExists) {
      await handleNeedExtract(packageFile, archivePath, '解压文件不存在', false, needExtractFiles)
      return
    }

    if (!hashFileExists) {
      logger.warn(`用户数据目录hash文件不存在: ${hashFileName}`)
      await handleNeedExtract(packageFile, archivePath, '用户数据目录hash文件不存在', true, needExtractFiles)
      return
    }

    const [resourceHash, appWorkHash] = await Promise.all([
      readHashFile(resourceHashPath),
      readHashFile(appWorkHashPath)
    ])

    if (!resourceHash || !appWorkHash) {
      logger.warn(`hash文件内容为空: ${packageFile}`)
      await handleNeedExtract(packageFile, archivePath, 'hash文件内容为空', true, needExtractFiles)
      return
    }

    if (resourceHash !== appWorkHash) {
      logger.warn(`hash不匹配: ${packageFile}`)
      await handleNeedExtract(packageFile, archivePath, 'hash不匹配', true, needExtractFiles)
    } else {
      logger.info(`hash验证通过: ${packageFile}`)
    }
  } catch (error) {
    logger.error(`检查解压文件失败: ${packageFile}`, error)
    needExtractFiles.push(packageFile)
  }
}

/**
 * 检查并清理已解压的文件，根据哈希验证结果确定需要重新解压的文件列表
 * @param packageFiles - 需要检查的压缩包文件名数组
 * @returns 需要重新解压的文件名数组
 */
async function checkAndCleanExtractedFiles(packageFiles: string[]): Promise<string[]> {
  const needExtractFiles: string[] = []

  for (const packageFile of packageFiles) {
    await checkSingleFile(packageFile, needExtractFiles)
  }

  logger.info(`需要重新解压的文件数量: ${needExtractFiles.length}`)
  return needExtractFiles
}

/**
 * 复制单个文件
 * @param fileName - 文件名
 * @returns 复制结果
 */
async function copySingleFile(fileName: string): Promise<{ fileName: string, success: boolean, error?: string }> {
  const sourcePath = join(resourcePath, fileName)
  const targetPath = join(appWorkPath, fileName)

  try {
    // 检查源文件是否存在
    await fs.access(sourcePath)
    logger.info(`复制文件: ${fileName}`)
    await fs.copyFile(sourcePath, targetPath)
    return { fileName, success: true }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error)
    logger.error(`复制文件失败: ${fileName}`, error)
    return { fileName, success: false, error: errorMessage }
  }
}

/**
 * 确保用户数据目录存在
 */
async function ensureAppWorkPathExists(): Promise<void> {
  try {
    await fs.access(appWorkPath)
  } catch {
    logger.info(`创建用户数据目录: ${appWorkPath}`)
    await fs.mkdir(appWorkPath, { recursive: true })
  }
}

/**
 * 记录复制结果
 * @param copyResults - 复制结果数组
 */
function logCopyResults(copyResults: Array<{ fileName: string, success: boolean, error?: string }>): void {
  const successfulCopies = copyResults.filter(r => r.success).length
  const failedCopies = copyResults.filter(r => !r.success).length

  if (failedCopies === 0) {
    logger.info(`所有文件复制完成，共${successfulCopies}个文件`)
  } else {
    logger.warn(`文件复制完成，成功${successfulCopies}个，失败${failedCopies}个`)
    const failedFiles = copyResults.filter(r => !r.success).map(r => r.fileName)
    logger.warn(`失败的文件: ${failedFiles.join(', ')}`)
  }
}

/**
 * 从资源目录复制Python包及其哈希文件到用户数据目录
 * @param fileNames - 需要复制的压缩包文件名数组
 */
async function copyPythonFromResources(fileNames: string[]) {
  if (fileNames.length === 0) {
    logger.info('没有需要复制的文件')
    return
  }

  logger.info(`开始复制文件到用户数据目录: ${fileNames.join(', ')}`)

  // 确保目标目录存在
  await ensureAppWorkPathExists()

  // 将压缩包和他的校验文件复制到 appWorkPath
  const copyFileNames = [
    ...fileNames,
    ...fileNames.map(fileName => `${fileName}.sha256.txt`)
  ]

  const copyResults: Array<{ fileName: string, success: boolean, error?: string }> = []

  for (const fileName of copyFileNames) {
    const result = await copySingleFile(fileName)
    copyResults.push(result)
  }

  logCopyResults(copyResults)
}

/**
 * 启动后端服务的主入口函数
 */
export async function startBackend() {
  if (globalThis.serverRunning)
    return

  const initMsg = `{"type":"sync","msg":{"msg":"${toUnicode('正在初始化')}","step":1}}`
  mainToRender('scheduler-event', initMsg, undefined, true)

  // 检查 python envJson.SCHEDULER_NAME 是否正在运行
  const isRunning = await checkPythonRpaProcess()
  if (isRunning) {
    logger.info('rpa is already running')
    return
  }

  // 安装资源目录下的需要解压的 python 包
  const packageFiles = await checkNeedExtractPythonPackage()

  // 如果没有需要处理的包，直接启动服务
  if (packageFiles.length === 0) {
    logger.info('没有需要处理的python包')
    startServer()
    return
  }

  logger.info(`发现需要处理的python包: ${packageFiles.join(', ')}`)

  // 检查是否有需要解压的 python 包（比对 packageFiles 与 appWorkPath 下的文件 hash 是否一致）
  const needExtractFiles = await checkAndCleanExtractedFiles(packageFiles)

  // 如果没有需要解压的文件，直接启动服务
  if (needExtractFiles.length === 0) {
    logger.info('所有python包都已正确解压，无需重新解压')
    startServer()
    return
  }

  logger.info(`需要解压的文件: ${needExtractFiles.join(', ')}`)

  await copyPythonFromResources(needExtractFiles)
  const extractMsg = `{"type":"sync","msg":{"msg":"${toUnicode('正在解压Python包')}","step": 30 }}`
  mainToRender('scheduler-event', extractMsg, undefined, true)

  // 解压所有文件
  await extractAllFiles(needExtractFiles)

  startServer()
}

/**
 * 解压所有文件并清理压缩文件
 * @param files - 需要解压的文件名数组
 */
async function extractAllFiles(files: string[]): Promise<void> {
  for (const file of files) {
    await extractAndCleanFile(file)
  }
}

/**
 * 解压单个文件并清理压缩文件
 * @param file - 需要解压的文件名
 */
async function extractAndCleanFile(file: string): Promise<void> {
  const archivePath = join(appWorkPath, file)
  const outputDir = join(appWorkPath, file.replace('.7z', ''))

  try {
    await extract7z(archivePath, outputDir)
    logger.info(`成功解压: ${file}`)
    await deleteArchiveFile(archivePath, file)
  } catch (error) {
    logger.error(`解压失败: ${file}`, error)
  }
}

/**
 * 删除压缩文件
 * @param archivePath - 压缩文件路径
 * @param fileName - 文件名（用于日志）
 */
async function deleteArchiveFile(archivePath: string, fileName: string): Promise<void> {
  try {
    await fs.unlink(archivePath)
    logger.info(`已删除压缩文件: ${fileName}`)
  } catch (error) {
    logger.warn(`删除压缩文件失败: ${fileName}`, error)
  }
}
