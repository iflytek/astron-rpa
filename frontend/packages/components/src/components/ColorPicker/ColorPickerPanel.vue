<script setup lang="ts">
import { message } from 'ant-design-vue'
import { computed, nextTick, onMounted, reactive, ref, useTemplateRef, watch } from 'vue'
import type { CSSProperties } from 'vue'

import type { RGB } from './utils'
import {
  getColorOnCanvas,
  getRgbColor,
  isHex,
  isRgb,
  renderBarColor,
  renderSaturationColor,
  rgb2hex,
  rgb2hsv,
} from './utils'

// 常量定义
const CANVAS_SATURATION_WIDTH = 150
const CANVAS_SATURATION_HEIGHT = 80
const CANVAS_BAR_WIDTH = 12
const CANVAS_BAR_HEIGHT = 80
const SLIDE_OFFSET = 5

interface ColorPickerPanelProps {
  defaultColors: string[]
  style?: CSSProperties
  class?: string
  // 是否在操作后自动关闭（用于 popover 场景）
  autoClose?: boolean
}

interface ColorPickerPanelEmits {
  (e: 'change', value: string): void
  (e: 'confirm', value: string): void
  (e: 'close'): void
}

const modelValue = defineModel<string>({ default: '' })
const props = defineProps<ColorPickerPanelProps>()
const emit = defineEmits<ColorPickerPanelEmits>()

const canvasSaturationRef = useTemplateRef<HTMLCanvasElement>('canvasSaturationRef')
const canvasBarRef = useTemplateRef<HTMLCanvasElement>('canvasBarRef')

// 是否正在更新颜色（用于避免 watch 循环）
const isUpdating = ref(false)

const position = reactive({
  pointPosition: { top: '0px', left: '0px' },
  slideBarStyle: { top: '0px' } as CSSProperties,
})

const attr = reactive({
  modelRgb: '',
  modelHex: '',
  r: 0,
  g: 0,
  b: 0,
  h: 0,
  s: 0,
  v: 0,
})

const rgbString = computed(() => `rgb(${attr.r}, ${attr.g}, ${attr.b})`)

// 更新颜色值（只更新内部状态，不触发 change 事件）
function updateColor(hex: string) {
  if (isUpdating.value) return
  isUpdating.value = true
  attr.modelHex = hex
  nextTick(() => {
    isUpdating.value = false
  })
}

// 颜色面板点击
function selectSaturation(e: MouseEvent) {
  const canvas = canvasSaturationRef.value
  if (!canvas) return
  const { pointPosition, imageData } = getColorOnCanvas(canvas, e)
  position.pointPosition = pointPosition
  const [r, g, b] = Array.from(imageData.data.slice(0, 3))
  setRGBHSV([r, g, b])
  const hex = rgb2hex({ r: attr.r, g: attr.g, b: attr.b }, true)
  updateColor(hex)
}

