export enum PickMode {
  NORMAL = 'normal',
  SMART = 'smart',
  CV = 'cv',
  WINDOW = 'window',
  ELEMENT = "element",
  POINT = "point",
  SIMILAR = "similar",
  BATCH = "batch",
}

export const PickTip = {
  [PickMode.NORMAL]: '元素拾取',
  [PickMode.SMART]: '智能识别',
  [PickMode.CV]: 'CV识别',
  [PickMode.WINDOW]: '窗口拾取',
  [PickMode.ELEMENT]: '元素拾取',
  [PickMode.POINT]: '坐标拾取',
  [PickMode.SIMILAR]: '相似元素拾取',
  [PickMode.BATCH]: '批量抓取',
}

const defaultShortCuts = [
  {
    title: "捕获元素",
    keys: 'Ctrl + 鼠标左键',
  },
  {
    title: "退出",
    keys: 'Esc',
  }
]

const cvShortCuts = [
  {
    title: "截图拾取",
    keys: 'Ctrl',
  },
  {
    title: "智能拾取",
    keys: 'Alt',
  },
  {
    title: "退出",
    keys: 'Esc',
  }
]

export const PickShortCuts = {
  [PickMode.NORMAL]: defaultShortCuts,
  [PickMode.SMART]: defaultShortCuts,
  [PickMode.CV]: cvShortCuts,
  [PickMode.WINDOW]: defaultShortCuts,
  [PickMode.ELEMENT]: defaultShortCuts,
  [PickMode.POINT]: defaultShortCuts,
  [PickMode.SIMILAR]: defaultShortCuts,
  [PickMode.BATCH]: defaultShortCuts,
}

export const TipPosition = {
  leftTop: {
    top: '10px',
    left: '10px',
  },
  rightBottom: {
    bottom: '60px',
    right: '10px',
  }
}
