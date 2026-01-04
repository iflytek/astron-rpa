/**
 * 全局运行状态的维护
 */
import { message } from 'ant-design-vue'
import { set } from 'lodash-es'
import { defineStore } from 'pinia'
import { computed, ref, shallowRef } from 'vue'

import { generateUUID } from '@/utils/common'

import type { StartExecutorParams } from '@/api/resource'
import { closeDataTable, deleteDataTable, getDataTable, startDataTableListenr, startExecutor, stopExecutor, updateDataTable } from '@/api/resource'
import Socket from '@/api/ws'
import { windowManager } from '@/platform'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'
import { useRunlogStore } from '@/stores/useRunlogStore'
import useUserSettingStore from '@/stores/useUserSetting.ts'
import type { Fun } from '@/types/common'
import { changeDebugging } from '@/views/Arrange/components/flow/hooks/useChangeStatus'

export type RunState = 'run' | 'free' | 'debug' // 执行状态

export const useRunningStore = defineStore('running', () => {
  const processStore = useProcessStore()
  const flowStore = useFlowStore()

  const running = ref<RunState>('free') // 全局运行状态 run-运行 debug-调试 free-停止  默认是free状态
  const debugData = ref<any>({}) // 调试信息, 包含当前调试的行号、断点等信息
  const debugDataVar = ref<any>({}) // 调试信息
  // 状态：starting 启动中， startSuccess 启动成功， startFailed 启动失败，running-运行中，runSuccess-运行成功，runFailed运行失败 stopping 停止中， stopSuccess 停止成功，  stopFailed 停止失败
  const status = ref('')
  // 数据表格内容
  const dataTable = shallowRef<RPA.IDataTableSheet>(null)
  let dataTableListenController: AbortController | null = null

  let debugReplyEventId = ''
  let runProjectId = null
  let RpaExecutorUrl = null
  let RpaExecutor = null

  const reset = () => {
    setRunning('free')
    debugData.value = {}
    RpaExecutor?.destroy()
    dataTableListenController?.abort()
    dataTable.value = null
  }

  const setRunning = (value: RunState) => {
    running.value = value
  }

  const setDebugData = (debugMsg, replyEventId: string) => {
    if (debugMsg.process_id && debugMsg.process_id !== processStore.activeProcessId) {
      processStore.checkActiveProcess(debugMsg.process_id)
    }
    if (debugMsg.debug_data?.data) {
      debugDataVar.value = debugMsg.debug_data.data
    }
    if (debugMsg.debug_data?.data) {
      debugDataVar.value = debugMsg.debug_data.data
    }
    if (debugMsg.debug_data?.is_break) {
      debugData.value = {
        ...debugMsg.debug_data,
        line: debugMsg.line,
        atomId: debugMsg.line_id,
        processId: debugMsg.process_id,
      }
    }
    // 调试下一步和继续时，执行器运行中，清空当前断点
    if (replyEventId === debugReplyEventId) {
      debugData.value = {}
    }
  }

  // 断点调试的原子能力
  const breakpointAtom = computed(() => {
    changeDebugging(debugData.value.atomId)
    if (debugData.value.atomId) {
      const findIdx = flowStore.simpleFlowUIData.findIndex(i => i.id === debugData.value.atomId)
      return flowStore.simpleFlowUIData[findIdx]
    }
    return null
  })

  const setStatus = (value: string) => {
    status.value = value
  }

  const setRunProjectId = (id: string | number) => {
    runProjectId = id
  }
  const getRunProjectId = () => {
    return runProjectId
  }

  // 创建ws连接
  const createSocket = (callback?: Fun) => {
    RpaExecutor = new Socket('', {
      url: RpaExecutorUrl,
      noInitCreat: true,
      isReconnect: true,
      reconnectCount: 5,
      isHeart: true,
      heartTime: 30 * 1000,
    })
    RpaExecutor.create(() => {
      callback && callback()
    })
    RpaExecutor.bindMessage((res) => { // 处理ws消息
      const result = JSON.parse(res)
      const { data: msg, event_time, channel, reply_event_id } = result
      if (!['debug_start', 'end'].includes(msg.status) && !reply_event_id) {
        useRunlogStore().addLog({ ...msg, event_time }) // 添加日志
      }

      running.value === 'debug' && setDebugData(msg, reply_event_id) // 处理调试数据

      // 执行结束、执行出错、执行器报错等异常退出时，关闭socket并重置状态
      if (['task_end', 'task_error'].includes(msg.status) || channel === 'exit') {
        setTimeout(() => {
          setStatus(msg.status === 'task_end' ? 'runSuccess' : 'runFailed')
          reset()
        }, 1000)
      }
    })
    RpaExecutor.bindOpen(() => {
      setStatus('startSuccess')
    })
    RpaExecutor.bindClose(() => {
      if (RpaExecutor.OPTIONS.reconnectCount === 0) {
        setStatus('startFailed')
        reset()
      }
    })
  }

  function getCookie(name: string) {
    const arr = document.cookie.match(new RegExp(`(^| )${name}=([^;]*)(;|$)`))
    if (arr != null)
      return unescape(arr[2])
    return ''
  }

  // 发送ws消息
  const send = (sendMsg) => {
    if (!RpaExecutor.isConnect()) {
      createSocket(() => {
        RpaExecutor.send(sendMsg)
      })
    }
    else {
      RpaExecutor.send(sendMsg)
    }
  }

  // 启动执行器并建立ws连接
  const start = async (params: StartExecutorParams) => {
    console.log('start: ', params)
    // http启动执行器，并获取执行器返回的ws url
    setStatus('starting')
    setRunProjectId(params.project_id)
    try {
      const res = await startExecutor({
        ...params,
        jwt: getCookie('jwt'),
        hide_log_window: !!useUserSettingStore().userSetting.commonSetting?.hideLogWindow,
        project_name: processStore.project.name,
      })
      useRunlogStore().clearLogs()
      RpaExecutorUrl = res.data.addr
      // 连接 ws
      createSocket()
      _startDataTableListenr()
    }
    catch {
      running.value = 'free'
      setStatus('startFailed')
      windowManager.maximizeWindow(true)
      dataTableListenController?.abort()
    }
  }

  const stop = (projectId: string | number) => {
    setStatus('stopping')
    stopExecutor({ project_id: projectId })
      .then(() => setStatus('stopSuccess'))
      .finally(() => reset())
  }

  const startRun = (projectId: string | number, processId?: string | number, line?: string | number, end_line?: string | number) => {
    const runParams: StartExecutorParams = { project_id: projectId, process_id: processId }

    line && (runParams.line = line)
    end_line && (runParams.end_line = end_line)

    start(runParams)
    running.value = 'run'
    windowManager.minimizeWindow()
  }

  const startDebug = (projectId: string | number, processId: string | number) => {
    const debugParams = { project_id: projectId, process_id: processId, debug: 'y' }
    running.value = 'debug'
    start(debugParams)
  }

  const nextStepDebug = () => {
    if (running.value !== 'debug')
      return message.warning('请先启动调试')
    const msg = {
      event_id: generateUUID(),
      event_time: Date.now(),
      channel: 'flow',
      key: 'next',
      data: {},
    }
    debugReplyEventId = msg.event_id
    send(msg)
  }

  const continueDebug = () => {
    if (running.value !== 'debug')
      return message.warning('请先启动调试')
    const msg = {
      event_id: generateUUID(),
      event_time: Date.now(),
      channel: 'flow',
      key: 'continue',
      data: {},
    }
    debugReplyEventId = msg.event_id
    send(msg)
  }

  const breakPointDebug = (isAdd: boolean, list?: Array<{ process_id: string | number, line: number }>) => {
    if (running.value !== 'debug')
      return
    const msg = {
      event_id: generateUUID(),
      event_time: Date.now(),
      channel: 'flow',
      key: isAdd ? 'add_break' : 'clear_break',
      data: {
        break_list: list,
      },
    }
    send(msg)
  }

  /**
   * 获取数据表格内容
   */
  const fetchDataTable = async () => {
    const data = await getDataTable(processStore.project.id)
    dataTable.value = data.sheets.find(it => it.name === data.active_sheet)
  }

  /**
   * 关闭数据表格监听
   * @returns
   */
  const closeDataTableListener = () => closeDataTable(processStore.project.id)

  /**
   * 更新单元格数据
   * @param cellData
   */
  const updateDataTableCell = async (cellData: Omit<RPA.IUpdateDataTableCell, 'sheet'>[]) => {
    const sheetName = dataTable.value?.name
    await updateDataTable(processStore.project.id, cellData.map(it => ({ sheet: sheetName, ...it })))
    // 同步到本地
    cellData.forEach(it => set(dataTable.value.data, [it.row, it.col], it.value))
    dataTable.value.max_row = dataTable.value.data.length
    dataTable.value.max_column = dataTable.value.data.length > 0 ? Math.max(...dataTable.value.data.map(it => it.length)) : 0
  }

  /**
   * 清空单元格数据
   */
  const clearDataTable = async () => {
    await deleteDataTable(processStore.project.id)
    dataTable.value = null
  }

  /**
   * 开启数据表格 sse 流式监听
   */
  const _startDataTableListenr = () => {
    dataTableListenController = startDataTableListenr(processStore.project.id)
  }

  return {
    dataTable,
    running,
    debugData,
    breakpointAtom,
    status,
    debugDataVar,
    reset,
    setRunning,
    startRun,
    startDebug,
    nextStepDebug,
    continueDebug,
    breakPointDebug,
    stop,
    setRunProjectId,
    getRunProjectId,
    fetchDataTable,
    updateDataTableCell,
    closeDataTableListener,
    clearDataTable,
  }
})
