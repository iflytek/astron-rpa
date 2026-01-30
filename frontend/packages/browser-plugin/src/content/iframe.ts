import { directoryXpath, getElementByXPath, getIFramesElements, getIframeTransform } from './element'
import { requestFrame } from './message'

const currentFrameInfo = {
  frameId: 0,
  iframeXpath: '',
  iframeTransform: {
    scaleX: 1,
    scaleY: 1,
  },
}

function postToIframe(frameDom) {
  frameDom.contentWindow?.postMessage({
    key: 'setCurrentWindowIframeInfo',
    data: {
      iframeXpath: directoryXpath(frameDom),
      iframeTransform: getIframeTransform(frameDom),
    },
  }, '*')
}
function postToParent() {
  window.parent.postMessage({
    key: 'getCurrentWindowIframeInfo',
  }, '*')
  window.parent.postMessage({
    key: 'bindCurrentWindowIframeInfo',
    data: currentFrameInfo,
  }, '*')
}
function tagFrames() {
  const frames = getIFramesElements()
  frames.forEach((frame) => {
    if (frame.complete) {
      postToIframe(frame)
    }
    frame.onload = () => {
      postToIframe(frame)
    }
    postToIframe(frame)
  })
  if (window.parent !== window) {
    postToParent()
  }
}
function tagFrameId(frameInfo: typeof currentFrameInfo) {
  const iframeEle = frameInfo.iframeXpath ? getElementByXPath(frameInfo.iframeXpath) : null
  if (iframeEle) {
    iframeEle.dataset.astronFrameId = String(frameInfo.frameId)
  }
}
function requestFrameId() {
  requestFrame().then((frameId) => {
    currentFrameInfo.frameId = frameId as number
    if (frameId !== 0) {
      window.parent.postMessage({
        key: 'bindCurrentWindowIframeInfo',
        data: currentFrameInfo,
      }, '*')
    }
  })
}
function listenMessage(ev: MessageEvent) {
  const { key, data } = ev.data
  if (data && key === 'setCurrentWindowIframeInfo') {
    currentFrameInfo.iframeXpath = data.iframeXpath
    currentFrameInfo.iframeTransform = data.iframeTransform
  }
  if (key === 'getCurrentWindowIframeInfo') {
    tagFrames()
  }
  if (data && key === 'bindCurrentWindowIframeInfo') {
    tagFrameId(data)
  }
}

function loadIframe() {
  window.removeEventListener('message', listenMessage)
  window.addEventListener('message', listenMessage)
  requestFrameId()
  tagFrames()
}

export { currentFrameInfo, loadIframe, tagFrameId, tagFrames }
