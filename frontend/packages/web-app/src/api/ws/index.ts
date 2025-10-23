import { storage } from '@/utils/storage'

const CONNECTOR_STATUS = 1 // 连接状态
const ignorePath = ['event_tracking'] // 忽略的路径
const ignoreMsg = ['ping', 'pong', 'error', 'ask'] // 忽略的消息

export interface SocketParamsType {
  url?: string
  port?: number
  noCreatRouters?: Array<string>
  noInitCreat?: boolean
  reconnectMaxTime?: number
  reconnectDelay?: number
  isReconnect?: boolean
  reconnectCount?: number
  isHeart?: boolean
  heartTime?: number
  timeout?: number
}

class Socket {
  ws: any

  RECONNEC_TTIMER = 0

  HEART_TIMER = 0

  CALLBACK: any // bindMessage回调函数

  OPENCALLBACK: any // open回调函数

  CLOSECALLBACK: any // close回调函数

  ERRORCALLBACK: any // error回调函数

  timer: any // 超时定时器

  OPTIONS = {
    url: 'ws://127.0.0.1',
    isHeart: false,
    heartTime: 60 * 1000, // 心跳时间间隔 60s
    port: 8003, // 默认端口号
    heartMsg: 'ping', // 心跳信息,默认为'ping'
    isReconnect: true, // 是否自动重连
    isDestory: false, // 是否销毁
    reconnectDelay: 10 * 1000, // 重连时间间隔 10s
    reconnectCount: -1, // -1 无限重连 0
    reconnectMaxTime: 20,
    noCreatRouters: [],
    noInitCreat: false, // 不在创建时初始化
    timeout: 10 * 1000, // 超时时间
  }

  eventId = '' // 消息id
  msgStack: any = [] // 消息栈

  constructor(router: string, params: SocketParamsType) {
    const port = storage.get('route_port') || params.port || this.OPTIONS.port
    const route = router || ''
    this.OPTIONS.url = `${this.OPTIONS.url}:${port}/${route}`
    if (params.url) {
      this.OPTIONS.url = params.url
    }
    if (params.isHeart)
      this.OPTIONS.isHeart = params.isHeart
    Object.assign(this.OPTIONS, params)
    if (!params.noInitCreat) {
      this.create()
    }
  }

  /**
   * 建立连接
   */
  create(callback?: any) {
    if (!this.OPTIONS.url) {
      throw new Error('地址不存在，无法建立通道')
    }
    this.OPTIONS.isDestory = false
    delete this.ws
    this.OPTIONS.url = `${this.OPTIONS.url}`
    this.ws = new WebSocket(this.OPTIONS.url)
    this.timeout()
    this.onopen(callback)
    this.onclose()
    this.onmessage()
    this.onerror()
  }

  /**
   * 心跳 60s 一次
   */
  heart() {
    this.send({ channel: this.OPTIONS.heartMsg })
    this.HEART_TIMER = window.setTimeout(() => {
      clearTimeout(this.HEART_TIMER)
      this.heart()
    }, this.OPTIONS.heartTime)
  }

  /**
   * timeout
   */
  timeout() {
    this.timer = setTimeout(() => {
      this.ws.close()
    }, this.OPTIONS.timeout)
  }

  /**
   * 自定义连接成功事件
   * 如果callback存在，调用callback，不存在调用OPTIONS中的回调
   * @param {Function} callback 回调函数
   */
  onopen(callback?: any) {
    this.ws.onopen = (event: any) => {
      console.log('onopen:', this.OPTIONS.url)
      clearTimeout(this.timer) // 清除超时定时器
      if (this.OPTIONS.isHeart)
        this.heart()
      this.msgStack = []
      clearTimeout(this.RECONNEC_TTIMER) // 清除重连定时器
      this.OPENCALLBACK
        ? this.OPENCALLBACK(event)
        : typeof callback === 'function' && callback(event)
    }
  }

