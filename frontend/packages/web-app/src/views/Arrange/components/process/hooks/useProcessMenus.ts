import { NiceModal } from '@rpa/components'

import { useProcessStore } from '@/stores/useProcessStore'
import type { Fun } from '@/types/common'
import { ProcessModal } from '@/views/Arrange/components/process'
import { CATEGORY_MAP } from '@/views/Arrange/config/atom'

import type { IMenuItem } from '../DropdownMenu.vue'

export enum ProcessActionEnum {
  OPEN = 'open',
  RENAME = 'rename',
  DELETE = 'delete',
  SEARCH_CHILD_PROCESS = 'searchChildProcess',
  COPY = 'copy',
  CLOSE_ALL = 'closeAll',
}

interface Params {
  item: RPA.Process.ProcessModule;
  disabled?: Fun;
  actions: ProcessActionEnum[];
}

export function useProcessMenuActions(params: Params): IMenuItem[] {
  const { item, disabled, actions } = params
  const { canvasManager } = useProcessStore()

  const renameFn = () => {
    NiceModal.show(ProcessModal, { processItem: item, type: item.resourceCategory })
  }

  const menus: IMenuItem[] = [
    { key: ProcessActionEnum.OPEN, name: '打开', fn: () => canvasManager.activateTab(item.resourceId) },
    { key: ProcessActionEnum.RENAME, name: '重命名', fn: renameFn },
    // { key: ProcessActionEnum.DELETE, name: '删除', fn: () => useProjectDocStore().removeProcessOrModule(item) },
    // { key: ProcessActionEnum.COPY, name: `复制${CATEGORY_MAP[item.resourceCategory]}`, fn: () => useProjectDocStore().copyProcessOrModule(item.resourceCategory, item.resourceId) },
    // { key: ProcessActionEnum.SEARCH_CHILD_PROCESS, name: `查找${CATEGORY_MAP[item.resourceCategory]}使用情况`, fn: () => processStore.searchSubProcess(item.resourceId) },
    // { key: ProcessActionEnum.CLOSE_ALL, name: '关闭所有子流程', fn: () => processStore.closeAllChildProcess() },
  ]

  return menus.filter(item => actions.includes(item.key as ProcessActionEnum)).map(item => ({ ...item, disabled: disabled(item.key) }))
}
