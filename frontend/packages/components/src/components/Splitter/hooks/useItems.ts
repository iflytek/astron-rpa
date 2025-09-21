import { computed, useSlots } from 'vue'
import type { VNode } from 'vue'

import type { PanelProps } from '../interface'

function getCollapsible(collapsible?: PanelProps['collapsible']) {
  if (collapsible && typeof collapsible === 'object') {
    return collapsible
  }

  const mergedCollapsible = !!collapsible

  return {
    start: mergedCollapsible,
    end: mergedCollapsible,
  }
}

export type ItemType = Omit<PanelProps, 'collapsible'> & {
  node: VNode
  collapsible: {
    start?: boolean
    end?: boolean
  }
}

export default function useItems() {
  const slots = useSlots()

  const items = computed<ItemType[]>(() => {
    const children = slots.default?.() || []

    return children
      .filter((node): node is VNode => !!node?.type)
      .map((node) => {
        const { collapsible, ...restProps } = (node.props || {}) as PanelProps

        return {
          ...restProps,
          collapsible: getCollapsible(collapsible),
          node,
        }
      })
  })

  return items
}
