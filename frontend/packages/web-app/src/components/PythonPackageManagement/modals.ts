import { NiceModal } from '@rpa/components'

import _PythonInstallModal from './components/PythonInstallModal.vue'
import _PythonLoadingModal from './components/PythonLoadingModal.vue'

export const pythonInstallModal = NiceModal.useModal(NiceModal.create(_PythonInstallModal))

export const PythonLoadingModal = NiceModal.create(_PythonLoadingModal)
