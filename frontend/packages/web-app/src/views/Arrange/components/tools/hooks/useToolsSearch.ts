import Search from '@/views/Arrange/components/search/Index.vue'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsSearch() {
  const item: ArrangeTools = {
    key: 'search',
    title: '',
    name: '',
    icon: '',
    fontSize: '',
    action: '',
    clickFn: () => {},
    component: Search,
  }
  return item
}
