import { paste } from '@/views/Arrange/components/flow/hooks/useFlow'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsPaste() {
  const item: ArrangeTools = {
    key: 'paste',
    title: 'paste',
    name: '',
    fontSize: '',
    icon: 'icon-paste',
    action: '',
    disable: ({ multiSelect }) => multiSelect,
    clickFn: paste,
  }
  return item
}
