import { deleteAtomData } from '@/views/Arrange/components/flow/hooks/useFlow'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsDelete() {
  const item: ArrangeTools = {
    key: 'delete',
    title: 'delete',
    name: '',
    fontSize: '17',
    icon: 'icon-list-array-delete',
    action: '',
    clickFn: atomIds => deleteAtomData(atomIds),
  }
  return item
}
