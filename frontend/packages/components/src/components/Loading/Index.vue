<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { useTranslation } from 'i18next-vue'
import { Button } from 'ant-design-vue'
import { useTimeoutFn } from '@vueuse/core'

import { LoadingDots } from '../LoadingDots'

export interface LoadingProps {
  isLoading: boolean
  text?: string
  immediate?: boolean
  timeout?: number // seconds
  exit?: boolean
  exitCallback?: () => void
}

const { t } = useTranslation()

// State
const visible = ref(false)
const tip = ref('')
const showExit = ref(false)
const exitCb = ref<(() => void) | undefined>()
const autoCloseDelay = ref(200000)

// Timers
const { start: startHideDelay, stop: stopHideDelay } = useTimeoutFn(() => {
  resetState()
}, 500, { immediate: false })

const { start: startAutoClose, stop: stopAutoClose } = useTimeoutFn(() => {
  resetState()
}, autoCloseDelay, { immediate: false })

function resetState() {
  visible.value = false
  tip.value = ''
  showExit.value = false
  exitCb.value = undefined
  stopAutoClose()
  stopHideDelay()
}

function setLoading(props: LoadingProps) {
  const {
    isLoading,
    text = '',
    immediate = false,
    timeout = 200,
    exit = false,
    exitCallback
  } = props

  // Immediate update overrides everything
  if (immediate) {
    stopHideDelay()
    stopAutoClose()
    
    visible.value = isLoading
    if (isLoading) {
      tip.value = text || t('loading')
      showExit.value = exit
      exitCb.value = exitCallback
    }
    return
  }

  if (isLoading) {
    // Show loading
    stopHideDelay() // Cancel pending hide
    
    visible.value = true
    tip.value = text || t('loading')
    showExit.value = exit
    exitCb.value = exitCallback

    // Setup auto-close
    if (timeout > 0) {
      autoCloseDelay.value = timeout * 1000
      startAutoClose()
    }
  } else {
    // Hide loading with delay (debounce)
    if (visible.value) {
      startHideDelay()
    }
    stopAutoClose()
  }
}

function handleExit() {
  const callback = exitCb.value
  resetState()
  nextTick(() => {
    callback?.()
  })
}

defineExpose({
  isLoading: setLoading,
  setLoading,
  exitLoading: handleExit,
})
</script>

<template>
  <Transition name="loading-fade">
    <div v-show="visible" class="loading-mask">
      <div class="loading-box p-2 flex flex-col items-center justify-center">
        <LoadingDots />
        <div v-if="tip" class="text-center mt-2">
          {{ tip }}...
        </div>
        <div v-if="showExit" class="loading-exit">
          <Button size="small" type="link" @click="handleExit">
            {{ $t("quit") }}
          </Button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style lang="scss" scoped>
.loading-mask {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;

  .loading-box {
    width: fit-content;
    min-width: 88px;
    min-height: 88px;
    background: var(--color-bg-elevated, #fff);
    border-radius: 8px;
    box-shadow: 0 6px 16px 0 rgba(0, 0, 0, 0.08), 0 3px 6px -4px rgba(0, 0, 0, 0.12), 0 9px 28px 8px rgba(0, 0, 0, 0.05);
  }

  .loading-exit {
    width: 100%;
    margin: 10px auto 0;
    padding-top: 8px;
    border-top: 1px solid var(--color-border, #ccc);
    display: flex;
    justify-content: center;
    align-items: center;

    .ant-btn-link {
      font-size: 12px;
    }
  }
}

// Vue Transition classes
.loading-fade-enter-active,
.loading-fade-leave-active {
  transition: opacity 0.3s linear;
}

.loading-fade-enter-from,
.loading-fade-leave-to {
  opacity: 0;
}
</style>
