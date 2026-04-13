import { computed } from 'vue'

export function usePlatform() {
  const userAgent = navigator.userAgent.toLowerCase()
  const platform = navigator.platform?.toLowerCase() || ''

  const isMac = computed(() => 
    /macintosh|mac os x/i.test(userAgent) || platform.startsWith('mac')
  )

  const isWindows = computed(() => 
    /windows|win32|win64/i.test(userAgent) || platform.startsWith('win')
  )

  const isLinux = computed(() => 
    /linux/i.test(userAgent) && !/android/i.test(userAgent)
  )

  const isAndroid = computed(() => 
    /android/i.test(userAgent)
  )

  const isIOS = computed(() => 
    /iphone|ipad|ipod/i.test(userAgent)
  )

  const osName = computed(() => {
    if (isMac.value) return 'Mac'
    if (isWindows.value) return 'Windows'
    if (isLinux.value) return 'Linux'
    if (isAndroid.value) return 'Android'
    if (isIOS.value) return 'iOS'
    return 'Unknown'
  })

  return {
    isMac,
    isWindows,
    isLinux,
    isAndroid,
    isIOS,
    osName
  }
}