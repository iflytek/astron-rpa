/** @format */
/* eslint-disable unused-imports/no-unused-vars */

import { generateUUID } from '@/utils/common'

import type { CustomValueType, DirectoryAttrItem, DirectoryItem, EleVariableType, VarDataType, WebElementType } from '@/types/resource'
import { PATTERN_RULES, PATTERN_RULES_IE, PATTERN_RULES_JAB, PATTERN_RULES_UIA, PATTERN_RULES_WEB, IFRAME_NODES, SHADOW_ROOT_FLAG } from '@/views/Arrange/config/pick'

export type ElementT = 'uia' | 'web' | 'cv' | 'jab' | 'sap' | 'msaa'

// ==================== 核心接口定义 ====================

/**
 * 元素格式化策略接口
 */
interface IElementFormatStrategy {
  /**
   * 格式化目录数据
   */
  formatDirectory: (data: any, app?: string) => any[]

  /**
   * 恢复目录数据
   */
  recoverDirectory: (data: any) => any

  /**
   * 格式化自定义数据
   */
  formatCustom?: (data: any) => any[]

  /**
   * 恢复自定义数据
   */
  recoverCustom?: (data: any) => any

  /**
   * 获取类型规则
   */
  getTypesPattern: (name: string) => any[]

  /**
   * 获取版本标识
   */
  getVersion: () => string
}

/**
 * 元素格式化配置
 */
interface IElementFormatConfig {
  version: string
  patternType: string
  patternRules: any[]
  ignoreKeys?: string[]
  formatOptions?: {
    checkDisabled?: boolean
    addDisabled?: boolean
    deleteDisabled?: boolean
  }
}

// ==================== 基础抽象类 ====================

/**
 * 元素格式化基础类
 * 实现通用逻辑，子类只需覆盖特定逻辑
 */
abstract class BaseElementFormatStrategy implements IElementFormatStrategy {
  protected config: IElementFormatConfig

  constructor(config: IElementFormatConfig) {
    this.config = config
  }

  getVersion(): string {
    return this.config.version
  }

  getTypesPattern(name: string): any[] {
    const rules = this.config.patternRules
    if (name === 'index') {
      // index 类型为数字 只有等于条件
      return rules.filter(item => item.value === 0)
    }
    return rules.length > 0 ? rules : PATTERN_RULES
  }

  /**
   * 通用目录格式化
   */
  formatDirectory(data: any, app?: string): any[] {
    if (!data)
      return []

    const ignoreKeys = this.config.ignoreKeys || ['checked', 'tag_name', 'disable_keys', 'attrs_map']

    return data.map((item: DirectoryItem) => {
      const attrKeys = Object.keys(item).filter(key => !ignoreKeys.includes(key))

      return {
        _version: this.config.version,
        _checkDisabled: this.config.formatOptions?.checkDisabled ?? false,
        _addDisabled: this.config.formatOptions?.addDisabled ?? false,
        _deleteDisabled: this.config.formatOptions?.deleteDisabled ?? false,
        tag: item.tag_name,
        checked: item.checked !== false,
        value: item.tag_name,
        attrs: attrKeys.map((key, index) => {
          return this.formatAttribute(item, key, index)
        }),
      }
    })
  }

  /**
   * 格式化单个属性
   */
  protected formatAttribute(item: DirectoryItem, key: string, index: number): any {
    const attr = {
      _checkDisabled: false,
      _addDisabled: false,
      _deleteDisabled: false,
      _typeDisabled: false,
      _nameDisabled: false,
      _typesPattern: this.getTypesPattern(key),
      value: item[key],
      type: item.attrs_map?.[key] ?? 0,
      name: key,
      checked: item.disable_keys ? !item.disable_keys.includes(key) : true,
      variableValue: null,
    }
    attr.variableValue = this.createVariableValue(attr, index)
    return attr
  }

  /**
   * 通用目录恢复
   */
  recoverDirectory(data: any) {
    if (!data)
      return []

    return data.map((item: any) => {
      const attrs = item.attrs
      const attrObj: any = {
        tag_name: item.value,
        checked: item.checked,
        disable_keys: [],
        attrs_map: {},
      }

      attrs.forEach((attr: any) => {
        const variableValue = attr.variableValue
          ? this.saveVariableValue(attr.variableValue.value)
          : attr.value
        attrObj[attr.name] = variableValue

        if (!attr.checked) {
          attrObj.disable_keys.push(attr.name)
        }
        attrObj.attrs_map[attr.name] = attr.type
      })

      return attrObj
    })
  }

