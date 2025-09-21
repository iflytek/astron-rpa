import { useModal } from './hooks'
import { Provider } from './Provider'
import { antdDrawer, antdModal, create, hide, register, remove, show, unregister } from './utils'

export const NiceModal = { useModal, Provider, create, hide, register, remove, show, unregister, antdModal, antdDrawer }

export type { NiceModalAction, NiceModalState, NiceModalStore } from './store'
