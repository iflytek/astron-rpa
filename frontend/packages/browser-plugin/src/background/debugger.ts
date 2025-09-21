import { Utils } from './utils'

const isFirefox = Utils.getNavigatorUserAgent() === '$firefox$' // 火狐浏览器

export function checkDebuggerDetached(tabId, attempts = 0) {
  return new Promise((resolve, reject) => {
    if (attempts > 10) {
      reject(new Error('检测 detach 状态超时'))
      return
    }

    chrome.debugger.getTargets((targets) => {
      const stillAttached = targets.some(target => target.tabId === tabId)

      if (!stillAttached) {
        resolve(true)
      }
      else {
        setTimeout(() => checkDebuggerDetached(tabId, attempts + 1), 500)
      }
    })
  })
}

/**
 * 调试器相关功能
 * 1，附加调试器
 * 2，监听事件， 获取到执行上下文
 * 3，执行代码
 * 4，断开调试器
 */

/** @format */
const Debugger = {
  attached: false,
  tabId: 0,
  frameContextIdMap: {
    0: [], // 默认frameId 0 对应的 executionContextIds
  } as Record<string, number[]>, // 绑定frameId 和executionContextIds
  enableRuntime: (tabId: number) => {
    return new Promise((resolve, reject) => {
      chrome.debugger.sendCommand({ tabId }, 'Runtime.enable', {}, () => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError)
          reject(chrome.runtime.lastError)
        }
        else {
          resolve(true)
        }
      })
    })
  },
  attachDebugger: (tabId: number) => {
    return new Promise((resolve, reject) => {
      if (Debugger.attached) {
        return reject(new Error('Debugger is already attached to a tab'))
      }
      chrome.debugger.attach({ tabId }, '1.3', () => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError)
          reject(chrome.runtime.lastError)
        }
        else {
          console.log('Debugger attached successfully')
          Debugger.tabId = tabId
          Debugger.attached = true
          resolve(true)
        }
      })
    })
  },
  detachDebugger: (tabId: number) => {
    return new Promise((resolve) => {
      chrome.debugger.detach({ tabId }, () => {
        console.log('Debugger detached successfully')
        Debugger.attached = false
        Debugger.frameContextIdMap = { 0: [] }
        resolve(true)
      })
    })
  },
  getFrameTree: async (tabId: number) => {
    return new Promise((resolve, reject) => {
      chrome.debugger.sendCommand({ tabId }, 'Page.getFrameTree', {}, (result) => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError)
          reject(chrome.runtime.lastError)
        }
        else {
          resolve(result)
        }
      })
    })
  },
  evaluate: async (tabId: number, code: string, frameId: number) => {
    // console.log('code: ', code)
    code = `(function() { ${code} })()`

    await Debugger.attachDebugger(tabId)
    await Debugger.enableRuntime(tabId)
    await Utils.wait(1)

    const currentFrameContextIds = Debugger.frameContextIdMap[frameId] || []
    if (!currentFrameContextIds.length) {
      throw new Error('未找到执行上下文，请确保页面已加载完成')
    }
    const allPromise = currentFrameContextIds?.map(item => chrome.debugger.sendCommand({ tabId }, 'Runtime.evaluate', { expression: code, contextId: item }))
    const allRes = await Promise.all(allPromise)
    const successRes = allRes.find(item => !item.exceptionDetails) // 成功
    const failRes = allRes.find(item => item.exceptionDetails) // 失败
    console.log('evaluate successRes: ', successRes, 'evaluate failRes: ', failRes)
    await Debugger.detachDebugger(tabId)
    if (successRes) {
      return successRes.result.value || ''
    }
    else if (failRes) {
      throw new Error(failRes.result.description)
    }
    else {
      throw new Error('执行失败，未获取到结果')
    }
  },
}
/**
 * 监听 console.log，获取 frameId 和 executionContextId 的对应关系
 * content 中的 iflyrpa_debugger_on 代码会打印 frameId
 */
if (!isFirefox) {
  chrome.debugger.onEvent.addListener(async (source, method, params) => {
    if (source.tabId !== Debugger.tabId)
      return
    if (method !== 'Runtime.consoleAPICalled' || params.type !== 'log' || !params.args?.length)
      return

    const logValue = params.args[0]?.value || ''
    const executionContextId = params.executionContextId

    if (logValue.includes('rpa_debugger_on')) {
      const frameId = `${logValue.split(':')[1]}` // 统一用字符串键
      if (!Debugger.frameContextIdMap[frameId]) {
        Debugger.frameContextIdMap[frameId] = [executionContextId]
      }
      if (!Debugger.frameContextIdMap[frameId].includes(executionContextId)) {
        Debugger.frameContextIdMap[frameId].push(executionContextId)
      }
    }
  })
  chrome.debugger.onDetach.addListener(() => {
    Debugger.attached = false
  })
}

export { Debugger }
