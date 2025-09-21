import { RpaPicker } from '@/api/pick'
import { WINDOW_NAME } from '@/constants'
import type { RECORD_EVENT } from '@/constants/record'
import { windowManager } from '@/platform'
import type { PickParams, RecordAction } from '@/types/resource'

// 通过 websocket 和拾取通信的一系列事件
export class RecordEvent {
  private socket: typeof RpaPicker
  private pickInfoResolve: PromiseWithResolvers<string>

  constructor(bindMessage: (message: any) => void, bindError: (error: any) => void) {
    RpaPicker.create(() => {
      this.listening()
    })

    // 绑定消息
    RpaPicker.bindMessage(bindMessage)

    // 绑定错误
    RpaPicker.bindError(bindError)

    this.socket = RpaPicker
  }

  private sendEvent(action: RecordAction, data = '') {
    console.log('sendEvent', action, data)

    const params: PickParams = {
      pick_sign: 'RECORD',
      record_action: action,
      data,
    }
    return this.socket.send(params)
  }

  destroy() {
    this.socket.destroy()
  }

  // 开启监听
  listening() {
    this.sendEvent('RECORD_LISTENING')
  }

  // 前端窗口hover住告知后端关闭拾取
  pausePick() {
    this.sendEvent('RECORD_AUTOMIC_HOVER_START')
  }

  // 前端告知后端hover结束开启拾取
  resumePick() {
    this.sendEvent('RECORD_AUTOMIC_HOVER_END')
  }

  //  录制结束，清理数据
  stopPick() {
    this.sendEvent('RECORD_END')
  }

  // 开始录制 - 开启拾取
  startRecord() {
    this.sendEvent('RECORD_START')
  }

  // 暂停录制 - 关闭拾取
  pauseRecord() {
    this.sendEvent('RECORD_PAUSE')
  }

  // 选择原子能力结束 - 前端发送信号，后端告知前端拾取信息
  getPickInfo() {
    this.pickInfoResolve = Promise.withResolvers<string>()

    this.sendEvent('RECORD_AUTOMIC_END')

    return this.pickInfoResolve.promise
  }

  pickInfoCallback(data: string) {
    this.pickInfoResolve?.resolve(data)
  }
}

export function emitToRecordMenu(type: RECORD_EVENT, data: any = '') {
  windowManager.emitTo({
    from: WINDOW_NAME.RECORD,
    target: WINDOW_NAME.RECORD_MENU,
    type,
    data,
  })
}

export function emitToMain(type: string, data: any = '') {
  windowManager.emitTo({
    from: WINDOW_NAME.RECORD,
    target: WINDOW_NAME.MAIN,
    type,
    data,
  })
}
