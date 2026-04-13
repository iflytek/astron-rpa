<!-- @format -->

<script lang="ts" setup>
import { ref } from 'vue'
import ConfigProvider from '@/components/ConfigProvider/index.vue'
import { useHighlight } from './hooks/useHighlight'

const tooltipRef = ref<HTMLElement | null>(null)
const {
  dpr,
  highlightRect,
  mousePos,
  appName,
  tagName,
  tooltipVisible,
  tooltipPos,
  tagPosition,
  shortcuts,
} = useHighlight()
</script>

<template>
  <ConfigProvider>
    <div class="highlight-overlay">
      <div
        v-if="highlightRect.width > 0"
        class="highlight-box"
        :style="{
        left: (highlightRect.x / dpr) + 'px',
        top: (highlightRect.y / dpr) + 'px',
        width: highlightRect.width + 'px',
        height: highlightRect.height + 'px'
      }">
        <span :class="`highlight-tag ${tagPosition === 'top' ? 'highlight-tag-top' : 'highlight-tag-bottom'}`">
          {{ tagName }}
        </span>
      </div>
      <div v-if="tooltipVisible" ref="tooltipRef" :class="`tooltip bg-bg-elevated ${tooltipPos === 'leftTop' ? 'tooltip-left-top' : 'tooltip-right-bottom'}`">
        <!-- <div class="tooltip-item font-bold">{{ modeTitle }}</div> -->
        <div class="tooltip-item font-bold" v-for="(sc, i) in shortcuts" :key="i">
          <span class="short-title">{{ sc.title }}</span>
          <span class="short-keys">{{ sc.keys }}</span>
        </div>
        <div class="tooltip-item">
          <span class="short-title">位置</span>
          <span class="short-">{{ mousePos.x }}, {{ mousePos.y }}</span>
        </div>
        <div class="tooltip-item" v-if="appName">
          <span class="short-title">应用</span>
          <span class="short-">{{ appName }}</span>
        </div>
      </div>
    </div>
  </ConfigProvider>
</template>

<style lang="scss">
.highlight-overlay {
  width: 100vw;
  height: 100%;
  position: fixed;
  top: 0;
  left: 0;
  pointer-events: none;
  background: transparent;
}

.highlight-box {
  position: absolute;
  border: 2px solid var(--color-primary);
  background: #716fff28;
  pointer-events: none;
  transition: all 0.1s ease-out;
   border-radius: 4px;
  .highlight-tag{
    position: absolute;
    background: #1c1c1c;
    color: #fff;
    padding: 2px 6px;
    font-size: 12px;
    border-radius: 4px;
    white-space: nowrap;
    transition: all 0.3s ease-out;
    &-top {
      top: -26px;
      left: -2px;
    }
    &-bottom {
      bottom: -26px;
      left: -2px;
    }
  }
}

.tooltip {
  position: fixed;
  // background: var(--color-bg-elevated);
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.5;
  pointer-events: none;
  border: 1px var(--color-border) solid;
  &-left-top {
    top: 10px;
    left: 10px;
  }
  &-right-bottom {
    bottom: 60px;
    right: 10px;
  }

  .tooltip-item {
    margin-bottom: 4px;
    display: flex;
    align-items: center;
     &:last-child {
      margin-bottom: 0;
     }
     .short-title {
      margin-right: 6px;
      width: 58px;
      display: inline-block;
     }
    .short-keys {
        background: var(--color-border-secondary);
        padding: 4px;
        border-radius: 3px;
        font-size: 12px;
        border: 1px solid var(--color-border);
        line-height: 1;
      }
  }
}
</style>
