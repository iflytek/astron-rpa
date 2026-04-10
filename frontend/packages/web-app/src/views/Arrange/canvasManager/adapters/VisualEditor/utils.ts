import { SnowflakeIdv1 } from 'simple-flakeid'
import { isEmpty, cloneDeep, partition } from 'lodash-es'

import { getAbilityInfo, getNewAtomDesc } from '@/api/atom'
import { ATOM_FORM_TYPE, ATOM_KEY_MAP, VAR_IN_TYPE } from '@/constants/atom'
import { useProcessStore } from '@/stores/useProcessStore'
import { useVariableStore } from '@/stores/useVariableStore'
import { isComponentKey, getComponentId, getComponentForm } from '@/utils/customComponent'
import { generateName } from '@/views/Arrange/utils'

export class AbilityInfoCache {
  // 缓存 Map，以 key:version 作为键
  private abilityInfoCache = new Map<string, RPA.Atom>()

  public getCacheKey(item: RPA.Flow.FlowItemValue) {
    return `${item.key}:${item.version}`
  }

  public setAbilityInfoCache(atom: RPA.Atom) {
    this.abilityInfoCache.set(this.getCacheKey(atom), atom)
  }

  /**
   * 按 key 模糊查找缓存，返回 version 最新的条目
   */
  private findLatestCacheByKey(key: string): RPA.Atom | undefined {
    let latest: RPA.Atom | undefined
    let maxVersion = ''
    for (const [cacheKey, atom] of this.abilityInfoCache) {
      if (!cacheKey.startsWith(`${key}:`)) continue
      const ver = cacheKey.split(':').pop() || ''
      if (!maxVersion || this.compareVersion(ver, maxVersion) > 0) {
        maxVersion = ver
        latest = atom
      }
    }
    return latest
  }

  private compareVersion(a: string, b: string): number {
    const pa = a.split('.').map(Number)
    const pb = b.split('.').map(Number)
    const len = Math.max(pa.length, pb.length)
    for (let i = 0; i < len; i++) {
      const diff = (pa[i] || 0) - (pb[i] || 0)
      if (diff !== 0) return diff
    }
    return 0
  }

  /**
   * 获取原子能力信息（带缓存和去重）
   * @param atomKeyMap 原子能力的 key 和 version 数组
   * @returns 以 CacheKey 为键，RPA.Atom 为值的对象
   */
  public async getAbilityInfoWithCache(atomValues: RPA.Flow.FlowItemValue[]): Promise<Record<string, RPA.Atom>> {
    // 去重并分离已缓存和未缓存的数据
    const seen = new Set<string>()
    const cachedAtoms: Record<string, RPA.Atom> = {}
    const uncachedKeys: { key: string; version: string }[] = []
    const uncachedComponentItems: RPA.Flow.FlowItemValue[] = []

    for (const item of atomValues) {
      const cacheKey = this.getCacheKey(item)
      if (seen.has(cacheKey)) continue
      seen.add(cacheKey)

      const cached = this.abilityInfoCache.get(cacheKey)
      if (cached) {
        cachedAtoms[cacheKey] = cached
      } else if (isComponentKey(item.key)) {
        uncachedComponentItems.push(item)
      } else {
        uncachedKeys.push({ key: item.key, version: item.version })
      }
    }

    // 请求未缓存的标准原子能力
    const newAtoms = uncachedKeys.length > 0 ? await getAbilityInfo(uncachedKeys) : []

    // 请求未缓存的自定义组件
    const componentAtoms = await Promise.all(
      uncachedComponentItems.map(item =>
        getComponentForm({ componentId: getComponentId(item.key), version: item.version, context: 'get' }),
      ),
    )

    const result: Record<string, RPA.Atom> = { ...cachedAtoms };

    [...newAtoms, ...componentAtoms].forEach(atom => {
      const cacheKey = this.getCacheKey(atom)
      this.setAbilityInfoCache(atom)
      result[cacheKey] = atom
    })

    return result
  }

  /**
   * 获取最新的原子能力信息
   * @param key 原子能力 key，可带版本后缀，格式：{atom.key}:{atom.version}
   * @returns 原子能力信息
   */
  public async getLatestAbilityInfo(key: string): Promise<RPA.Atom> {
    // 1. 精确匹配缓存
    const exactCached = this.abilityInfoCache.get(key)
    if (exactCached) return exactCached

    // 2. 按 key 匹配缓存中 version 最新的条目
    const latestCached = this.findLatestCacheByKey(key)
    if (latestCached) return latestCached

    // 3. 缓存未命中，请求接口
    let abilityInfo: RPA.Atom
    if (isComponentKey(key)) {
      const [componentKey, version] = key.split(':')
      abilityInfo = await getComponentForm({
        componentId: getComponentId(componentKey),
        version,
        context: 'add',
      })
    } else {
      abilityInfo = await getNewAtomDesc(key)
    }

    this.setAbilityInfoCache(abilityInfo)

    return abilityInfo
  }
}

