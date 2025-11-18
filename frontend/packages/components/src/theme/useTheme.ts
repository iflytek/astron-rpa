import type { BasicColorMode } from '@vueuse/core'
import { createGlobalState, useColorMode } from '@vueuse/core'
import { computed } from 'vue'

export type { BasicColorMode } from '@vueuse/core'

export const useTheme = createGlobalState(() => {
  const colorMode = useColorMode({ emitAuto: true, initialValue: 'light' })

  const colorTheme = computed<BasicColorMode>(() => {
    return colorMode.value === 'auto' ? colorMode.system.value : colorMode.value
  })

  const isDark = computed(() => colorTheme.value === 'dark')

  const setColorMode = (theme: BasicColorMode) => {
    colorMode.value = theme
  }

  return { colorMode: colorMode.store, colorTheme, isDark, setColorMode }
})
