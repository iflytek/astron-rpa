// ColorPicker.ts
// rgb转hex
export function rgb2hex({ r, g, b }: any, toUpper: boolean) {
  const change = (val: any) => (`0${Number(val).toString(16)}`).slice(-2)
  const color = `#${change(r)}${change(g)}${change(b)}`
  return toUpper ? color.toUpperCase() : color
}

// 创建线性渐变
export function createColorLinearGradient(
  direction: any,
  ctx: any,
  width: any,
  height: any,
  color1: any,
  color2: any,
) {
  // l horizontal p vertical
  const isL = direction === 'l'
  const gradient = ctx.createLinearGradient(0, 0, isL ? width : 0, isL ? 0 : height)
  gradient.addColorStop(0.01, color1)
  gradient.addColorStop(0.99, color2)
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, width, height)
}

// hex转rgb
export function hex2rgb(hex: any) {
  hex = hex.slice(1)
  if (hex.length === 3) {
    hex = `${hex[0]}${hex[0]}${hex[1]}${hex[1]}${hex[2]}${hex[2]}`
  }
  const change = (val: any) => Number.parseInt(val, 16) || 0
  return {
    r: change(hex.slice(0, 2)),
    g: change(hex.slice(2, 4)),
    b: change(hex.slice(4, 6)),
  }
}

// rgb转hsv
export function rgb2hsv({ r, g, b }: any) {
  r = r / 255
  g = g / 255
  b = b / 255
  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  const delta = max - min
  let h = 0
  if (max === min) {
    h = 0
  }
  else if (max === r) {
    if (g >= b) {
      h = (60 * (g - b)) / delta
    }
    else {
      h = (60 * (g - b)) / delta + 360
    }
  }
  else if (max === g) {
    h = (60 * (b - r)) / delta + 120
  }
  else if (max === b) {
    h = (60 * (r - g)) / delta + 240
  }
  h = Math.floor(h)
  const s = Number.parseFloat((max === 0 ? 0 : 1 - min / max).toFixed(2))
  const v = Number.parseFloat(max.toFixed(2))
  return { h, s, v }
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
