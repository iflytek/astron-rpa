import { NiceModal } from '@rpa/components'

import _PublishDetail from './PublishDetail.vue'
import _PublishModal from './PublishModal.vue'

export const ComponentPublishModal = NiceModal.create(_PublishModal)
export const ComponentPublishDetail = NiceModal.create(_PublishDetail)
