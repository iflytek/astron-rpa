import { log } from '../3rd/log'
import { ErrorMessage, FRAME_ELEMENT_TAGS } from '../common/constant'
import { Utils } from '../common/utils'

import { Tabs } from './tab'

/**
 * Finds the target browser tab and frame based on the provided parameters.
 */
export async function findTabAndFrame(params: ElementParams) {
  const { isFrame, tabUrl } = params.data
  let tab = await Tabs.getActiveTab()
  if (!tab) {
    tab = await Tabs.activeTargetTabByTabUrl(tabUrl)
    if (!tab || !Utils.isSupportProtocal(tab.url)) {
      throw new Error(ErrorMessage.ACTIVE_TAB_ERROR)
    }
  }
  if (!isFrame) {
    return { tab, frameId: 0 }
  }
  else {
    const frames = await Tabs.getAllFrames(tab.id)
    const frameId = await frameFinder(tab, frames, params)
    return { tab, frameId, frames }
  }
}

async function frameFinder(tab: chrome.tabs.Tab, frames: FrameDetails[], params: ElementParams) {
  let iframeBuildXpath = ''
  const { url, iframeXpath, iframePathDirs, checkType } = params.data
  let targetFrame = null

  if (checkType === 'visualization' && iframePathDirs && iframePathDirs.length) {
    const frameLevels: ElementDirectory[][] = []
    let currentLevel: ElementDirectory[] = []
    for (let i = 0; i < iframePathDirs.length; i++) {
      const dir = iframePathDirs[i]
      const isFrameTag = FRAME_ELEMENT_TAGS.includes(dir.tag.toLowerCase())
      if (isFrameTag) {
        currentLevel.push(dir)
        frameLevels.push(currentLevel)
        currentLevel = []
      }
      else {
        currentLevel.push(dir)
      }
    }
    iframeBuildXpath = frameLevels
      .map(levelDirs => Utils.generateXPath(levelDirs))
      .join('/$iframe$')
    log.info('frameLevels: ', frameLevels, ' build iframe xpath: ', iframeBuildXpath)
  }
  else {
    iframeBuildXpath = iframeXpath
  }

  if (iframeBuildXpath) {
    targetFrame = findFrameByXpath(frames, iframeBuildXpath)
  }
  else {
    targetFrame = findFrameByUrl(frames, url)
  }

  if (targetFrame) {
    return targetFrame.frameId
  }
  else {
    // try to find frame by directly using the iframe xpath without comparing with frames
    let frameId = await frameFind(iframeBuildXpath)
    // try to find frame by element, if element is in current frame, return current frameId, else return null
    if (frameId === null) {
      frameId = await elementLocatorFrameId(tab.id, params.data)
    }
    return frameId
  }
}

