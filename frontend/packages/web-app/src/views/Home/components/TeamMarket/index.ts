import { NiceModal } from '@rpa/components'

import _DeployRobotModal from './DeployRobotModal.vue'
import _MarketAchieveModal from './MarketAchieveModal.vue'
import _VersionPushModal from './VersionPushModal.vue'

export const DeployRobotModal = NiceModal.create(_DeployRobotModal)
export const MarketAchieveModal = NiceModal.create(_MarketAchieveModal)
export const VersionPushModal = NiceModal.create(_VersionPushModal)
