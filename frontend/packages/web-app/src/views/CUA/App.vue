<script lang="ts" setup>
import { BorderMotion } from "@rpa/components";
import { useToggle } from "@vueuse/core";
import { onMounted, onUnmounted, ref } from "vue";

import { cuaChatStream } from "@/api/common";
import ConfigProvider from "@/components/ConfigProvider/index.vue";
import ChainOfThought from "@/components/ChainOfThought/ChainOfThought.vue";
import type { StreamContext, Step } from "@/components/ChainOfThought/utils";
import { createStep, processSseMessage } from "@/components/ChainOfThought/utils";
import { windowManager } from '@/platform'
import { WINDOW_NAME } from '@/constants'

import Header from "./Header.vue";

const [isExpanded, toggleExpanded] = useToggle(false);

const steps = ref<Step[]>([]);
const isStreaming = ref(false);
let abortController: AbortController | null = null;

async function markAllComplete() {
  steps.value.forEach((s) => {
    if (s.status !== "complete") s.status = "complete";
  });

  await windowManager.emitTo({
    from: WINDOW_NAME.CUA,
    target: WINDOW_NAME.MAIN,
    type: 'complete',
    data: JSON.stringify(steps.value),
  })
  windowManager.showWindow(WINDOW_NAME.MAIN)
  windowManager.closeWindow()
}

function startRequest(userMessage: string) {
  if (isStreaming.value) return;
  isStreaming.value = true;
  steps.value = [];

  abortController = new AbortController();

  const context: StreamContext = {
    steps: steps.value,
    partialToolCalls: {},
    currentTextStepId: null,
  };

  cuaChatStream(
    userMessage,
    (data) => {
      if (processSseMessage(data, context)) {
        markAllComplete();
        isStreaming.value = false;
      }
    },
    (err) => {
      if (err.name !== "AbortError") {
        const errorStep = createStep(
          "text",
          `流式响应出错: ${err?.message ?? String(err)}`,
        );
        errorStep.status = "complete";
        steps.value.push(errorStep);
      }
      isStreaming.value = false;
    },
    () => {
      markAllComplete();
      isStreaming.value = false;
    },
    abortController.signal,
  );
}

function handlePause() {
  if (abortController) {
    abortController.abort();
    isStreaming.value = false;
    markAllComplete();
  }
}

onMounted(() => {
  // 初始化信息
  const targetInfo = new URL(location.href).searchParams
  // 文件路径
  const message = targetInfo.get('message') || ''
  message && startRequest(message);
});

onUnmounted(() => {
  abortController?.abort();
});
</script>

<template>
  <ConfigProvider>
    <div class="cua-container">
      <div class="motion-layer">
        <BorderMotion />
      </div>

      <div
        class="panel-layer"
        :class="
          isExpanded
            ? 'items-center justify-center'
            : 'items-end justify-end p-6'
        "
      >
        <div
          class="cua-content-container border-border border-[1px] bg-white"
          :class="
            isExpanded
              ? 'w-[840px] h-[640px] rounded-3xl p-6'
              : 'w-[275px] rounded-2xl p-3 gap-2'
          "
        >
          <Header
            :is-streaming="isStreaming"
            :is-expanded="isExpanded"
            @toggleExpanded="toggleExpanded"
            @pause="handlePause"
          />
          <ChainOfThought
            v-if="isExpanded"
            :steps="steps"
            :is-streaming="isStreaming"
            class="mt-6 h-[460px]"
          />
        </div>
      </div>
    </div>
  </ConfigProvider>
</template>

<style scoped>
.cua-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.motion-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.panel-layer {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  pointer-events: none;
  z-index: 1;
}

.panel-layer > * {
  pointer-events: auto;
}

.cua-content-container {
  box-shadow:
    0 12px 16px -4px rgba(10, 13, 18, 0.08),
    0 4px 6px -2px rgba(10, 13, 18, 0.03);
}
</style>
