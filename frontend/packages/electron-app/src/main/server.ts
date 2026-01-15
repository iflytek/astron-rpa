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

  const rpaSetup = spawn(pythonExe, ['-m', envJson.SCHEDULER_NAME, '--conf', confPath], { cwd: appWorkPath, detached: true, windowsHide: true })
 
  rpaSetup.stdout?.on('data', (data) => msgFilter(data.toString()))

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
 * 检查单个文件是否需要重新解压
 * @param packageFile - 压缩包文件名
 * @returns 是否需要重新解压
 * */
async function checkSingleFile(packageFile: string): Promise<boolean> {
  const archiveName = packageFile.replace('.7z', '')
  const archivePath = join(appWorkPath, archiveName)
  const hashFileName = `${packageFile}.sha256.txt`
  const resourceHashPath = join(resourcePath, hashFileName)
  const appWorkHashPath = join(appWorkPath, hashFileName)

  logger.info(`检查文件: ${packageFile}`)

  try {
    // 1. 检查资源目录中的hash文件是否存在
    await fs.access(resourceHashPath)

    // 2. 并行检查解压文件和用户数据目录中的hash文件是否存在
    const [archiveExists, hashFileExists] = await Promise.all([
      fs.access(archivePath).then(() => true).catch(() => false),
      fs.access(appWorkHashPath).then(() => true).catch(() => false)
    ])

    // 3. 如果解压文件不存在，需要重新解压
    if (!archiveExists) {
      logger.warn(`解压文件不存在: ${packageFile}`)
      return true
    }

    // 4. 如果用户数据目录中的hash文件不存在，需要重新解压
    if (!hashFileExists) {
      logger.warn(`用户数据目录hash文件不存在: ${packageFile}`)
      return true
    }

    // 5. 并行读取两个hash文件的内容
    const [resourceHash, appWorkHash] = await Promise.all([
      readHashFile(resourceHashPath),
      readHashFile(appWorkHashPath)
    ])

    // 6. 如果任何一个hash文件内容为空，需要重新解压
    if (!resourceHash || !appWorkHash) {
      logger.warn(`hash文件内容为空: ${packageFile}`)
      return true
    }

    // 7. 比较hash值，如果不匹配则需要重新解压
    if (resourceHash !== appWorkHash) {
      logger.warn(`hash不匹配: ${packageFile}`)
      return true
    } else {
      logger.info(`hash验证通过: ${packageFile}`)
    }

    return false
  } catch (error) {
    logger.error(`检查解压文件失败: ${packageFile}`, error)
    return true
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
    const needExtract = await checkSingleFile(packageFile)
    if (needExtract) {
      needExtractFiles.push(packageFile)
    }
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
  await Promise.all(needExtractFiles.map(file => extractAndCleanFile(file)))

  startServer()
}

/**
 * 解压单个文件并清理压缩文件
 * @param file - 需要解压的文件名
 */
async function extractAndCleanFile(file: string): Promise<void> {
  const archivePath = join(appWorkPath, file)
  const outputDir = join(appWorkPath, file.replace('.7z', ''))
  const tempOutputDir = `${outputDir}.temp`

  const clearAll = () => Promise.all([
    fs.rm(tempOutputDir, { recursive: true, force: true }),
    fs.rm(outputDir, { recursive: true, force: true })
  ])

  try {
    // 1. 确保临时目录/目标目录不存在
    logger.info("删除已解压目录")
    await clearAll()

    // 2. 解压到临时目录
    logger.info(`开始解压到临时目录: ${tempOutputDir}`)
    await extract7z(archivePath, tempOutputDir)
    logger.info(`临时目录解压成功: ${tempOutputDir}`)

    // 3. 将临时目录重命名为目标目录
    await fs.rename(tempOutputDir, outputDir)
    logger.info(`成功解压: ${outputDir}`)

    // 4. 删除原始压缩文件
    await deleteArchiveFile(archivePath, file)
  } catch (error) {
    logger.error(`解压失败: ${file}`, error)
    // 清理所有解压目录
    clearAll()
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
