<script lang="tsx">
import { CheckCircleFilled, ClockCircleOutlined, CloseCircleFilled, CloseOutlined, DoubleLeftOutlined, DoubleRightOutlined, IssuesCloseOutlined, LoadingOutlined, MinusOutlined } from '@ant-design/icons-vue'
import { invoke } from '@tauri-apps/api/tauri'
import { Tooltip } from 'ant-design-vue'
import { isEmpty } from 'lodash-es'

import { generateUUID } from '@/utils/common'

import { getUserSetting } from '@/api/setting'
import Socket from '@/api/ws'
import { windowManager } from '@/platform'

import { DEFAULT_STOPRUN_SHORTKEY } from './config'

const iconStatusMap = {
  current: <LoadingOutlined class="text-[rgba(0,0,0,0.85) ] dark:text-[#fff]" />,
  success: <CheckCircleFilled class="color-primary" />,
  error: <CloseCircleFilled class="color-error" />,
  error_skip: <IssuesCloseOutlined />,
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
    const targetInfo = new URL(location.href).searchParams
    this.createWs(targetInfo.get('ws'))
    this.setProjectName(targetInfo.get('title'))
    this.isSiderMinimized = targetInfo.get('mini') === '1'
    setTimeout(async () => {
      await invoke('render_ready')
    }, 1000)
  },
  methods: {
    createWs(url) {
      this.ws = new Socket('', {
        url,
        isReconnect: true,
        reconnectCount: 10,
        isHeart: true,
        heartTime: 30 * 1000,
      })
      this.ws.bindMessage((res) => { // 处理ws消息
        const result = JSON.parse(res)
        // console.log('result: ', result)
        const { data, channel } = result
        this.getLogData(data)

        // 执行结束、执行出错、执行器报错等异常退出时，关闭socket并重置状态
        if (['task_end', 'task_error'].includes(data.status) || channel === 'exit') {
          windowManager.closeWindow()
        }
      })
      this.ws.bindClose(() => {
        console.log('bindClose: ')
      })
    },

    setProjectName(name = '') {
      this.projectName = name || '执行日志'
    },
    // 开始计时
    startCount() {
      if (this.countTimer)
        clearInterval(this.countTimer)
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
          setTimeout(() => {
            clearInterval(this.countTimer)
          }, 1000)
        }
        if (line) {
          // 当前行
          this.currentLine = Math.max(this.currentLine, line)
        }
      }

      console.log('logItem+++++: ', logItem)
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
      if (this.isSiderMinimized) {
        await windowManager.minLogWindow(false)
      }
      else {
        await windowManager.minLogWindow(true)
      }
      this.isSiderMinimized = !this.isSiderMinimized
    },
    // 停止按钮
    clickStop() {
      // 发送停止请求后关闭窗口

      this.ws && this.ws.send({
        event_id: generateUUID(),
        event_time: new Date().getTime(),
        channel: 'flow',
        key: 'close', // 关键标识key
        data: {},
      })
      setTimeout(() => windowManager.closeWindow(), 500)
    },
    clickHide() {
      // 不停止，只关闭窗口
      windowManager.closeWindow()
    },
    clickMinimize() {
      windowManager.minimizeWindow()
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
      const hours = Math.floor(time / 3600)
      const minutes = Math.floor((time % 3600) / 60)
      const seconds = time % 60
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds
        .toString()
        .padStart(2, '0')}`
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
        return <div class="content-log !text-[rgba(0,0,0,0.85)] dark:!text-[rgba(255,255,255,0.85)]">正在进行初始化...</div>
      }

      return this.logData.map((item, index) => {
        return (
          <div class="content-log">
            {this.getIconState(item, index)}
            &nbsp;
            <span class="!text-[rgba(0,0,0,0.85)] dark:!text-[rgba(255,255,255,0.85)]">{item.msg_str}</span>
          </div>
        )
      })
    },
  },
  render() {
    return (
      <div class="logData bg-[#fff] dark:bg-[#1f1f1f]">
        <div class={this.isSiderMinimized ? 'logData-sider sider-min' : 'logData-sider'} onClick={this.siderMinimize}>
          {
            this.isSiderMinimized
              ? <DoubleLeftOutlined class="color-white" />
              : <DoubleRightOutlined class="color-white" />
          }
        </div>
        <div class={this.isSiderMinimized ? 'hide' : 'logData-container'} style={this.getProcessStyle()}>
          <div class="logData-title p-[10px]" data-tauri-drag-region>
            <div class="title-text flex items-center">
              <div class="w-[20px] h-[20px] bg-primary rounded-[2px] flex items-center justify-center mr-[10px]">
                <rpa-icon name="robot" class="w-[14px] h-[14px] text-[#fff]" />
              </div>
              <div class="h-[20px] leading-5 text-[14px] text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)] font-semibold">{this.projectName || '执行日志'}</div>
            </div>
            <div class="title-button">
              <MinusOutlined onClick={this.clickMinimize} class="text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)] no-drag mr-2" />
              <CloseOutlined onClick={this.clickHide} class="text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)] no-drag" />
            </div>
          </div>
          <div class="logData-content">{this.renderLogContent()}</div>
          <div class="logData-footer px-[10px]">
            <span>
              <ClockCircleOutlined class="text-[rgba(0,0,0,0.85) ] dark:text-[#fff] mr-[5px]" />
              <span class="!text-[rgba(0,0,0,0.85)] dark:!text-[rgba(255,255,255,0.85)]">{this.getCountTime(this.countTime)}</span>
            </span>
            <Tooltip
              placement="topLeft"
              class="tool-tip"
              title={this.$t('quitShortcut', { key: this.stopRunText })}
              overlayClassName="whitespace-nowrap"
            >
              <span class="stop-button text-[#ec483e] text-[14px]" onClick={this.clickStop}>
                <rpa-icon name="cancel" class="w-[14px] h-[14px] text-[#ec483e]" />
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

    .sider-icon {
      color: white;
    }
  }

  .sider-min {
    width: 34px;
  }

  &-container {
    flex: 1;
    overflow: hidden;
    position: relative;
  }

  .hide {
    display: none;
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
    .tool-tip {
      font-size: 14px;
    }
  }
}

.color-white {
  color: white;
}
.color-primary {
  color: $color-primary;
}
.color-error {
  color: $color-error;
}
.bg-primary {
  background-color: $color-primary;
}
</style>