const exceptionKeys = [
  '__skip_err__',
  '__retry_time__',
  '__retry_interval__',
]

/**
 * 将 Atom 节点数据序列化为后端存储格式
 * 白名单提取：只保留后端需要的字段，去除前端 UI 元数据（formType, options, errors 等）
 */
export function serializeAtomForSave(atom: RPA.Atom): RPA.Flow.FlowItemValue {
  const { key, version, id, alias, disabled, breakpoint, inputList, outputList, advanced, exception } = atom

  const serializeFormItems = (items: RPA.AtomDisplayItem[] = []) =>
    items.map((item) => {
      const result: RPA.AtomDisplayItem = { key: item.key, value: '' }

      if (Array.isArray(item.value)) {
        result.value = item.value.map((v) =>
          v.varId ? { ...v } : { type: v.type, value: v.value, ...(v.data != null ? { data: v.data } : {}) },
        )
      } else {
        result.value = item.value
      }

      if (item.show != null) result.show = item.show

      return result
    })

  return {
    key,
    version,
    id,
    alias,
    inputList: serializeFormItems(inputList),
    outputList: serializeFormItems(outputList),
    advanced: serializeFormItems(advanced),
    exception: serializeFormItems(exception),
    ...(disabled ? { disabled } : {}),
    ...(breakpoint ? { breakpoint } : {}),
  }
}

/**
 * 原子能力的结构分成两部分：
 * 1. AtomMeta 原子能力的元数据，类型为 RPA.Flow.FlowItemValue
 * 2. AtomForm 原子能力的表单数据，类型为 RPA.Atom
 *
 * 将 AtomForm 合并到 AtomMeta 中
 */
export function mergeAtomFormToAtomMeta(atomMeta: RPA.Atom, atomForm: RPA.Flow.FlowItemValue = {} as RPA.Flow.FlowItemValue): RPA.Atom {
  const processStore = useProcessStore()

  const mergeValue = (target: RPA.AtomDisplayItem[], origin: RPA.AtomDisplayItem[]) => {
    if (isEmpty(target)) {
      return []
    }

    if (isEmpty(origin)) {
      return target
    }

    return target.map((item) => {
      const findItem = origin.find((i) => i.key === item.key)
      if (findItem) {
        item.value = findItem.value ?? item.default
        item.show = findItem.show ?? true
      }

      return item
    })
  }

  const [baseAdvanced, baseException] = partition(cloneDeep(processStore.commonAdvancedParameter), item => exceptionKeys.includes(item.key))

  const advanced = mergeValue(baseAdvanced, atomForm.advanced)
  const exception = mergeValue(baseException, atomForm.exception)
  const inputList = mergeValue(atomMeta.inputList, atomForm.inputList)
  const outputList = mergeValue(atomMeta.outputList, atomForm.outputList)

  return {
    ...atomMeta,
    id: atomForm.id,
    alias: atomForm.alias,
    advanced,
    exception,
    inputList,
    outputList,
  }
}

/**
 * 生成唯一id
 */
const genId = new SnowflakeIdv1({ workerId: 1 })
export function genNonDuplicateID(head: string = ''): string {
  const headStr = head || 'bh'
  return `${headStr}${genId.NextId()}`
}

// 生成原子能力id
export function generateId(type: string) {
  let id = genNonDuplicateID()
  if (type === ATOM_KEY_MAP.Group || type === ATOM_KEY_MAP.GroupEnd)
    id = `group_${id}`
  return id
}

/**
 * 判断数组是否连续
 * @param arr 数组
 * @returns 是否连续
 */
export function isContinuous(arr: number[]) {
  const set = new Set(arr)
  return set.size === arr.length && Math.max(...set) - Math.min(...set) + 1 === arr.length
}

/**
 * 为新增原子能力的输出表单生成不重复的变量名
 * @param outputList 原子能力的输出表单列表
 * @param existingVarNames 当前流程中已存在的变量名列表
 */
export function generateOutItems(outputList: RPA.AtomDisplayItem[], existingVarNames: string[]): RPA.AtomDisplayItem[] {
  return outputList.map((item) => {
    const newVarName = generateName(
      existingVarNames.filter(v => new RegExp(`^${item.key}_\\d+$`).test(v) || v === item.key),
      item.key,
      '_',
    )
    existingVarNames.push(newVarName)

    return { ...item, value: [{ type: VAR_IN_TYPE, value: newVarName }] }
  })
}

/**
 * 收集当前流程中所有输出流变量名 + 全局变量名
 */
export function collectFlowVarNames(data: RPA.Atom[] = []): string[] {
  const names: string[] = []
  data.forEach(atom => {
    (atom.outputList || []).forEach((item: RPA.AtomDisplayItem) => {
      const values = item.value as Array<{ type: string, value: string }>
      if (Array.isArray(values)) {
        values.forEach(v => { if (v.type === VAR_IN_TYPE && v.value) names.push(v.value) })
      }
    })
  })
  const globalVarNames = useVariableStore().globalVariableList.map(v => v.varName)
  return names.concat(globalVarNames)
}