async function frameFind(frameXpath: string) {
  const framePath = frameXpath.split('/$iframe$')
  const tab = await Tabs.getActiveTab()
  if (!tab) {
    throw new Error(ErrorMessage.ACTIVE_TAB_ERROR)
  }
  let frameId = 0
  for (let i = 0; i < framePath.length; i++) {
    const res = await locatorFrameId(tab.id!, frameId, framePath[i])
    if (res && res.frameId !== null) {
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

// try to find frame by element, send message to all frames to find which frame has the element, and return the frameId
async function elementLocatorFrameId(tabId: number, data: ElementInfo) {
  const result = await Tabs.executeFuncOnAllFrame(tabId, (arg) => {
    // @ts-expect-error window in content_script
    return window.handleSync({
      key: 'elementLocatorFrameId',
      data: arg,
    })
  }, [data])
  log.info('find element in all frames to get frameIds', result)
  const validResult = result.find(res => res && typeof res === 'object' && 'frameId' in res && Number.isInteger(res.frameId))
  return validResult ? (validResult as { frameId: number | null }).frameId : null
}

/**
 * Processes a sequence of frames within a browser tab, executing a function on each frame to retrieve iframe element information.
 *
 * For each frame in the `framePath`, this function calls `Tabs.executeFuncOnFrame` to execute a handler that retrieves iframe element data.
 * The position `p` is updated at each step based on the returned `nextPos` from the frame.
 * If an error occurs during processing, the function returns an array containing the `activeElement`.
 * Otherwise, it returns an array of iframe depth information collected from each frame.
 *
 * @param tab - The Chrome tab object where the frames are located.
 * @param framePath - An array of frame identifiers representing the path through nested iframes.
 * @param p - The current position, which is updated as frames are processed.
 * @param activeElement - Information about the currently active element, returned if processing fails.
 * @returns A promise that resolves to an array of iframe depth information, or an array containing the active element if an error occurs.
 */
async function processFrames(tab: chrome.tabs.Tab, framePath: number[], p: Point, activeElement: ElementInfo) {
  const iframeDepthInfo = []
  for (const frame of framePath) {
    try {
      const res = await Tabs.executeFuncOnFrame(tab.id, frame, (arg) => {
        // @ts-expect-error window in content_script
        return window.handleSync({
          key: 'getIframeElement',
          data: arg,
        })
      }, [p])

      iframeDepthInfo.push(res)
      const { nextPos } = res as { nextPos: Point }
      p.x = nextPos.x
      p.y = nextPos.y
    }
    catch {
      return [activeElement]
    }
  }
  return iframeDepthInfo
}

/**
 * Retrieves detailed information about an iframe element based on a given point and active element.
 * This function calculates the iframe path and adjusts the element's rectangle coordinates relative to nested iframes.
 * If the element is within nested iframes, it updates the `iframeXpath` and rectangle properties to reflect its position.
 *
 * @param p - The point (coordinates) used to locate the element within the frame hierarchy.
 * @param activeElement - The information about the currently active element, including its frame and xpath.
 * @returns A promise that resolves to an updated `ElementInfo` object with iframe path and adjusted rectangle,
 *          or the original `activeElement` if no iframe nesting is detected.
 */
export async function getIframeElement(p: Point, activeElement: ElementInfo) {
  const tab = await Tabs.getActiveTab()
  const frames = await Tabs.getAllFrames(tab.id)
  const iframeElementInfo = JSON.parse(JSON.stringify(activeElement))

  let targetFrame = frames.find(frame => frame.frameId === activeElement.frameId)
  const framePath: number[] = []
  // get the position of the frame relative to the parent frame
  while (targetFrame) {
    framePath.unshift(targetFrame.frameId)
    targetFrame = frames.find(frame => frame.frameId === targetFrame.parentFrameId)
  }
  const iframeDepthInfo = await processFrames(tab, framePath, p, activeElement)

  if (iframeDepthInfo.length > 0) {
    const lastElement = iframeDepthInfo[iframeDepthInfo.length - 1]
    const isPathEqual = lastElement.xpath === activeElement.xpath
    const isUrlEqual = lastElement.url === activeElement.url
    if (!isPathEqual || !isUrlEqual) {
      iframeDepthInfo[iframeDepthInfo.length - 1] = iframeElementInfo
    }

    let iPathDirs: ElementDirectory[] = []
    let iXpath = ''
    const iStack = iframeDepthInfo.slice(0, -1)
    iStack.forEach((frameInfo, index) => {
      if (index === 0) {
        iXpath = frameInfo.xpath
        iPathDirs = frameInfo.pathDirs || []
      }
      else {
        iXpath = `${iXpath}/$iframe$${frameInfo.xpath}`
        iPathDirs = [
          ...iPathDirs,
          ...frameInfo.pathDirs,
        ]
      }
      if (frameInfo.iframeContentRect) {
        iframeElementInfo.rect.x += frameInfo.iframeContentRect.x
        iframeElementInfo.rect.y += frameInfo.iframeContentRect.y
      }
    })
    // iframeElementInfo left, top, right, bottom,
    iframeElementInfo.rect.left = iframeElementInfo.rect.x
    iframeElementInfo.rect.top = iframeElementInfo.rect.y
    iframeElementInfo.rect.right = iframeElementInfo.rect.x + iframeElementInfo.rect.width
    iframeElementInfo.rect.bottom = iframeElementInfo.rect.y + iframeElementInfo.rect.height

    iframeElementInfo.iframeXpath = iXpath
    iframeElementInfo.iframePathDirs = iPathDirs

    return iframeElementInfo
  }
  else {
    return activeElement
  }
}

function findFrameByUrl(frames: FrameDetails[], url: string) {
  return frames.find(frame => frame.url.includes(url))
}

/**
 * Finds a frame within a list of frames by traversing the hierarchy using an iframe XPath.
 *
 * The function splits the provided `iframeXpath` into segments using the delimiter `/$iframe$`,
 * then iteratively searches for child frames matching each segment, starting from the root frame
 * (where `frameId === 0`). If any segment does not match a frame in the hierarchy, the function returns `null`.
 *
 * @param frames - An array of `FrameDetails` objects representing all available frames.
 * @param iframeXpath - A string representing the hierarchical XPath to the target iframe, delimited by `/$iframe$`.
 * @returns The `FrameDetails` object corresponding to the target frame if found; otherwise, `null`.
 */
function findFrameByXpath(frames: FrameDetails[], iframeXpath: string) {
  if (!iframeXpath || !Array.isArray(frames) || frames.length === 0)
    return null

  const segments = iframeXpath
    .split('/$iframe$')
    .map(s => s.trim())
    .filter(Boolean)
  if (segments.length === 0)
    return null

  const rootFrame = frames.find(f => f.frameId === 0)
  if (!rootFrame)
    return null

  let current: FrameDetails | null = rootFrame
  for (const seg of segments) {
    const next = frames.find(f => f.iframeXpath === seg && f.parentFrameId === current!.frameId)
    if (!next)
      return null
    current = next
  }
  return current
}

export function getFramePath(frames: FrameDetails[], targetFrame: FrameDetails) {
  const framePath: FrameDetails[] = []
  while (targetFrame) {
    framePath.unshift(targetFrame)
    targetFrame = frames.find(frame => frame.frameId === targetFrame.parentFrameId)
  }
  return framePath
}

export function buildFrameTree(frames: FrameDetails[]) {
  const frameMap = new Map<number, FrameDetails & { children: FrameDetails[] }>()

  frames.forEach((frame) => {
    frameMap.set(frame.frameId, { ...frame, children: [] })
  })
  const roots: (FrameDetails & { children: FrameDetails[] })[] = []
  frameMap.forEach((frame) => {
    if (frame.parentFrameId === -1) {
      roots.push(frame)
    }
    else {
      const parent = frameMap.get(frame.parentFrameId)
      if (parent) {
        parent.children.push(frame)
      }
    }
  })
  function frameTreeHelper(tree) {
    tree.forEach((frame) => {
      if (frame.children.length > 0) {
        frameTreeHelper(frame.children)
      }
      else {
        delete frame.children
      }
    })
  }
  frameTreeHelper(roots)

  return roots
}

/**
 * Calculates the absolute position of a nested frame within a browser tab by aggregating the positions of each frame in the provided `framePath`.
 *
 * For each frame (except the last one) in the `framePath`, this function executes a position retrieval function on the corresponding frame,
 * then sums up all the positions to determine the absolute position relative to the top-level document.
 *
 * @param tabId - The ID of the browser tab containing the frames.
 * @param framePath - An array of `FrameDetails` representing the hierarchy of frames, from the top-level frame to the target frame.
 * @returns A promise that resolves to a `Point` object containing the absolute `x` and `y` coordinates.
 */
export async function calculateAbsolutePosition(tabId: number, framePath: FrameDetails[]) {
  const posPromises = framePath.slice(0, -1).map((frame, index) => {
    const nextFrame = framePath[index + 1]
    const args = [{
      iframeXpath: nextFrame.iframeXpath,
      url: nextFrame.url,
    }]
    return Tabs.executeFuncOnFrame(tabId, frame.frameId, (arg) => {
      // @ts-expect-error window in content_script
      return window.handleSync({
        key: 'getFramePosition',
        data: arg,
      })
    }, args)
  })

  const posRes = await Promise.all(posPromises) as Point[]
  return posRes.reduce(
    (acc, pos) => {
      acc.x += pos.x
      acc.y += pos.y
      return acc
    },
    { x: 0, y: 0 },
  )
}

export function adjustPosition(rect: DOMRectT | DOMRectT[], absolutePos: Point) {
  if (Array.isArray(rect)) {
    rect.forEach(r => adjustRectPosition(r, absolutePos))
  }
  else {
    adjustRectPosition(rect, absolutePos)
  }
}

function adjustRectPosition(rect: DOMRectT, absolutePos: Point) {
  rect.x += absolutePos.x
  rect.y += absolutePos.y
  rect.left = rect.x
  rect.top = rect.y
  rect.right = rect.x + rect.width
  rect.bottom = rect.y + rect.height
}
