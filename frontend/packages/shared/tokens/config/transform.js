import { TinyColor } from '@ctrl/tinycolor'

function getRgbaValue(token, isDark) {
  const lightValue = token?.$value || token?.value
  const value = isDark ? token.dark || lightValue : lightValue
  const { r, g, b, a } = new TinyColor(value).toRgb()
  const hasAlpha = a !== undefined
  return `${r} ${g} ${b}${hasAlpha ? ` / ${a}` : ''}`
}

export function rgbChannels(token) {
  return getRgbaValue(token, false)
}

export function rgbChannelsDark(token) {
  return getRgbaValue(token, true)
}
