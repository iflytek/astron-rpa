import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsKeyManagement() {
  const backToMain = () => {}
  const item: ArrangeTools = {
    key: 'keyManagement',
    title: 'keyManagement',
    name: 'keyManagement',
    fontSize: '',
    icon: 'icon-key',
    action: '',
    loading: false,
    show: true,
    disable: false,
    clickFn: backToMain,
  }
  return item
}