  /**
   * 默认不支持自定义格式化
   */
  formatCustom?(data: any): any[] {
    return []
  }

  /**
   * 默认不支持自定义恢复
   */
  recoverCustom?(data: any): any {
    return {}
  }

  /**
   * 创建变量值
   */
  protected createVariableValue(item: DirectoryAttrItem | CustomValueType, index: number): any {
    const variableValue = this.makeVariableValue(item.value)
    return {
      types: 'Any',
      default: '',
      rowIdx: index,
      formType: {
        type: 'INPUT_VARIABLE',
        params: {
          values: [],
        },
      },
      key: item.name,
      title: item.name,
      name: item.name,
      value: variableValue,
      show: true,
      uniqueKey: generateUUID(),
    }
  }

  /**
   * 制作变量值
   */
  protected makeVariableValue(val: EleVariableType | any): VarDataType[] {
    const isVariable = val !== null
      && typeof val === 'object'
      && 'rpa' in val
      && val.rpa === 'special'

    return isVariable
      ? val.value
      : [{ type: 'other', value: val === null ? '' : val }]
  }

  /**
   * 保存变量值
   */
  protected saveVariableValue(value: VarDataType[]) {
    return {
      rpa: 'special',
      value,
    }
  }
}

// ==================== 具体策略实现 ====================

/**
 * UIA 元素格式化策略
 */
class UiaElementFormatStrategy extends BaseElementFormatStrategy {
  constructor() {
    super({
      version: 'uia_1',
      patternType: 'uia_1',
      patternRules: PATTERN_RULES_UIA,
    })
  }
}

/**
 * MSAA 元素格式化策略（复用 UIA 逻辑）
 */
class MsaaElementFormatStrategy extends UiaElementFormatStrategy {
  constructor() {
    super()
    this.config.version = 'msaa_1'
  }
}

/**
 * JAB 元素格式化策略
 */
class JabElementFormatStrategy extends BaseElementFormatStrategy {
  constructor() {
    super({
      version: 'jab_1',
      patternType: 'jab_1',
      patternRules: PATTERN_RULES_JAB,
    })
  }
}

/**
 * Web 元素格式化策略
 */
class WebElementFormatStrategy extends BaseElementFormatStrategy {
  constructor() {
    super({
      version: 'web_1',
      patternType: 'web_1',
      patternRules: PATTERN_RULES_WEB,
    })
  }

  /**
   * Web 特殊的目录格式化
   * @returns 返回对象 [...iframePathDirs, ...pathDirs]，其中 pathDirs 和 iframePathDirs 都是格式化后的目录数组
   */
  override formatDirectory(data: { pathDirs: DirectoryItem[], iframePathDirs?: DirectoryItem[] }, app?: string) {
    if (!data || !data.pathDirs)
      return []

    const formatDirs = (dirs: DirectoryItem[]) => {
      return dirs.map((item: DirectoryItem) => {
        return {
          _version: 'web_1',
          _checkDisabled: item.tag === '$shadow$',
          _addDisabled: false,
          _deleteDisabled: item.tag === '$shadow$',
          tag: item.value || item.tag,
          checked: item.checked === true,
          value: item.value || item.tag,
          attrs: item.attrs.map((attr: DirectoryAttrItem, index: number) => {
            return {
              variableValue: this.createVariableValue(attr, index),
              _deleteDisabled: true,
              _nameDisabled: true,
              _typesPattern: app === 'iexplore'
                ? this.getIETypesPattern(attr.name)
                : this.getTypesPattern(attr.name),
              value: attr.value,
              type: attr.type || 0,
              name: attr.name,
              checked: attr.checked === true,
            }
          }),
        }
      })
    }

    const pathDirs = formatDirs(data.pathDirs)
    const iframePathDirs = data.iframePathDirs ? formatDirs(data.iframePathDirs) : []

    return [...iframePathDirs, ...pathDirs]
  }

  /**
   * 获取 IE 类型规则
   */
  private getIETypesPattern(name: string): any[] {
    const rules = PATTERN_RULES_IE
    if (name === 'index') {
      return rules.filter(item => item.value === 0)
    }
    return rules.length > 0 ? rules : PATTERN_RULES
  }