  /**
   * 自定义关闭事件
   * 如果callback存在，调用callback，不存在调用OPTIONS中的回调
   * @param {Function} callback 回调函数
   */
  onclose(callback?: any) {
    if (this.ws) {
      this.ws.onclose = (event: any) => {
        console.log('onclose:', event)
        clearTimeout(this.timer) // 清除超时定时器
        this.msgStack = []
        if (this.OPTIONS.isHeart)
          clearTimeout(this.HEART_TIMER)
        if (!this.OPTIONS.isDestory && this.OPTIONS.isReconnect) {
          // 非主动销毁，且需要重连
          this.reconnect()
        }
        this.CLOSECALLBACK
          ? this.CLOSECALLBACK(event)
          : typeof callback === 'function' && callback(event)
      }
    }
  }

  /**
   * 自定义错误事件
   * 如果callback存在，调用callback，不存在调用OPTIONS中的回调
   * @param {Function} callback 回调函数
   */
  onerror(callback?: any) {
    this.ws.onerror = (event: any) => {
      console.log('onerror:', event)
      clearTimeout(this.timer)
      this.msgStack = []
      this.ERRORCALLBACK ? this.ERRORCALLBACK(event) : typeof callback === 'function' && callback(event)
    }
  }

  /**
   * 自定义消息监听事件
   * 如果callback存在，调用callback，不存在调用OPTIONS中的回调
   */
  onmessage() {
    this.ws.onmessage = (event: any) => {
      const dataAll = JSON.parse(event.data) // 一定保证返回的数据是json格式
      if (ignoreMsg.includes(dataAll.channel))
        return
      this.eventId = dataAll.event_id
      if (typeof dataAll.data === 'object') {
        this.CALLBACK && this.CALLBACK(JSON.stringify(dataAll))
      }
      else {
        this.CALLBACK && this.CALLBACK(dataAll)
      }
    }
  }

  bindMessage(callback?: any) {
    if (callback) {
      this.CALLBACK = callback
    }
  }

  bindClose(callback?: any) {
    if (callback) {
      this.CLOSECALLBACK = callback
    }
  }

  bindError(callback?: any) {
    if (callback) {
      this.ERRORCALLBACK = callback
    }
  }

  bindOpen(callback?: any) {
    if (callback) {
      this.OPENCALLBACK = callback
    }
  }

  send(data: object) {
    if (!this.ws || this.ws.readyState !== this.ws.OPEN) {
      return new Error('没有连接到服务器，无法推送')
    }
    this.sendText(JSON.stringify(data))
  }

  sendText(data: string) {
    if (typeof data !== 'string')
      throw new Error('请发送文本消息')
    this.msgStack.pop()
    this.ws.send(data)
  }

  /**
   * 判断是否已连接
   */
  isConnect() {
    return this.ws && this.ws.readyState === CONNECTOR_STATUS
  }

  /**
   * 连接事件
   */
  reconnect() {
    if (this.OPTIONS.reconnectCount === 0 || !this.OPTIONS.isReconnect) {
      // 不重连
      clearTimeout(this.RECONNEC_TTIMER)
      this.OPTIONS.isDestory = true
      return
    }
    if (this.OPTIONS.isReconnect && this.OPTIONS.reconnectCount === -1) {
      // 不限重连 不记录重连日志
      this.RECONNEC_TTIMER = window.setTimeout(() => {
        this.create()
      }, this.OPTIONS.reconnectDelay)
      return
    }

    this.RECONNEC_TTIMER = window.setTimeout(() => {
      // 开始重连
      this.create()
    }, this.OPTIONS.reconnectDelay)

    this.OPTIONS.reconnectCount--
  }

  /**
   * 销毁
   */
  destroy() {
    clearTimeout(this.HEART_TIMER) // 清除心跳定时器
    clearTimeout(this.RECONNEC_TTIMER) // 清除重连定时器
    clearTimeout(this.timer)
    this.OPTIONS.isDestory = true
    this.ws && this.ws.close()
    this.CALLBACK = null
    this.OPENCALLBACK = null
    this.CLOSECALLBACK = null
    this.ERRORCALLBACK = null
    this.ws = null
    this.msgStack = []
  }

  /**
   * 忽略心跳，日志记录接口信息
   */
  ignoreLog(msg: string) {
    const fitPath = ignorePath.find(i => this.OPTIONS.url.includes(i))
    const fitMsg = ignoreMsg.find(j => msg.includes(j))
    return fitPath || fitMsg
  }
}

export default Socket
