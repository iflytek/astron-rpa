import { NiceModal } from '@rpa/components'

import _CopyModal from './CopyModal.vue'
import _LogModal from './LogModal.vue'
import _NewProjectModal from './NewProjectModal.vue'
import _RenameModal from './RenameModal.vue'
import _TaskReferInfoModal from './TaskReferInfoModal.vue'
import _VersionManagementModal from './VersionManagementModal/index.vue'

export const LogModal = NiceModal.create(_LogModal)
export const RenameModal = NiceModal.create(_RenameModal)
export const CopyModal = NiceModal.create(_CopyModal)
export const NewProjectModal = NiceModal.create(_NewProjectModal)
export const VersionManagementModal = NiceModal.create(_VersionManagementModal)
export const TaskReferInfoModal = NiceModal.create(_TaskReferInfoModal)

export const newProjectModal = NiceModal.useModal(NewProjectModal)