  /**
   * Web 特殊的目录恢复
   * @param data 格式化后的数据
   * @returns 恢复后的对象 { pathDirs: DirectoryItem[], iframePathDirs?: DirectoryItem[] }，其中 pathDirs 和 iframePathDirs 都是恢复后的目录数组
   */
  override recoverDirectory(data: DirectoryItem[]) {
    if (!data)
      return []

    // 恢复单个目录数组的函数
    const recoverDirs = (dirs: DirectoryItem[]) => {
      return dirs.map((item: DirectoryItem) => {
        return {
          tag: item.value || item.tag,
          checked: item.checked,
          value: item.value,
          attrs: item.attrs.map((attr: DirectoryAttrItem & { variableValue: EleVariableType }) => {
            const variableValue = attr.variableValue
              ? this.saveVariableValue(attr.variableValue.value)
              : attr.value
            return {
              name: attr.name,
              value: variableValue,
              checked: attr.checked,
              type: attr.type,
            }
          }),
        }
      })
    }

    // 区分 iframePathDirs 和 pathDirs
    let lastIframeIndex = data.findLastIndex(item => IFRAME_NODES.includes(item.tag))
    if (lastIframeIndex === data.length - 1) { // iframe是最后一个节点, 当做普通节点
      lastIframeIndex = data.slice(0, data.length - 1).findLastIndex(item => IFRAME_NODES.includes(item.tag))
    }
    const iframePathDirs = lastIframeIndex !== -1 ? recoverDirs(data.slice(0, lastIframeIndex + 1)) : []
    const pathDirs = recoverDirs(data.slice(lastIframeIndex + 1))
    return { pathDirs, iframePathDirs }
  }

  /**
   * Web 自定义格式化
   */
  override formatCustom(data: WebElementType): any[] {
    if (!data)
      return []

    const { xpath, cssSelector, shadowRoot, url, isFrame, iframeXpath } = data
    const resArr = [
      { name: 'url', value: url },
      { name: 'xpath', value: xpath },
      { name: 'cssSelector', value: cssSelector },
    ]

    if (shadowRoot) {
      // shadowRoot 使用 cssSelector 匹配，不使用 xpath
      const xpathIndex = resArr.findIndex(item => item.name === 'xpath')
      resArr.splice(xpathIndex, 1)
    }

    if (isFrame) {
      const urlIndex = resArr.findIndex(item => item.name === 'url')
      resArr.splice(urlIndex, 1)
      resArr.unshift({ name: 'iframeXpath', value: iframeXpath })
    }

    return this.customValueFormatVariable(resArr)
  }

  /**
   * Web 自定义恢复
   */
  override recoverCustom(data: any[]): any {
    const obj = {}
    data.forEach((item) => {
      const variableObj = this.saveVariableValue(item.value)
      obj[item.name] = variableObj
    })
    return obj
  }

  /**
   * 将数组数据格式化为支持变量的模式数据
   */
  private customValueFormatVariable(arr: CustomValueType[]): any[] {
    return arr.map((item, index) => {
      return this.createVariableValue(item, index)
    })
  }
}

/**
 * 通用元素格式化策略（用于未知类型）
 */
class CommonElementFormatStrategy extends BaseElementFormatStrategy {
  constructor() {
    super({
      version: 'common_1',
      patternType: 'common_1',
      patternRules: PATTERN_RULES,
    })
  }
}

// ==================== 策略注册器 ====================

/**
 * 元素格式化策略注册器
 * 支持动态注册和查找策略
 */
class ElementFormatStrategyRegistry {
  private strategies: Map<string, IElementFormatStrategy> = new Map()
  private defaultStrategy: IElementFormatStrategy

  constructor() {
    // 注册默认策略
    this.defaultStrategy = new CommonElementFormatStrategy()

    // 注册内置策略
    this.registerBuiltInStrategies()
  }

  /**
   * 注册内置策略
   */
  private registerBuiltInStrategies(): void {
    this.register('uia', new UiaElementFormatStrategy())
    this.register('msaa', new MsaaElementFormatStrategy())
    this.register('jab', new JabElementFormatStrategy())
    this.register('web', new WebElementFormatStrategy())
    this.register('common', new CommonElementFormatStrategy())
  }

  /**
   * 注册策略
   */
  register(type: string, strategy: IElementFormatStrategy): void {
    this.strategies.set(type.toLowerCase(), strategy)
  }

  /**
   * 获取策略
   */
  getStrategy(type: string): IElementFormatStrategy {
    const strategy = this.strategies.get(type.toLowerCase())
    return strategy || this.defaultStrategy
  }

  /**
   * 检查策略是否存在
   */
  hasStrategy(type: string): boolean {
    return this.strategies.has(type.toLowerCase())
  }

  /**
   * 获取所有已注册的类型
   */
  getRegisteredTypes(): string[] {
    return Array.from(this.strategies.keys())
  }
}

// ==================== 单例注册器 ====================

