import { NiceModal } from '@rpa/components'

import { CustomComponentSettingModal } from '@/components/CustomComponentSetting'
import { useProcessStore } from '@/stores/useProcessStore'
import type { ArrangeTools } from '@/views/Arrange/types/arrangeTools'

export function useToolsCustomComp() {
  const className = '_tools-custom-comp-setting'

  const settingModal = NiceModal.useModal(CustomComponentSettingModal)

  const item: ArrangeTools = {
    key: 'customComponentSetting',
    title: 'components.customComponentSetting',
    name: 'components.customComponentSetting',
    fontSize: '',
    icon: 'tools-custom-comp-setting',
    class: className,
    action: '',
    loading: false,
    show: () => useProcessStore().isComponent,
    disable: () => !useProcessStore().isComponent,
    clickFn: () => {
      settingModal.visible ? settingModal.hide() : settingModal.show({ clickOutsideIgnoreSelector: className })
    },
  }

  return item
}
