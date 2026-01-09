<script setup lang="ts">
import { Button } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { nextTick, ref, unref } from 'vue'

interface LoadingProps {
  isLoading: boolean
  text?: string
  immediate?: boolean
  timeout?: number
  exit?: boolean
  exitCallback?: () => void
}

const { t } = useTranslation()
const loadingShow = ref(false)
const loadingText = ref('')
const loadingExit = ref(false)

const loadingHideTimer = ref()
const loadingTimer = ref()
const loadingExitCallback = ref()

function fn({
  isLoading,
  text = '',
  immediate,
  timeout = 200,
  exit = false,
  exitCallback,
}: LoadingProps) {
  if (!isLoading) {
    // false
    unref(loadingHideTimer) && clearTimeout(unref(loadingHideTimer))
    loadingHideTimer.value = setTimeout(() => {
      // 延迟500ms 关闭，兼容多个接口连续不断loading
      loadingShow.value = false
      loadingText.value = ''
      loadingHideTimer.value = undefined
    }, 500)
  }
  else {
    unref(loadingHideTimer) && clearTimeout(unref(loadingHideTimer)) // 清空定时器
    unref(loadingTimer) && clearTimeout(unref(loadingTimer)) // 清空定时器
    loadingTimer.value = setTimeout(() => {
      loadingShow.value = false
      loadingTimer.value = null
    }, timeout * 1000) // timeout 秒后自动关闭, 大工程加载超时时间过长
    loadingShow.value = true
    loadingText.value = text || t('loading')
    loadingExit.value = exit
    loadingExitCallback.value = exitCallback
  }
  if (immediate) {
    // 立即触发
    loadingShow.value = isLoading
    unref(loadingHideTimer) && clearTimeout(unref(loadingHideTimer))
    unref(loadingTimer) && clearTimeout(unref(loadingTimer)) // 清空定时器
  }
}

function exitLoading() {
  loadingShow.value = false
  loadingText.value = ''
  loadingExit.value = false
  loadingHideTimer.value = null
  loadingTimer.value = null
  nextTick(() => {
    typeof loadingExitCallback.value === 'function'
    && loadingExitCallback.value()
    loadingExitCallback.value = null
  })
}

function isLoading(params: LoadingProps) {
  fn(params)
}

defineExpose({
  isLoading,
})
</script>

<template>
  <div class="loading-mask bg-[#00000059] dark:bg-[#ffffff59]" :class="[loadingShow ? 'loading-show' : 'loading-hide']">
    <div class="loading-box">
      <div class="lb-spinner" />
      <div class="lb-info text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)]">
        {{ loadingText }}...
      </div>
      <div v-if="loadingExit" class="loading-exit">
        <Button size="small" type="link" @click="exitLoading">
          {{ $t("quit") }}
        </Button>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.loading-mask {
  position: fixed;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  z-index: 9999;
  display: none;
  align-items: center;
  justify-content: center;
  -webkit-animation: 0.3s fadeIn linear;
  animation: 0.3s fadeIn linear;
  user-select: none;

  .loading-box {
    width: fit-content;
    min-width: 120px;
    min-height: 68px;
    align-items: center;
    border-radius: 4px;
    padding-top: 8px;

    .lb-spinner {
      width: 50px;
      height: 50px;
      margin: 0 auto;
      border-radius: 50%;
      background-image: url('../../assets/imgs/loading.gif');
      background-size: 100% 100%;
    }

    .lb-info {
      text-align: center;
      font-size: 12px;
      margin-bottom: 8px;
      padding: 0 8px;
    }
  }

  .loading-exit {
    left: 50%;
    margin: 10px auto 0;
    border-top: 1px solid #ccc;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;

    .ant-btn-link {
      font-size: 12px;
    }
  }
}

.loading-show {
  display: flex;
}

.loading-hide {
  -webkit-animation: 0.4s fadeOut forwards;
  animation: 0.4s fadeOut forwards;
}

@keyframes spin {
  from {
    -webkit-transform: rotate(0deg);
    transform: rotate(0deg);
  }

  to {
    -webkit-transform: rotate(360deg);
    transform: rotate(360deg);
  }
}

@keyframes fadeIn {
  0% {
    opacity: 0;
  }

  100% {
    opacity: 1;
  }
}

@keyframes fadeOut {
  0% {
    display: flex;
    opacity: 1;
  }

  95% {
    display: flex;
    opacity: 0;
  }

  100% {
    display: none;
    opacity: 0;
  }
}
</style>
