<script lang="tsx">
import { CheckCircleFilled, ClockCircleOutlined, CloseCircleFilled, DoubleLeftOutlined, DoubleRightOutlined, IssuesCloseOutlined, LoadingOutlined } from '@ant-design/icons-vue'
import { Tooltip } from 'ant-design-vue'
import { isEmpty } from 'lodash-es'

import { generateUUID, sleep } from '@/utils/common'

import { getUserSetting } from '@/api/setting'
import Socket from '@/api/ws'
import { windowManager } from '@/platform'

const DEFAULT_STOPRUN_SHORTKEY = 'Shift + F5'

const iconStatusMap = {
  current: <LoadingOutlined class="text-[rgba(0,0,0,0.85) ] dark:text-[#fff]" />,
  success: <CheckCircleFilled class="text-primary" />,
  error: <CloseCircleFilled class="text-error" />,
  error_skip: <IssuesCloseOutlined />,
}

async function closeWindow(immediate: boolean) {
  if (!immediate) {
    await sleep(500)
  }

  windowManager.closeWindow()
}

export default {
  name: 'LogWindow',
  data() {
    return {
      logData: [],
      stopRunText: DEFAULT_STOPRUN_SHORTKEY,
      projectName: '',
      isSiderMinimized: false,
      maxLine: 1,
      currentLine: 0,
      countTime: 0,
      countTimer: 0 as unknown as ReturnType<typeof setInterval>,
      logError: false,
      logFrom: '',
      ws: null,
    }
  },
  mounted() {
    this.clearLogData()
    this.startCount()
    const searchParams = new URLSearchParams(window.location.search)
    this.createWs(searchParams.get('ws'))
    this.projectName = searchParams.get('title') || '执行日志'
    this.isSiderMinimized = searchParams.get('mini') === '1'
  },
  methods: {
    createWs(url: string) {
      this.ws = new Socket('', {
        url,
        isReconnect: true,
        reconnectCount: 10,
        isHeart: true,
        heartTime: 30 * 1000,
      })
      this.ws.bindMessage((res: string) => { // 处理ws消息
        const { data, channel } = JSON.parse(res)

        this.getLogData(data)

        // 执行结束、执行出错、执行器报错等异常退出时，关闭socket并重置状态
        if (['task_end', 'task_error'].includes(data.status) || channel === 'exit') {
          closeWindow(true)
        }
      })
    },
    // 开始计时
    startCount() {
      this.countTimer && clearInterval(this.countTimer)
      this.countTimer = setInterval(() => {
        this.countTime += 1
      }, 1000)
    },
    getLogData(logItem) {
      // 判断是否重复
      // const isRepeat = this.logData.some(item => isEqual(item, logItem))
      // if (isRepeat)
      //   return

      const { log_type, status, max_line, line } = logItem
      if (log_type === 'flow') {
        if (status === 'init') {
          // 初始化
          this.countTime = 0
          this.startCount()
          this.maxLine = max_line
        }
        if (status === 'task_end') {
          setTimeout(() => clearInterval(this.countTimer), 1000)
        }
        if (line) {
          // 当前行
          this.currentLine = Math.max(this.currentLine, line)
        }
      }

      this.logData.push(logItem)
      if (this.logData.length > 2) {
        // 最多显示2条
        this.logData.shift()
      }
    },
    closeCurrentWin() {
      this.clearLogData()
    },
    // 重制初始状态
    resetLogDataPage() {
      this.logData = []
      this.projectName = ''
      this.isSiderMinimized = false
      this.maxLine = 1
      this.currentLine = 0
      this.logError = false
    },
    clearLogData() {
      this.resetLogDataPage()
    },
    // 停止快捷键
    async stopShortcut() {
      const userSetting = await getUserSetting()
      const shortcutConfig = userSetting.shortcutConfig || {}
      let stopRunText = shortcutConfig?.stopRun?.text || DEFAULT_STOPRUN_SHORTKEY
      if (stopRunText.includes('按键')) {
        stopRunText = DEFAULT_STOPRUN_SHORTKEY
      }
      this.stopRunText = stopRunText
    },
    // 右侧收起最小化
    async siderMinimize() {
      this.isSiderMinimized = !this.isSiderMinimized
      windowManager.minLogWindow(this.isSiderMinimized)
    },
    // 停止按钮
    clickStop() {
      // 发送停止请求后关闭窗口
      this.ws?.send({
        event_id: generateUUID(),
        event_time: new Date().getTime(),
        channel: 'flow',
        key: 'close', // 关键标识key
        data: {},
      })
      closeWindow(false)
    },
    // icon 状态
    getIconState(item, index) {
      let indexStatus = index === 1 ? 'current' : 'success'
      indexStatus = this.logData.length === 1 ? 'current' : indexStatus // 仅一条时
      indexStatus = item.log_level === 'error' ? 'error' : indexStatus
      return iconStatusMap[indexStatus]
    },
    // 运行开始计时
    getCountTime(time) {
      const hours = Math.floor(time / 3600).toString().padStart(2, '0')
      const minutes = Math.floor((time % 3600) / 60).toString().padStart(2, '0')
      const seconds = (time % 60).toString().padStart(2, '0')
      return `${hours}:${minutes}:${seconds}`
    },
    // 底部运行进度
    getPercent() {
      return Math.floor((this.currentLine / this.maxLine) * 100)
    },
    getProcessStyle() {
      const color = this.logError ? '#ffeeee' : '#e6f4ff'
      const percent = this.getPercent()

      if (percent === 0)
        return ''

      return `background: linear-gradient(to right, ${color} ${percent}%, #FFFFFF 0%);`
    },
    renderLogContent() {
      if (isEmpty(this.logData)) {
        return <div class="content-log">正在进行初始化...</div>
      }

      return this.logData.map((item, index) => (
        <div class="content-log" key={index}>
          {this.getIconState(item, index)}
          &nbsp;
          <span>{item.msg_str}</span>
        </div>
      ))
    },
  },
  render() {
    return (
      <div class="logData bg-[#fff] dark:bg-[#1f1f1f]">
        <div class={this.isSiderMinimized ? 'logData-sider sider-min' : 'logData-sider'} onClick={this.siderMinimize}>
          {
            this.isSiderMinimized
              ? <DoubleLeftOutlined class="text-white" />
              : <DoubleRightOutlined class="text-white" />
          }
        </div>
        <div class={this.isSiderMinimized ? 'hidden' : 'logData-container'} style={this.getProcessStyle()}>
          <div class="logData-title p-[10px]" data-tauri-drag-region>
            <div class="title-text flex items-center">
              <div class="w-[20px] h-[20px] bg-primary rounded-[2px] flex items-center justify-center mr-[10px]">
                <rpa-icon name="robot" class="w-[14px] h-[14px] text-[#fff]" />
              </div>
              <div class="h-[20px] leading-5 text-sm font-semibold">
                {this.projectName || '执行日志'}
              </div>
            </div>
            <div class="flex items-center gap-3">
              <rpa-hint-icon name="remove" enableHoverBg class="text-base" onClick={this.siderMinimize} />
              <rpa-hint-icon name="close" enableHoverBg class="text-base" onClick={this.clickStop} />
            </div>
          </div>
          <div class="logData-content">{this.renderLogContent()}</div>
          <div class="logData-footer px-[10px]">
            <span>
              <ClockCircleOutlined class="text-[rgba(0,0,0,0.85) ] dark:text-[#fff] mr-[5px]" />
              <span>{this.getCountTime(this.countTime)}</span>
            </span>
            <Tooltip
              placement="topLeft"
              class="text-sm"
              title={this.$t('quitShortcut', { key: this.stopRunText })}
              overlayClassName="whitespace-nowrap"
            >
              <span class="stop-button text-error text-[14px]" onClick={this.clickStop}>
                <rpa-icon name="cancel" class="w-[14px] h-[14px]" />
                <span class="text-[12px]">终止</span>
              </span>
            </Tooltip>
          </div>
        </div>
      </div>
    )
  },
}
</script>

<style lang="scss">
.logData {
  width: 100%;
  height: 100%;
  text-align: left;
  border-radius: 8px;
  overflow-y: hidden;
  display: flex;

  &-sider {
    height: 100%;
    width: 20px;
    background-color: $color-primary;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
  }

  .sider-min {
    width: 34px;
  }

  &-container {
    flex: 1;
    overflow: hidden;
    position: relative;
  }

  &-title {
    font-size: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;

    .title-text {
      user-select: none;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      width: 85%;

      .title-text-icon {
        width: 14px;
        margin-right: 6px;
        vertical-align: text-bottom;
      }
    }
  }

  &-content {
    padding: 0px 10px;
    height: calc(100% - 74px);
    font-size: 12px;

    .content-log {
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
      line-height: 1.5;
      padding: 2px 0px;
    }
  }

  &-footer {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: absolute;
    bottom: 10px;
    font-size: 12px;
    overflow: hidden;

    .stop-button {
      width: 42px;
      height: 17px;
      line-height: 17px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: space-between;
    }
  }
}
</style>
