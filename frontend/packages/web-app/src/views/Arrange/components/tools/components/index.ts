import { NiceModal } from '@rpa/components'

import _ContractEleModal from './ContractEleModal.vue'
import _ContractValidateModal from './ContractValidateModal.vue'
import _EmailTextReplaceModal from './EmailTextReplaceModal.vue'
import _TextareaModal from './TextareaModal.vue'

export const TextareaModal = NiceModal.create(_TextareaModal)
export const EmailTextReplaceModal = NiceModal.create(_EmailTextReplaceModal)
export const ContractValidateModal = NiceModal.create(_ContractValidateModal)
export const ContractEleModal = NiceModal.create(_ContractEleModal)
