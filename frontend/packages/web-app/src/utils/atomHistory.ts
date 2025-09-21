import { LRUCache } from './lruCache'

const ATOM_USAGE_HISTORY_KEY = 'atom_usage_history'

interface AtomUsageRecord {
  key: string
  title: string
  icon?: string
  parentKey?: string
  timestamp?: number
}

// 创建LRU缓存实例，最多保存50条记录
const atomHistoryCache = new LRUCache<AtomUsageRecord[]>(ATOM_USAGE_HISTORY_KEY, 50, [])

export function recordAtomUsage(atom: {
  key: string
  title: string
  icon?: string
  parentKey?: string
}) {
  try {
    const currentHistory = atomHistoryCache.get('history') || []
    const newRecord: AtomUsageRecord = {
      ...atom,
      timestamp: Date.now(),
    }
    const filteredHistory = currentHistory.filter(item => item.key !== atom.key)
    const updatedHistory = [newRecord, ...filteredHistory]
    atomHistoryCache.set('history', updatedHistory)
  }
  catch (error) {
    console.error('Failed to record atom usage:', error)
  }
}

/**
 * 获取最近使用的原子能力列表
 * @param limit 返回的记录数量限制，默认5条
 * @returns 最近使用的原子能力列表
 */
export function getRecentAtomUsage(limit: number = 5): AtomUsageRecord[] {
  try {
    const history = atomHistoryCache.get('history') || []
    return history.slice(0, limit)
  }
  catch (error) {
    console.error('Failed to get recent atom usage:', error)
    return []
  }
}

/**
 * 清除原子能力使用历史
 */
export function clearAtomUsageHistory() {
  try {
    atomHistoryCache.set('history', [])
  }
  catch (error) {
    console.error('Failed to clear atom usage history:', error)
  }
}
