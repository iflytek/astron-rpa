import { NiceModal } from '@rpa/components'

import _MailModal from './Index.vue'
import _MailListModal from './MailListModal.vue'

export const MailListModal = NiceModal.create(_MailListModal)
export const MailModal = NiceModal.create(_MailModal)
