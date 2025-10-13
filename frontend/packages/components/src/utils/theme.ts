import * as darkTokens from '@rpa/shared/tokens/dark'
import * as lightTokens from '@rpa/shared/tokens/light'
import type { ConfigProvider } from 'ant-design-vue'
import { lowerFirst } from 'lodash-es'

type ConfigProps = InstanceType<typeof ConfigProvider>['$props']

export type Theme = 'light' | 'dark'

export function getAntdvTheme(theme: Theme): ConfigProps['theme'] {
  const isLight = theme === 'light'
  const tokens = (isLight ? lightTokens : darkTokens) as Record<string, unknown>

  // 用 lodash 将 tokens 所有的 key 首字母转成小写
  const lowerTokens = Object.keys(tokens).reduce((acc, key) => {
    acc[lowerFirst(key)] = tokens[key]
    return acc
  }, {} as Record<string, unknown>)

  return {
    token: lowerTokens,
    components: {
      Input: {
        colorBgContainer: isLight ? '#f3f3f7' : 'rgba(255,255,255,0.08)',
        colorText: isLight ? 'rgba(0,0,0,0.65)' : 'rgba(255,255,255,0.65)',
        lineWidth: 0,
        colorPrimaryHover: 'transparent',
        colorBorder: 'transparent',
        controlOutlineWidth: 0,
        // controlOutline: 'none',
      },
      InputNumber: {
        colorBgContainer: isLight ? '#f3f3f7' : 'rgba(255,255,255,0.08)',
        lineWidth: 0,
      },
      // TextArea: {
      //   colorBgContainer: isLight ? '#f3f3f7' : 'rgba(255,255,255,0.08)',
      //   lineWidth: '0',
      // },
      Select: {
        colorBgContainer: isLight ? '#f3f3f7' : 'rgba(255,255,255,0.08)',
        lineWidth: 0,
        colorPrimaryHover: 'transparent',
        colorBorder: 'transparent',
        controlOutlineWidth: 0,
      },
      DatePicker: {
        colorBgContainer: isLight ? '#f3f3f7' : 'rgba(255,255,255,0.08)',
        lineWidth: 0,
        colorLink: tokens.colorPrimary as string,
      },
      Form: {
        colorTextHeading: isLight ? 'rgba(0,0,0,0.65)' : 'rgba(255,255,255,0.65)',
        fontSize: 12,
      },
      Segmented: {
        colorBgLayout: isLight ? '#f3f3f7' : 'rgba(255,255,255,0.04)',
        colorBgElevated: isLight ? '#ffffff' : 'rgba(255,255,255,0.12)',
      },
    },
  }
}
