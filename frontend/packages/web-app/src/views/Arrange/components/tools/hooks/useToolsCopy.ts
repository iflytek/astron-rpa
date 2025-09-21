import { copy } from '@/views/Arrange/components/flow/hooks/useFlow'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsCopy() {
  const item: ArrangeTools = {
    key: 'copy',
    title: 'copy',
    name: '',
    fontSize: '',
    icon: 'icon-copy',
    action: '',
    clickFn: atomIds => copy(atomIds),
  }
  return item
}
