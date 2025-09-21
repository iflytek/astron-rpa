/** @format */
declare enum StatusCode {
  SUCCESS = '0000',
  UNKNOWN_ERROR = '5001', // 通用错误
  ELEMENT_NOT_FOUND = '5002', // 元素未找到
  EXECUTE_ERROR = '5003', // 执行错误
  VERSION_ERROR = '5004', // 版本错误
}
interface ElementPosition {
  element: HTMLElement
  x: number
  y: number
  width: number
  height: number
  top: number
  left: number
  bottom: number
  right: number
}

interface ElementRange {
  start: {
    x: number
    y: number
  }
  end: {
    x: number
    y: number
  }
}

interface Point {
  x: number
  y: number
}

interface ElementDirectory {
  tag: string
  value: string
  checked: boolean
  attrs: ElementAttrs[]
}

interface ElementAttrs {
  name: string
  value: string | number
  checked: boolean
  type: number
}

interface DOMRectT {
  left: number
  top: number
  width: number
  height: number
  right: number
  bottom: number
  x: number
  y: number
}

interface ElementParams {
  key: string
  data: ElementInfo
  predata?: ElementInfo // 上一个元素信息，用于相似元素获取
}

interface Options {
  relativeType: 'child' | 'parent' | 'sibling'
  elementGetType: 'index' | 'xpath' | 'last' | 'all' | 'next' | 'prev' | '' // index xpath 为 getType 为 child 时， 第 index 个子元素, xpath 为子元素相对xpath, all 为所有子元素, next 为下一个兄弟元素, prev 为上一个兄弟元素
  index?: number // getType 为 child 时， 第 index 个子元素, 默认为 0
  xpath?: string // getType 为 child 时， 子元素相对xpath
}

interface ElementInfo {
  xpath: string
  cssSelector: string
  pathDirs: Array<ElementDirectory>
  parentClass?: string
  rect: DOMRectT
  domain: string
  url: string
  shadowRoot: boolean // 是否是shadowRoot
  tabTitle?: string
  tabUrl?: string
  favIconUrl?: string
  isFrame?: boolean // 是否是iframe
  checkType?: 'visualization' | 'customization' // 获取元素类型，可视化获取 / 自定义获取
  matchTypes?: Array<string> // 匹配类型， 位置匹配onlyPosition / 滚动查找scrollPosition
  // watch?: boolean; // 是否监听元素变化
  frameId?: number
  iframeXpath?: string // iframe的xpath
  iframeCssSelector?: string
  similarCount?: number // 相似元素个数，用于相似拾取
  preData?: ElementInfo // 上一个元素信息，用于相似元素获取
  tag?: string // 拾取元素标签名，用于拾取过程中展示
  text?: string // 拾取元素名称，用于展示
  // hightlight?: boolean;
  openSourcePage?: boolean // 是否打开元素原始页面，抓取使用
  value_type?: string // 抓取数据显示类型，抓取使用
  batchType?: string // 抓取类型，抓取使用

  index?: number // 相似元素迭代使用
  count?: number // 相似元素迭代使用

  relativeOptions?: Options // 关联元素获取参数，用于获取相对元素

  atomConfig?: any // 元素原子配置参数
}

interface SocketParamsType {
  url?: string
  port?: number
  noCreatRouters?: Array<string>
  noInitCreat?: boolean
  reconnectMaxTime?: number
  reconnectDelay?: number
  isReconnect?: boolean
  reconnectCount?: number
  heartTime?: number
}

interface ContentResult {
  code: StatusCode
  data: any
  msg: string
}

interface FrameDetails {
  errorOccurred: boolean
  processId: number
  frameId: number
  parentFrameId: number
  url: string
  documentId: string
  parentDocumentId?: string
  documentLifecycle: chrome.extensionTypes.DocumentLifecycle
  frameType: chrome.extensionTypes.FrameType
  iframeXpath?: string
  iframeCssSelector?: string
  xpath?: string
}

interface Rects {
  x: number
  y: number
  width: number
  height: number
  left: number
  top: number
  right: number
  bottom: number
}

interface CookieDetails {
  url: string
  name?: string
  value?: string
  domain?: string
  path?: string
  secure?: boolean
  httpOnly?: boolean
  expirationDate?: number
}

interface SimilarDataValueT {
  text: string
  attrs?: {
    text?: string
    src?: string
    href?: string
  }
}

interface GenerateParamsT {
  type: 'xpath' | 'cssSelector'
  value: string
}

type XPathStep = string

interface WatchXPathResult {
  found: boolean
  lastMatchedNode: Node | null
  lastMatchedStep: XPathStep | null
  notFoundStep: XPathStep | null
  notFoundIndex?: number // 未找到的索引位置
}
interface CurrentFrameInfo {
  frameId?: number
  iframeXpath: string
  iframeTransform?: {
    scaleX: number
    scaleY: number
  }
}

// 策略
type Strategy = 'all' | 'visualization' | 'customization'