const strategyRegistry = new ElementFormatStrategyRegistry()

// ==================== 对外 API ====================

/**
 * 元素信息格式化转换
 * @param version - version of the format (暂时保留，未来可用于版本控制)
 * @param type - type of the format
 * @param data - data to format
 * @param app - application type (optional)
 * @returns - formatted data
 */
export function elementDirectoryFormat(version: string = '1', type: ElementT, data: any, app?: string) {
  const strategy = strategyRegistry.getStrategy(type)
  return strategy.formatDirectory(data, app)
}

/**
 * 元素信息格式化恢复
 */
export function elementDirectoryFormatRecover(version: string = '1', type: ElementT, data: any) {
  const strategy = strategyRegistry.getStrategy(type)
  return strategy.recoverDirectory(data)
}

/**
 * custom 自定义编辑的数据格式化
 */
export function elementCustomFormat(version: string = '1', type: ElementT, data: any) {
  const strategy = strategyRegistry.getStrategy(type)
  return strategy.formatCustom?.(data) ?? []
}

/**
 * 自定义编辑数据恢复
 */
export function elementCustomFormatRecover(version: string = '1', type: ElementT, data: any) {
  if (!data)
    return {}
  const strategy = strategyRegistry.getStrategy(type)
  return strategy.recoverCustom?.(data) ?? {}
}

/**
 * 获取类型规则
 */
export function typesPattern(type: string, name: string) {
  // 兼容旧的调用方式
  const typeMap = {
    uia_1: 'uia',
    web_1: 'web',
    jab_1: 'jab',
    ie_1: 'web', // IE 使用 web 策略
    common_1: 'common',
  }

  const strategyType = typeMap[type] || 'common'
  const strategy = strategyRegistry.getStrategy(strategyType)
  return strategy.getTypesPattern(name)
}

/**
 * 添加属性
 */
export function addAttr(v: string, index: number) {
  const strategy = strategyRegistry.getStrategy(v.replace(/_\d+$/, ''))
  const attr = {
    name: '',
    type: 0,
    value: '',
    checked: false,
    _typesPattern: strategy.getTypesPattern(''),
    variableValue: null,
  }
  attr.variableValue = (strategy as any).createVariableValue(attr, index)
  return attr
}

/**
 * 添加节点
 */
export function addNode(v: string, originNode: DirectoryItem) {
  return {
    _version: v,
    tag: originNode.tag,
    checked: true,
    value: originNode.value,
    attrs: [],
  }
}

/**
 * 过滤 elementAction
 */
export function filterActionData(data, actions) {
  const actionData = data
    .filter(i => actions.includes(i.key) || i.menus.some(item => actions.includes(item.key)))
    .map((i) => {
      if (i.menus) {
        i.menus = i.menus.filter(item => actions.includes(item.key))
      }
      return i
    })

  const moreItem = actionData.find(item => item.key === 'more')
  if (!moreItem)
    return actionData

  const moreMenusKeys = moreItem.menus.map(item => item.key)
  const externalItems = actionData.filter(item => item.key !== 'more')

  // 如果more中只有一项，且外层包含，则过滤掉more
  if (moreItem.menus.length === 1 && externalItems.some(extItem => extItem.key === moreItem.menus[0].key)) {
    return actionData.filter(item => item.key !== 'more')
  }

  return actionData.filter(item => item.key === 'more' || !moreMenusKeys.includes(item.key))
}

// ==================== 扩展 API ====================

/**
 * 注册自定义元素类型策略
 * @param type 元素类型
 * @param strategy 格式化策略
 * @example
 * ```ts
 * // 注册新的元素类型
 * class SapElementFormatStrategy extends BaseElementFormatStrategy {
 *   constructor() {
 *     super({
 *       version: 'sap_1',
 *       patternType: 'sap_1',
 *       patternRules: PATTERN_RULES_SAP,
 *     })
 *   }
 * }
 *
 * registerElementStrategy('sap', new SapElementFormatStrategy())
 * ```
 */
export function registerElementStrategy(type: string, strategy: IElementFormatStrategy): void {
  strategyRegistry.register(type, strategy)
}

/**
 * 检查元素类型是否已注册
 */
export function hasElementStrategy(type: string): boolean {
  return strategyRegistry.hasStrategy(type)
}

/**
 * 获取所有已注册的元素类型
 */
export function getRegisteredElementTypes(): string[] {
  return strategyRegistry.getRegisteredTypes()
}

/**
 * 导出基础类供扩展使用
 */
export { BaseElementFormatStrategy, type IElementFormatConfig, type IElementFormatStrategy }
