import { ErrorMessage } from './constant'
import { Tabs } from './tab'

export async function frameFind(frameXpath: string) {
  const framePath = frameXpath.split('/$iframe$')
  const tab = await Tabs.getActiveTab()
  if (!tab) {
    throw new Error(ErrorMessage.ACTIVE_TAB_ERROR)
  }
  let frameId = 0
  for (let i = 0; i < framePath.length; i++) {
    const res = await locatorFrameId(tab.id!, frameId, framePath[i])
    if (res && res.frameId != null) {
      frameId = res.frameId
      continue
    }
    else {
      return null
    }
  }
  return frameId
}

async function locatorFrameId(tabId: number, curFrameId = 0, curFrameXpath: string) {
  try {
    const res = await Tabs.executeFuncOnFrame(tabId, curFrameId, (arg) => {
      // @ts-expect-error window in content_script
      return window.handleSync({
        key: 'findIframeId',
        data: arg,
      })
    }, [curFrameXpath])
    if (res) {
      return res as { frameId: number | null }
    }
  }
  catch {
    return null
  }
}
