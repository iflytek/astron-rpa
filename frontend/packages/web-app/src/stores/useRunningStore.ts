/**
 * 全局运行状态的维护
 */
import { message } from 'ant-design-vue'
import { set } from 'lodash-es'
import { defineStore } from 'pinia'
import { computed, ref, shallowRef } from 'vue'

import { generateUUID } from '@/utils/common'
import { baseUrl } from '@/utils/env'

import type { StartExecutorParams } from '@/api/resource'
import { closeDataTable, deleteDataTable, getDataTable, startDataTableListener, startExecutor, stopExecutor, updateDataTable } from '@/api/resource'
import Socket from '@/api/ws'
import { WINDOW_NAME } from '@/constants'
import { windowManager, type CreateWindowOptions } from '@/platform'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'
import { useRunlogStore } from '@/stores/useRunlogStore'
import useUserSettingStore from '@/stores/useUserSetting.ts'
import type { Fun, AnyObj } from '@/types/common'
import { changeDebugging } from '@/views/Arrange/components/flow/hooks/useChangeStatus'
import { getCookie, sleep } from '@/utils/common'

export type RunState = 'run' | 'free' | 'debug' | 'silence' // 执行状态

export const useRunningStore = defineStore('running', () => {
  const processStore = useProcessStore()
  const flowStore = useFlowStore()
  const userSettingStore = useUserSettingStore()
  const runLogStore = useRunlogStore()

  // 执行过程中创建的窗口 label (后续用于关闭窗口)
  let createdWindowLabels: string[] = []
  // 全局运行状态 run-运行 debug-调试 free-停止 silence-静默（在执行器列表执行） 默认是free状态
  const running = ref<RunState>('free')
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
  let RpaExecutor: Socket | null = null

  const reset = () => {
    setRunning('free')
    debugData.value = {}
    RpaExecutor?.destroy()
    dataTableListenController?.abort()
    closeDataTableListener()
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
    RpaExecutor.bindMessage(async (res: string) => { // 处理ws消息
      const result = JSON.parse(res)
      const { data: msg, event_time, channel, reply_event_id } = result

      if (running.value !== 'silence' && !['debug_start', 'end'].includes(msg.status) && !reply_event_id) {
        runLogStore.addLog({ ...msg, event_time }) // 添加日志
      }

      // 打开自定义表单窗口
      if (result.key === 'sub_window' && msg.name === 'userform') {
        const windowLabel = `${WINDOW_NAME.USERFORM}-${generateUUID()}`
        createdWindowLabels.push(windowLabel)

        // 打开自定义表单窗口后，点击表单提交，有一个消息回复
        const replyEventData = {
          key: result.key,
          channel: result.channel,
          reply_event_id: result.event_id,
          // 回复消息，方向正好相反
          uuid: result.send_uuid,
          send_uuid: result.uuid,
        }

        // 构建 URL，如果有 params 则添加查询参数
        const options: CreateWindowOptions = {
          url: `${baseUrl}/${WINDOW_NAME.USERFORM}.html?option=${JSON.stringify(msg.option)}&reply=${JSON.stringify(replyEventData)}`,
          title: 'iflyrpa-window',
          label: windowLabel,
          alwaysOnTop: true,
          position: 'center',
          width: 500,
          height: 400,
          resizable: false,
          skipTaskbar: true,
          transparent: false,
          show: false,
        }

        windowManager.createWindow(options)
      }

      // 打开多轮对话窗口
      if (result.key === 'sub_window' && msg.name === 'multichat') {
        const windowLabel = `${WINDOW_NAME.MULTICHAT}-${generateUUID()}`
        createdWindowLabels.push(windowLabel)

        // 打开AI对话窗口后，点击保存，有一个消息回复
        const replyEventData = {
          key: result.key,
          channel: result.channel,
          reply_event_id: result.event_id,
          // 回复消息，方向正好相反
          uuid: result.send_uuid,
          send_uuid: result.uuid,
        }

        const queryString = new URLSearchParams({ ...msg.params, reply: JSON.stringify(replyEventData) }).toString()
        const options: CreateWindowOptions = {
          url: `${baseUrl}/${WINDOW_NAME.MULTICHAT}.html?${queryString}`,
          label: windowLabel,
          alwaysOnTop: true,
          position: 'center',
          width: 800,
          height: 600,
          skipTaskbar: true,
          transparent: true,
        }
        windowManager.createWindow(options)
      }

      if (running.value === 'debug') {
        setDebugData(msg, reply_event_id) // 处理调试数据
      }

      // 执行结束、执行出错、执行器报错等异常退出时，关闭socket并重置状态
      if (['task_end', 'task_error'].includes(msg.status) || channel === 'exit') {
        await sleep(1000)
        setStatus(msg.status === 'task_end' ? 'runSuccess' : 'runFailed')
        reset()
      }
    })
    RpaExecutor.create(() => callback?.())
    RpaExecutor.bindOpen(() => setStatus('startSuccess'))
    RpaExecutor.bindClose(() => {
      if (RpaExecutor.OPTIONS.reconnectCount === 0) {
        setStatus('startFailed')
        reset()
      }
    })
  }

  // 关闭执行过程中创建的窗口
  const closeCreatedWindows = () => {
    // 关闭日志弹窗
    windowManager.closeWindow(WINDOW_NAME.LOGWIN)
    createdWindowLabels.forEach(label => windowManager.closeWindow(label))
    createdWindowLabels = []
  }

  // 发送ws消息
  const send = (sendMsg) => {
    if (RpaExecutor.isConnect()) {
      RpaExecutor.send(sendMsg)
    }
    else {
      createSocket(() => RpaExecutor.send(sendMsg))
    }
  }

  // 发送回复数据
  const sendReplyMessage = (data: AnyObj) => {
    send({ ...data, event_id: generateUUID(), event_time: Date.now() })
  }

  // 启动执行器并建立ws连接
  const start = async (params: StartExecutorParams) => {
    console.log('start: ', params)
    // http启动执行器，并获取执行器返回的ws url
    setStatus('starting')
    setRunProjectId(params.project_id)
    try {
      RpaExecutorUrl = await startExecutor({
        ...params,
        jwt: getCookie('jwt'),
        hide_log_window: !userSettingStore.openLogModalAfterRun,
        project_name: params.project_name || processStore.project.name,
      })
      // 连接 ws
      createSocket()

      if (running.value !== 'silence') {
        runLogStore.clearLogs()
        _startDataTableListener()
      }
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
    processStore.isComponent && (runParams.is_custom_component = processStore.isComponent)

    running.value = 'run'
    start(runParams)
    windowManager.minimizeWindow()
  }

  const startDebug = (projectId: string | number, processId: string | number) => {
    const debugParams: StartExecutorParams = { project_id: projectId, process_id: processId, debug: 'y' }

    processStore.isComponent && (debugParams.is_custom_component = processStore.isComponent)

    running.value = 'debug'
    start(debugParams)
  }

  const startSlice = async (editObj: AnyObj) => {
    running.value = 'silence'
    await start({
      project_id: editObj.robotId,
      exec_position: editObj.exec_position || 'PROJECT_LIST',
      recording_config: JSON.stringify(userSettingStore.userSetting.videoForm),
      project_name: editObj.robotName,
      open_virtual_desk: editObj.open_virtual_desk || false,
    })
    windowManager.minimizeWindow()
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
    dataTable.value = null
    await deleteDataTable(processStore.project.id)
  }

  /**
   * 开启数据表格 sse 流式监听
   */
  const _startDataTableListener = () => {
    dataTableListenController = startDataTableListener(processStore.project.id, (res) => {
      if (res.event === 'file_deleted') {
        dataTable.value = null
      }
      else if (res.event === 'file_changed') {
        fetchDataTable()
      }
    })
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
    startSlice,
    nextStepDebug,
    continueDebug,
    breakPointDebug,
    stop,
    getRunProjectId,
    fetchDataTable,
    updateDataTableCell,
    closeDataTableListener,
    clearDataTable,
    sendReplyMessage,
    closeCreatedWindows,
  }
})
