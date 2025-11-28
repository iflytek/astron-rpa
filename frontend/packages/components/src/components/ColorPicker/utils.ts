// ColorPicker 工具函数

export interface RGB {
  r: number
  g: number
  b: number
}

export interface HSV {
  h: number
  s: number
  v: number
}

export type ColorInput = string | RGB | [number, number, number]

// rgb转hex
export function rgb2hex({ r, g, b }: RGB, toUpper = false): string {
  const toHex = (val: number) => (`0${Math.round(val).toString(16)}`).slice(-2)
  const color = `#${toHex(r)}${toHex(g)}${toHex(b)}`
  return toUpper ? color.toUpperCase() : color
}

// 创建线性渐变
export function createColorLinearGradient(
  direction: 'l' | 'p',
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  color1: string,
  color2: string,
): void {
  // l horizontal p vertical
  const isL = direction === 'l'
  const gradient = ctx.createLinearGradient(0, 0, isL ? width : 0, isL ? 0 : height)
  gradient.addColorStop(0.01, color1)
  gradient.addColorStop(0.99, color2)
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, width, height)
}

// hex转rgb
export function hex2rgb(hex: string): RGB {
  let hexValue = hex.slice(1)
  if (hexValue.length === 3) {
    hexValue = `${hexValue[0]}${hexValue[0]}${hexValue[1]}${hexValue[1]}${hexValue[2]}${hexValue[2]}`
  }
  const toInt = (val: string) => Number.parseInt(val, 16) || 0
  return {
    r: toInt(hexValue.slice(0, 2)),
    g: toInt(hexValue.slice(2, 4)),
    b: toInt(hexValue.slice(4, 6)),
  }
}

// rgb转hsv
export function rgb2hsv({ r, g, b }: RGB): HSV {
  const rNorm = r / 255
  const gNorm = g / 255
  const bNorm = b / 255
  const max = Math.max(rNorm, gNorm, bNorm)
  const min = Math.min(rNorm, gNorm, bNorm)
  const delta = max - min

  let h = 0
  if (max !== min) {
    if (max === rNorm) {
      h = (gNorm >= bNorm ? 0 : 360) + (60 * (gNorm - bNorm)) / delta
    }
    else if (max === gNorm) {
      h = 120 + (60 * (bNorm - rNorm)) / delta
    }
    else {
      h = 240 + (60 * (rNorm - gNorm)) / delta
    }
  }

  return {
    h: Math.floor(h),
    s: Number.parseFloat((max === 0 ? 0 : 1 - min / max).toFixed(2)),
    v: Number.parseFloat(max.toFixed(2)),
  }
}

// 验证输入的hex是否合法
export function isHex(str: string) {
  return /^#([0-9a-f]{6}|[0-9a-f]{3})$/i.test(str)
}

// 验证输入的rgb是否合法
export function isRgb(str: string) {
  const regex = /^(\d{1,3}),\s?(\d{1,3}),\s?(\d{1,3})$/ // 匹配rgb格式的正则表达式
  const match = str.match(regex) // 使用match方法进行匹配
  if (match) {
    // 如果匹配成功
    const r = Number.parseInt(match[1]) // 获取红色值
    const g = Number.parseInt(match[2]) // 获取绿色值
    const b = Number.parseInt(match[3]) // 获取蓝色值
    if (r >= 0 && r <= 255 && g >= 0 && g <= 255 && b >= 0 && b <= 255) {
      // 判断RGB值是否在合法范围内
      return true // 如果合法，返回true
    }
  }
  return false // 如果不合法，返回false
}

// 渲染面板颜色
export function renderSaturationColor(color: string, canvas: HTMLCanvasElement) {
  const height = canvas.height
  const width = canvas.width
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  ctx.fillStyle = color
  ctx.fillRect(0, 0, width, height)
  createColorLinearGradient('l', ctx, width, height, '#FFFFFF', 'rgba(255,255,255,0)')
  createColorLinearGradient('p', ctx, width, height, 'rgba(0,0,0,0)', '#000000')
}

// 渲染调色器颜色
export function renderBarColor(canvas: HTMLCanvasElement) {
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  const width = canvas.width
  const height = canvas.height
  const gradient = ctx.createLinearGradient(0, 0, 0, height)
  gradient.addColorStop(0, '#FF0000') // red
  gradient.addColorStop(0.17 * 1, '#FF00FF') // purple
  gradient.addColorStop(0.17 * 2, '#0000FF') // blue
  gradient.addColorStop(0.17 * 3, '#00FFFF') // green
  gradient.addColorStop(0.17 * 4, '#00FF00') // green
  gradient.addColorStop(0.17 * 5, '#FFFF00') // yellow
  gradient.addColorStop(1, '#FF0000') // red
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, width, height)
}

// 获取颜色面板canvas上的颜色
export function getColorOnCanvas(canvas: HTMLCanvasElement, e: MouseEvent) {
  const height = canvas.height
  const width = canvas.width
  const x = Math.max(0, Math.min(e.offsetX, width))
  const y = Math.max(0, Math.min(e.offsetY, height))
  const pointPosition = {
    top: `${y - 5}px`,
    left: `${x - 5}px`,
  }
  const ctx = canvas.getContext('2d')
  if (!ctx) {
    return { pointPosition, imageData: { data: new Uint8ClampedArray([0, 0, 0, 255]) } }
  }
  const imageData = ctx.getImageData(Math.max(x - 5, 0), Math.max(y - 5, 0), 1, 1)
  return {
    pointPosition,
    imageData,
  }
}

// 获取rgb颜色
export function getRgbColor(color: ColorInput): RGB {
  if (Array.isArray(color)) {
    return { r: color[0], g: color[1], b: color[2] }
  }
  if (typeof color === 'object' && 'r' in color && 'g' in color && 'b' in color) {
    return color
  }
  if (typeof color === 'string') {
    if (color.includes('#')) {
      return hex2rgb(color)
    }
    if (color.includes(',')) {
      const [r, g, b] = color.split(',').map(v => Number.parseInt(v.trim(), 10))
      return { r, g, b }
    }
  }
  return { r: 0, g: 0, b: 0 }
}


