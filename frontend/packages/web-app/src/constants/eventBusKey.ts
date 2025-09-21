import type { EventBusKey } from '@vueuse/core'

export const updateSimpleFlowUIDataByIndexKey = Symbol('symbol-key') as EventBusKey<number>
export const showTriggerInputKey = Symbol('symbol-key')
export const atomScrollIntoViewKey = Symbol('symbol-key') as EventBusKey<string | number>
