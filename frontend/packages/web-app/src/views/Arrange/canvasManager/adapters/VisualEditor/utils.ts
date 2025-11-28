import { SnowflakeIdv1 } from 'simple-flakeid'
import { isEmpty, cloneDeep } from 'lodash-es'

import { getAbilityInfo, getNewAtomDesc } from '@/api/atom'
import { ATOM_KEY_MAP } from '@/constants/atom'
import { useProcessStore } from '@/stores/useProcessStore'

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
   * 获取原子能力信息（带缓存和去重）
   * @param atomKeyMap 原子能力的 key 和 version 数组
   * @returns 以 CacheKey 为键，RPA.Atom 为值的对象
   */
  public async getAbilityInfoWithCache(atomValues: RPA.Flow.FlowItemValue[]): Promise<Record<string, RPA.Atom>> {
    // 去重并分离已缓存和未缓存的数据
    const seen = new Set<string>()
    const cachedAtoms: Record<string, RPA.Atom> = {}
    const uncachedKeys: { key: string; version: string }[] = []
  
    for (const item of atomValues) {
      const cacheKey = this.getCacheKey(item)
      if (seen.has(cacheKey)) continue
      seen.add(cacheKey)
  
      const cached = this.abilityInfoCache.get(cacheKey)
      if (cached) {
        cachedAtoms[cacheKey] = cached
      } else {
        uncachedKeys.push({ key: item.key, version: item.version })
      }
    }
  
    // 请求未缓存的数据并更新缓存
    const newAtoms = uncachedKeys.length > 0 ? await getAbilityInfo(uncachedKeys) : []
  
    const result: Record<string, RPA.Atom> = { ...cachedAtoms }
    newAtoms.forEach(atom => {
      const cacheKey = this.getCacheKey(atom)
      this.setAbilityInfoCache(atom)
      result[cacheKey] = atom
    })
  
    return result
  }

  /**
   * 获取最新的原子能力信息
   * @param key 原子能力 key
   * @returns 原子能力信息
   */
  public async getLatestAbilityInfo(key: string): Promise<RPA.Atom> {
    const abilityInfo = await getNewAtomDesc(key)

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
 * 原子能力的结构分成两部分：
 * 1. AtomMeta 原子能力的元数据，类型为 RPA.Flow.FlowItemValue
 * 2. AtomForm 原子能力的表单数据，类型为 RPA.Atom
 *
 * 将 AtomForm 合并到 AtomMeta 中
 */
export function mergeAtomFormToAtomMeta(atomMeta: RPA.Atom, atomForm: RPA.Flow.FlowItemValue): RPA.Atom {
  const processStore = useProcessStore()

  const mergeValue = (target: RPA.AtomDisplayItem[], origin: RPA.AtomDisplayItem[]) => {
    if (isEmpty(target)) {
      return []
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

  const mergeException = (origin: RPA.AtomDisplayItem[]): RPA.AtomDisplayItem[] => {
    const target = cloneDeep(processStore.commonAdvancedParameter).filter(item => exceptionKeys.includes(item.key))
    const result = isEmpty(origin) ? target : origin
    return mergeValue(target, result)
  }

  const mergeAdvanced = (origin: RPA.AtomDisplayItem[]): RPA.AtomDisplayItem[] => {
    const target = cloneDeep(processStore.commonAdvancedParameter).filter(item => !exceptionKeys.includes(item.key))
    const result = isEmpty(origin) ? target : origin
    return mergeValue(target, result)
  }

  const advanced = mergeAdvanced(atomForm.advanced);
  const inputList = mergeValue(atomMeta.inputList, atomForm.inputList);

  // 从 inputList 中筛选出高级参数（level = 'advanced'）
  const advancedFromInputList = inputList.filter(item => item.level === 'advanced');
  // 从 inputList 中移除高级参数
  const filteredInputList = inputList.filter(item => item.level !== 'advanced');
  // 将高级参数添加到 advanced 列表中
  const finalAdvanced = [...advancedFromInputList, ...advanced];

  return {
    ...atomMeta,
    id: atomForm.id,
    alias: atomForm.alias,
    advanced: finalAdvanced,
    exception: mergeException(atomForm.exception),
    inputList: filteredInputList,
    outputList: mergeValue(atomMeta.outputList, atomForm.outputList),
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