// 颜色条选中
function selectBar(e: MouseEvent) {
  const canvas = canvasBarRef.value
  if (!canvas) return
  const target = e.target as HTMLCanvasElement
  const ctx = target.getContext('2d')
  if (!ctx) return

  const { top: barTop, height } = canvas.getBoundingClientRect()

  const handleMouseMove = (moveEvent: MouseEvent) => {
    const y = Math.max(0, Math.min(moveEvent.clientY - barTop, height))
    position.slideBarStyle = {
      top: `${y - 2}px`,
    }
    // 先获取颜色条上的颜色在颜色面板上进行渲染
    const imgData = ctx.getImageData(0, Math.min(y, height - 1), 1, 1)
    const [r, g, b] = imgData.data
    const saturationCanvas = canvasSaturationRef.value
    if (saturationCanvas) {
      renderSaturationColor(`rgb(${r},${g},${b})`, saturationCanvas)
    }
    // 再根据颜色面板上选中的点的颜色，来修改输入框的值
    nextTick(() => {
      const saturationCanvas = canvasSaturationRef.value
      if (!saturationCanvas) return
      const saturationCtx = saturationCanvas.getContext('2d')
      if (!saturationCtx) return
      const pointX = Number.parseFloat(position.pointPosition.left) || 0
      const pointY = Number.parseFloat(position.pointPosition.top) || 0
      const pointRgb = saturationCtx.getImageData(
        Math.max(0, pointX),
        Math.max(0, pointY),
        1,
        1,
      )
      const [r, g, b] = Array.from(pointRgb.data.slice(0, 3))
      setRGBHSV([r, g, b])
      const hex = rgb2hex({ r: attr.r, g: attr.g, b: attr.b }, true)
      updateColor(hex)
    })
  }

  handleMouseMove(e)

  const handleMouseUp = () => {
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

// 默认颜色选择区选择颜色
function selectColor(color: string) {
  setRGBHSV(color)
  attr.modelRgb = rgbString.value.substring(4, rgbString.value.length - 1)
  const hex = rgb2hex({ r: attr.r, g: attr.g, b: attr.b }, true)
  attr.modelHex = hex

  const saturationCanvas = canvasSaturationRef.value
  if (saturationCanvas) {
    renderSaturationColor(rgbString.value, saturationCanvas)
  }

  position.pointPosition = {
    left: `${Math.max(attr.s * CANVAS_SATURATION_WIDTH - SLIDE_OFFSET, 0)}px`,
    top: `${Math.max((1 - attr.v) * CANVAS_SATURATION_HEIGHT - SLIDE_OFFSET, 0)}px`,
  }
  renderSlide()
  updateColor(hex)
}

// 调色卡的位置
function renderSlide() {
  position.slideBarStyle = {
    top: `${(1 - attr.h / 360) * (CANVAS_BAR_HEIGHT - 4)}px`,
  }
}

// hex输入框失去焦点
function inputHex() {
  if (isHex(attr.modelHex)) {
    selectColor(attr.modelHex)
  }
  else {
    message.error('请输入3位或者6位合法十六进制值')
  }
}

function inputRgb() {
  if (isRgb(attr.modelRgb)) {
    const [r, g, b] = attr.modelRgb.split(',').map(v => Number.parseInt(v.trim(), 10))
    const hex = rgb2hex({ r, g, b }, true)
    attr.modelHex = hex
    selectColor(attr.modelHex)
  }
  else {
    message.error('请输入合法的rgb数值')
  }
}

// color可能是 #fff 也可能是 123,21,11  这两种格式
function setRGBHSV(color: string | RGB | [number, number, number], initHex = false) {
  const rgb = getRgbColor(color)
  const hsv = rgb2hsv(rgb)
  attr.r = rgb.r
  attr.g = rgb.g
  attr.b = rgb.b
  attr.h = hsv.h
  attr.s = hsv.s
  attr.v = hsv.v
  if (initHex) {
    attr.modelHex = rgb2hex(rgb, true)
  }
  attr.modelRgb = rgbString.value.substring(4, rgbString.value.length - 1)
}

function clearColor() {
  // 清空时设置为黑色
  const blackHex = '#000000'
  setRGBHSV(blackHex)
  attr.modelHex = blackHex
  attr.modelRgb = '0, 0, 0'
  
  const saturationCanvas = canvasSaturationRef.value
  if (saturationCanvas) {
    renderSaturationColor(rgbString.value, saturationCanvas)
  }
  
  position.pointPosition = {
    left: `${Math.max(attr.s * CANVAS_SATURATION_WIDTH - SLIDE_OFFSET, 0)}px`,
    top: `${Math.max((1 - attr.v) * CANVAS_SATURATION_HEIGHT - SLIDE_OFFSET, 0)}px`,
  }
  renderSlide()
  updateColor(blackHex)
}

// 确认选择的颜色
function changeColor() {
  if (!isHex(attr.modelHex) || !isRgb(attr.modelRgb))
    return

  emit('change', attr.modelHex)
  emit('confirm', attr.modelHex)
  // 确认后关闭 popover
  if (props.autoClose) {
    emit('close')
  }
}

// 初始化颜色
function initColor(color?: string) {
  const colorToInit = color || modelValue.value
  if (colorToInit) {
    selectColor(colorToInit)
  }
}

// 渲染颜色条
function renderColorBar() {
  nextTick(() => {
    const barCanvas = canvasBarRef.value
    if (barCanvas) {
      renderBarColor(barCanvas)
    }
  })
}

onMounted(() => {
  renderColorBar()
  // 延迟初始化颜色，确保 canvas 已渲染
  nextTick(() => {
    initColor()
  })
})

// 监听外部传入的 modelValue 变化
watch(modelValue, (newVal) => {
  if (isUpdating.value) return
  if (newVal && newVal !== attr.modelHex) {
    initColor(newVal)
  }
  else if (!newVal && attr.modelHex) {
    // 如果外部清空，设置为黑色
    clearColor()
  }
})

defineExpose({
  canvasSaturationRef,
  canvasBarRef,
  renderColorBar,
})
</script>

<template>
  <div class="color-picker" :style="style" :class="class">
    <div class="color-panel">
      <ul class="colors color-box">
        <li
          v-for="item in defaultColors"
          :key="item"
          class="item"
          :style="{ background: item }"
          @click="selectColor(item)"
        />
      </ul>
      <div class="color-set">
        <!-- 颜色面板 -->
        <div class="saturation" @mousedown.prevent.stop="selectSaturation">
          <canvas
            ref="canvasSaturationRef"
            :width="CANVAS_SATURATION_WIDTH"
            :height="CANVAS_SATURATION_HEIGHT"
          />
          <div :style="position.pointPosition" class="slide" />
        </div>
        <!-- 颜色卡条 -->
        <div class="bar" @mousedown.prevent.stop="selectBar">
          <canvas ref="canvasBarRef" :width="CANVAS_BAR_WIDTH" :height="CANVAS_BAR_HEIGHT" />
          <div :style="position.slideBarStyle" class="slide" />
        </div>
      </div>
    </div>
    <!-- 颜色预览和颜色输入 -->
    <div class="color-view">
      <!-- 颜色预览区 -->
      <div :style="{ background: rgbString }" class="color-show" />
      <!-- 颜色输入区 -->
      <div class="input">
        <div class="color-type">
          <span class="name"> HEX </span>
          <input
            v-model="attr.modelHex"
            class="value"
            @blur="inputHex"
          >
        </div>
        <div class="color-type">
          <span class="name"> RGB </span>
          <input
            v-model="attr.modelRgb"
            class="value"
            @blur="inputRgb"
          >
        </div>
      </div>
    </div>
    <!-- 默认颜色列表选择区 -->
    <div class="btn border-border border-t">
      <button class="clear-btn" @click="() => clearColor()">
        清空
      </button>
      <button class="confirm-btn" @click="changeColor">
        确认
      </button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.color-picker {
  width: 275px;

  canvas {
    vertical-align: top;
  }

  .color-set {
    display: flex;
    margin-left: 5px;
  }

  .color-show {
    height: 56px;
    width: 100px;
    margin: 8px auto;
    display: flex;
  }
}

.color-panel {
  display: flex;

  .color-box {
    width: 100px;
  }
}

.color-view {
  display: flex;
}

.input {
  flex: 1;
  margin-left: 8px;
}

// 颜色面板
.saturation {
  position: relative;
  cursor: pointer;

  .slide {
    position: absolute;
    left: calc(100% - 4px);
    top: 0;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    border: 1px solid #fff;
    box-shadow: 0 0 1px 1px rgba(0, 0, 0, 0.3);
    pointer-events: none;
    transform: translate(-50%, -50%);
  }
}

// 颜色调节条
.bar {
  position: relative;
  margin-left: 8px;
  cursor: pointer;

  .slide {
    box-sizing: border-box;
    position: absolute;
    left: 0;
    width: 100%;
    height: 4px;
    background: #fff;
    border: 1px solid #f0f0f0;
    box-shadow: 0 0 2px rgba(0, 0, 0, 0.6);
    pointer-events: none;
    border-radius: 1px;
  }
}

.color-type {
  display: flex;
  margin: 8px auto;
  font-size: 12px;

  .name {
    width: 32px;
    height: 24px;
    float: left;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #a0acc0;
  }

  .value {
    display: block;
    box-sizing: border-box;
    flex: 1;
    height: 24px;
    width: 100px;
    padding: 0 8px;
    border: 1px solid #42516c;
    color: #eff0f4;
    background: #2e3850;
    caret-color: #49a4ff;

    &:focus-visible {
      outline: 1px solid rgba(18, 107, 190, 0.5);
    }
  }
}

// 默认颜色
.colors {
  display: flex;
  flex-wrap: wrap;
  padding: 0;
  margin: 0;

  .item {
    flex-basis: calc(20% - 4px);
    margin: 2px;
    width: 16px;
    height: 16px;
    border-radius: 1px;
    box-sizing: border-box;
    vertical-align: top;
    display: inline-block;
    transition: all 0.1s;
    cursor: pointer;

    &:hover {
      transform: scale(1.2);
    }
  }
}

.btn {
  text-align: right;
  padding-top: 8px;

  button {
    margin-left: 8px;
    width: 52px;
    height: 20px;
    font-size: 12px;
    font-weight: 400;
    border-radius: 6px;
    border: none;
  }

  .confirm-btn {
    color: #fff;
    background-color: var(--headerFontColorHover);

    &:hover {
      background-color: #7a93ff;
    }
  }

  .clear-btn {
    border: 1px solid #d9d9d9;
    background-color: #fff;
    color: #000000;
  }
}
</style>
