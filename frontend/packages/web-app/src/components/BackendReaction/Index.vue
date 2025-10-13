<script setup lang="ts">
import { message } from 'ant-design-vue'
/**
 *  全局主进程事件监听
 *  1、监听主进程事件，处理渲染进程需要执行的逻辑
 *  2、注意此文件中的代码以及导入的依赖尽量要干净，避免引入不必要的内容
 *  3、尽量使用BUS进行触发，减少导入
 */
import { h } from 'vue'
import { useRoute } from 'vue-router'

import { base64ToString } from '@/utils/common'
import BUS from '@/utils/eventBus'
import $loading from '@/utils/globalLoading'
import { storage } from '@/utils/storage'

import { endSchedulingMode, stopSchedulingTask } from '@/api/engine'
import http from '@/api/http'
import { taskCancel, taskNotify } from '@/api/task'
import authService from '@/auth/index'
import GlobalModal from '@/components/GlobalModal/index.ts'
import { WINDOW_NAME } from '@/constants'
import { DESIGNER } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import { utilsManager, windowManager } from '@/platform'
import { useAppModeStore } from '@/stores/useAppModeStore'
import { useRunningStore } from '@/stores/useRunningStore'
import useUserSettingStore from '@/stores/useUserSetting.ts'

export interface W2WType {
  from: string // 来源窗口
  target: string // 目标窗口
  type: string // 类型
  data?: any // 数据
}

const route = useRoute()
// 主进程与渲染进程通信
utilsManager.listenEvent('scheduler-event', (eventMsg) => {
  console.log('message: ', eventMsg)
  const msgString = base64ToString(eventMsg)
  const msgObject = JSON.parse(msgString)
  const { type, msg } = msgObject
  console.log('主进程消息: ', msgObject)
  switch (type) {
    case 'sync': {
      // 启动进度
      BUS.$emit('launch-progress', msg)
      break
    }
    case 'sync_cancel': {
      $loading.close(true)
      storage.set('route_port', msg?.route_port ?? '')
      storage.set('httpReady', '1', 'sessionStorage')
      http.init()
      http.resolveReadyPromise()
      loginAuto()
      break
    }
    case 'tip': {
      const msgContent = typeof msg === 'string' ? msg : msg.msg
      if (msg.type === 'error') {
        message.error(msgContent)
        $loading.close(true)
      }
      else {
        message.info(msgContent)
      }
      break
    }
    case 'crontab': {
      openTaskCountDown(msg)
      break
    }
    case 'executor_end': {
      if (useAppModeStore().appMode === 'normal') {
        executorHandle()
        useRunningStore().reset()
      }
      break
    }
    case 'log_report': {
      logReportHandle(msg)
      break
    }
    case 'edit_show_hide': {
      if (msg.type === 'hide') {
        windowManager.minimizeWindow()
      }
      else {
        windowManager.showWindow()
        windowManager.maximizeWindow(true)
      }
      break
    }
    case 'alert': {
      alertHandle(msg)
      break
    }
    case 'terminal_status': {
      // 监听调度模式时，终端状态-运行中、空闲，通知主进程切换托盘菜单
      utilsManager.invoke('tray_change', { mode: 'scheduling', status: msg.type })
      break
    }
    default:
      break
  }
})

// 渲染进程窗口之间通信
utilsManager.listenEvent('w2w', (eventMsg: W2WType) => {
  console.log('w2w: ', eventMsg)
  const { type, from, data } = eventMsg

  if (from === WINDOW_NAME.BATCH) {
    if (type === 'save' && data.noEmit !== 'true') {
      BUS.$emit('batch-done', { data: data.elementId, value: data.name })
    }
    BUS.$emit('batch-close')
    BUS.$emit('get-elements')

    windowManager.showWindow()
  }
  else if (from === WINDOW_NAME.RECORD) {
    if (type === 'close') {
      windowManager.closeWindow(WINDOW_NAME.RECORD_MENU)
      windowManager.closeWindow(WINDOW_NAME.RECORD)
      windowManager.showWindow()
    }
    else if (type === 'save') {
      BUS.$emit('record-save', data)
    }
  }
})

utilsManager.listenEvent('exit_scheduling_mode', () => {
  console.log('exit_scheduling_mode')
  useAppModeStore().setAppMode('normal') // 设置为正常模式
  endSchedulingMode()
})

// 调度模式，停止当前任务
utilsManager.listenEvent('stop_task', () => {
  console.log('stop_task')
  stopSchedulingTask()
  utilsManager.invoke('tray_change', { mode: 'scheduling', status: 'idle' }) // 改变托盘菜单
})

function loginAuto() {
  authService.init() // 初始化认证服务
  authService.getAuth().checkLogin(() => {    useRoutePush({ name: DESIGNER })
    setTimeout(() => {
      taskNotify({ event: 'login' })
    }, 3000)
  })
}

function openTaskCountDown(countDownInfo) {
  const { task_name, task_id, count_down } = countDownInfo
  let timer = null
  let count = Number(count_down)
  const highlighStyle = 'color: #4E68F6;font-weight: bold;font-size: 14px;'
  function getContent(count: number) {
    return h('div', [h('span', { style: highlighStyle }, `${count}s `), h('span', '之后，即将运行计划任务：'), h('span', { style: highlighStyle }, task_name)])
  }
  const modal = GlobalModal.info({
    title: '计划任务运行提示',
    content: () => getContent(count),
    closable: false,
    maskClosable: false,
    okText: '停止本次运行',
    onOk: () => {
      taskCancel({ task_id }).then(() => {
        message.success('计划任务已停止')
        modal.destroy()
        timer && clearInterval(timer)
      })
    },
    zIndex: 99999,
    centered: true,
    keyboard: false,
  })
  timer = setInterval(() => {
    count--
    modal.update({
      content: () => getContent(count),
    })
    if (count === 0) {
      modal.destroy()
      clearInterval(timer)
    }
  }, 1000)
}

function executorHandle() {
  windowManager.showWindow()
  windowManager.maximizeWindow(true)
}

function logReportHandle(msg) {
  const { log_path } = msg
  // 设置中心的详细日志是否启用，如果启用，则打开日志弹窗
  if (useUserSettingStore().userSetting.commonSetting.hideDetailLogWindow)
    return
  if (route.name !== 'arrange' && log_path) {
    BUS.$emit('open-log-modal', log_path)
  }
}

function alertHandle(msg) {
  if (msg.type === 'normal') {
    GlobalModal.warning({
      title: '提示',
      content: msg.msg,
      centered: true,
      okText: '知道了',
      zIndex: 99999,
    })
  }
}

window.onload = () => {
  if (storage.get('httpReady', 'sessionStorage') === '1') {
    http.resolveReadyPromise()
  }

  utilsManager.invoke('main_window_onload').catch(() => {
    // 在浏览器中，默认引擎已经启动，可以发送 http 请求了
    http.resolveReadyPromise()
  })
}
</script>

<template>
  <div style="display: none" />
</template>
