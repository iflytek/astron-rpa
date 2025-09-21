import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsSaveTemplate() {
  const handleVersionDuplicate = () => {}
  const item: ArrangeTools = {
    key: 'saveAsTemplate',
    title: 'saveAsTemplate',
    name: 'saveAsTemplate',
    fontSize: '16',
    icon: 'icon-icon-saveTemplate',
    action: 'design_cloud_pj_tmp',
    loading: false,
    show: true,
    disable: false,
    clickFn: handleVersionDuplicate,
  }
  return item
}
