import { TinyColor } from '@ctrl/tinycolor'
import { theme } from 'ant-design-vue'

const { defaultSeed, defaultAlgorithm, darkAlgorithm } = theme

const white = '#FFFFFF'
const black = '#000000'
const colorPrimary = '#726FFF'
const darkColorPrimay = new TinyColor('#8482FE').setAlpha(0.9).toString()

const seeds = {
  ...defaultSeed,
  colorPrimary,
}

const defaultTokens = {
  ...defaultAlgorithm(seeds),
  colorPrimaryBg: 'rgba(215,215,255,0.40)',
  colorBgElevated: white,
  colorText: new TinyColor(black).setAlpha(0.85).toString(),
  colorLink: '#726FFF',
  colorLinkHover: '#9e99ff',
}
const darkTokens = {
  ...darkAlgorithm(seeds),
  colorPrimary: darkColorPrimay,
  colorPrimaryBg: '#383764',
  colorBgElevated: '#1d1d1d',
  colorText: white,
  colorLink: '#8482fe',
  colorLinkHover: '#908ce8',
}

const presetColors = [
  'blue',
  'purple',
  'cyan',
  'green',
  'magenta',
  'pink',
  'red',
  'orange',
  'yellow',
  'volcano',
  'geekblue',
  'lime',
  'gold',
]

// 从 1 到 10 的颜色梯度数组
const gradientInde = Array.from({ length: 10 }, (_, i) => i + 1)

const colorTokenNames = [
  ...presetColors.map(it => [it, ...gradientInde.map(index => `${it}-${index}`)]).flat(),
  'colorBgBase',
  'colorError',
  'colorInfo',
  'colorPrimary',
  'colorSuccess',
  'colorTextBase',
  'colorWarning',
  'colorBgContainer',
  'colorBgElevated',
  'colorBgLayout',
  'colorBgMask',
  'colorBgSpotlight',
  'colorBorder',
  'colorBorderSecondary',
  'colorErrorActive',
  'colorErrorBg',
  'colorErrorBgHover',
  'colorErrorBorder',
  'colorErrorBorderHover',
  'colorErrorHover',
  'colorErrorText',
  'colorErrorTextActive',
  'colorErrorTextHover',
  'colorFill',
  'colorFillQuaternary',
  'colorFillSecondary',
  'colorFillTertiary',
  'colorInfoActive',
  'colorInfoBg',
  'colorInfoBgHover',
  'colorInfoBorder',
  'colorInfoBorderHover',
  'colorInfoHover',
  'colorInfoText',
  'colorInfoTextActive',
  'colorInfoTextHover',
  'colorPrimaryActive',
  'colorPrimaryBg',
  'colorPrimaryBgHover',
  'colorPrimaryBorder',
  'colorPrimaryBorderHover',
  'colorPrimaryHover',
  'colorPrimaryText',
  'colorPrimaryTextActive',
  'colorPrimaryTextHover',
  'colorSuccessActive',
  'colorSuccessBg',
  'colorSuccessBgHover',
  'colorSuccessBorder',
  'colorSuccessBorderHover',
  'colorSuccessHover',
  'colorSuccessText',
  'colorSuccessTextActive',
  'colorSuccessTextHover',
  'colorText',
  'colorTextQuaternary',
  'colorTextSecondary',
  'colorTextTertiary',
  'colorWarningActive',
  'colorWarningBg',
  'colorWarningBgHover',
  'colorWarningBorder',
  'colorWarningBorderHover',
  'colorWarningHover',
  'colorWarningText',
  'colorWarningTextActive',
  'colorWarningTextHover',
  'colorWhite',
]

const tokens = Object.entries(defaultTokens).reduce((result, [key, value]) => {
  const isColor = colorTokenNames.includes(key)
  const isDifferent = isColor && darkTokens[key] !== value

  result[key] = {
    value,
    type: isColor ? 'color' : undefined,
    dark: isDifferent ? darkTokens[key] : undefined,
  }
  return result
}, {})

export default tokens
