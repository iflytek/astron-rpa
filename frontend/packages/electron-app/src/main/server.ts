import { exec } from 'node:child_process'
import fs from 'node:fs/promises'
import { join } from 'node:path'

import { toUnicode } from '../common'

import { readConfig } from './config'
import { axiosRequest, downloadWithAxiosProgress } from './download'
import { mainToRender } from './event'
import { extract7z, rename } from './file'
import logger from './log'
import { appWorkPath, confPath, pythonExe, resourcePath } from './path'
import { getMainWindow } from './window'

let setupProcessId

process.on('uncaughtException', (err) => {
  logger.error(`uncaughtException: ${err.message}`)
})

/**
 * 检查 python rpa_setup是否正在运行
 */
export function checkPythonRpaProcess() {
  return new Promise((resolve, reject) => {
    // linux 上检测 python 进程中 命令行中包含 rpa_setup 的进程
    if (process.platform !== 'win32') {
      exec('ps aux | grep "rpa_setup"', (error, stdout) => {
        logger.info('11', stdout)
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
        const isRunning = stdout.includes('rpa_setup')
        resolve(isRunning)
      })
    }
  })
}

/**
 * 启动服务
 */
export async function startServer() {
  // 查看是否已经启动 rpa_setup.exe
  const isRunning = await checkPythonRpaProcess()
  if (isRunning) {
    logger.info('rpa_setup is running')
    return
  }
  mainToRender('scheduler-event', `{"type":"sync","msg":{"msg":"${toUnicode('正在启动服务')}","step":51 }}`, undefined, true)

  const rpaSetup = exec(`${pythonExe} -m rpa_setup --conf=${confPath}`, { cwd: appWorkPath }, (error) => {
    if (error) {
      logger.error(`rpa_setup error: ${error}`)
    }
  })
  rpaSetup.stdout?.on('data', (data) => {
    msgFilter(data.toString())
  })

  rpaSetup.stderr?.on('data', (data) => {
    logger.info(`rpa_setup stderr: ${data.toString()}`)
  })

  rpaSetup.on('close', (code) => {
    if (code === 0) {
      logger.info('rpa_setup exited successfully.')
    }
    else {
      logger.error(`rpa_setup exited with error code: ${code}`)
    }
  })
  rpaSetup.on('error', (error) => {
    logger.error(`Failed to start rpa_setup: ${error.message}`)
  })
  await checkOld7zFilesProcess()
}
/**
 * 关闭服务
 */
export function stopServer(callback?: () => void) {
  const treeKill = require('tree-kill')
  treeKill(setupProcessId, 'SIGTERM', (err) => {
    if (err)
      logger.error(`Failed to stop rpa_setup: ${err.message}`)
    callback && callback()
  })
}
// 事件处理
function msgFilter(msg: string) {
  // 匹配以 ||emit_msg|| 开头的字符串
  const reg = /\|\|emit\|\|(.*)/
  const match = msg.match(reg)
  if (match) {
    // 发送到渲染进程
    const matchMsg = match[1].trim().replaceAll('"', '')
    const win = getMainWindow()
    win?.webContents.send(
      'scheduler-event',
      matchMsg,
    )
  }
}

// python 环境是否存在
function pythonExist() {
  return new Promise((resolve) => {
    fs.access(pythonExe)
      .then(() => {
        resolve(true)
      })
      .catch(() => {
        logger.info(`${pythonExe} is not exist`)
        resolve(false)
      })
  })
}
// 检查是否已经下载 python 包
function pythonPackageDownloaded(): Promise<Array<string>> {
  return new Promise((resolve, reject) => {
    // 获取appWorkPath目录下的所有文件
    fs.readdir(appWorkPath)
      .then((files) => {
        const files7z = files.filter(file => file.endsWith('.7z'))
        const extract7zFiles = files7z.map(file => join(appWorkPath, file))
        resolve(extract7zFiles)
      })
      .catch((err) => {
        logger.error(`Error reading appWorkPath: ${err}`)
        reject(new Error(`Error reading appWorkPath: ${err}`))
      })
  })
}
// 获取资源目录下的 python 包
function getPythonInResources() {
  return new Promise<boolean>((resolve, reject) => {
    const copyTasks: Promise<any>[] = []
    if (process.platform === 'win32') {
      fs.readdir(resourcePath)
        .then((files) => {
          files.forEach((file) => {
            if (file.endsWith('.7z')) {
              copyTasks.push(fs.copyFile(join(resourcePath, file), join(appWorkPath, file)))
            }
          })
          Promise.all(copyTasks).then(() => {
            logger.info('Copy python package from resources to appWorkPath finished')
            resolve(true)
          }).catch((err) => {
            logger.error(`Copy python package error: ${err}`)
            reject(new Error(`Copy python package error: ${err}`))
          })
        })
    }
    else {
      logger.info('No python package in resources for non-windows platform')
    }
  })
}
// 删除 旧的7z文件
function checkOld7zFilesProcess() {
  return new Promise((resolve, reject) => {
    if (process.platform === 'win32') {
      // check old 7z files in appWorkPath
      fs.readdir(appWorkPath).then((files) => {
        const deleteTasks: Promise<any>[] = []
        files.forEach((file) => {
          if (file.endsWith('.7z')) {
            deleteTasks.push(fs.unlink(join(appWorkPath, file)))
          }
        })
        if (deleteTasks.length > 0) {
          Promise.all(deleteTasks).then(() => {
            logger.info('Delete old 7z files in appWorkPath finished')
            resolve(true)
          }).catch((err) => {
            logger.error(`Delete old 7z files error: ${err}`)
            reject(new Error(`Delete old 7z files error: ${err}`))
          })
        }
        else {
          resolve(true)
        }
      })
    }
    else {
      resolve(true)
      logger.info('checkOld7zFilesProcess not impl for non-windows platform')
    }
  })
}

export function startBackend() {
  ; (async () => {
    if (globalThis.serverRunning)
      return
    const msg = `{"type":"sync","msg":{"msg":"${toUnicode('正在初始化')}","step":1}}`
    mainToRender('scheduler-event', msg, undefined, true)

    // 检查 python rpa_setup是否正在运行
    const isRunning = await checkPythonRpaProcess()
    if (isRunning) {
      logger.info('rpa is already running')
      return
    }

    // 检查是否存在 python 环境
    const pythonExistFlag = await pythonExist()
    if (pythonExistFlag) {
      logger.info(`${pythonExe} is exist, start server...`)
      startServer()
      return
    }

    await getPythonInResources()

    // 已存在 python 包
    const packagesDownloaded = await pythonPackageDownloaded()
    if (packagesDownloaded) {
      logger.info('Python package is downloaded, start extracting...')
      const msg = `{"type":"sync","msg":{"msg":"${toUnicode('正在解压Python包')}","step": 30 }}`
      mainToRender('scheduler-event', msg, undefined, true)
      await Promise.all(packagesDownloaded.map((file) => {
        return extract7z(file, file.replace('.7z', ''))
      }))
      startServer()
      return
    }

    const data = await getPythonUrl()
    logger.info('getPythonUrl data ', JSON.stringify(data))
    const downloadPromise: Array<Promise<any>> = []
    for (const key in data) {
      downloadPromise.push(downloadPython(key, data[key]))
    }
    await Promise.all(downloadPromise)
    startServer()
  })()
}

async function getPythonUrl() {
  try {
    const config = await readConfig()
    const base = config.remote_addr
    const url = `${base}/api/rpa_update/v2/rpa_soft/python?platform=${process.platform}&version=$arch=${process.arch}`
    logger.info(`getPythonUrl url: ${url}`)
    const data = await axiosRequest(url, 'get', {}, {})
    return data
  }
  catch (error) {
    logger.error('getPythonUrl error: ', error)
    mainToRender('scheduler-event', `{"type":"sync","msg":{"msg":"${toUnicode('获取Python下载地址失败')}","step":""}}`, undefined, true)
    return null
  }
}

async function downloadPython(name, url) {
  const tempName = `${name}_temp`
  const pythonPath = join(appWorkPath, name)
  const pythonFile = join(appWorkPath, `${name}.7z`)
  const tempPythonPath = join(appWorkPath, tempName)
  const tempPythonFile = join(appWorkPath, `${tempName}.7z`)

  const coreExist = await pythonExist()
  //  判断python 下载包是否存在， 存在则跳过下载
  if (coreExist) {
    logger.info(`${pythonFile} is already downloaded, start extracting...`)
    logger.info(`extract ${pythonFile} start...`)
    mainToRender('scheduler-event', `{"type":"sync","msg":{"msg":"${toUnicode('正在解压Python包')}","step": 30 }}`, undefined, true)
    //  解压python
    await extract7z(pythonFile, tempPythonPath) // 解压到临时目录
    await rename(tempPythonPath, pythonPath) //  重命名目录
    logger.info(`extract ${pythonFile} finished `)
    return true
  }
  //  判断python路径是否存在，不存在则创建
  if (!pythonPath) {
    await fs.mkdir(pythonPath)
  }
  try {
    // 下载python
    logger.info(`download ${tempPythonFile} start...`)
    await downloadWithAxiosProgress(url, tempPythonFile) //  下载python 临时压缩包
    logger.info(`download ${tempPythonFile} finished `)
    await rename(tempPythonFile, pythonFile) //   重命名文件
    logger.info(`rename ${tempPythonFile} finished `)

    // 解压python
    logger.info(`extract ${name} start...`)
    await extract7z(pythonFile, tempPythonPath) //  解压到临时目录
    logger.info(`extract ${name} finished `)
    await rename(tempPythonPath, pythonPath) //   重命名目录
    logger.info(`rename ${name} finished `)

    await fs.unlink(pythonFile) //   删除压缩包
    logger.info(`delete ${pythonFile} finished `)
  }
  catch (error) {
    logger.error(`downloadPython error: ${error}`)
    mainToRender('scheduler-event', `{"type":"sync","msg":{"msg":"${toUnicode('下载Python包失败')}","step":""}}`, undefined, true)
  }
  return true
}
