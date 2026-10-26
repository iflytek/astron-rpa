import globalLoading from '@/utils/globalLoading'

import { GlobalLoadingTracker } from './loadingTracker'

export { shouldTrackGlobalLoading } from './loadingTracker'

export const globalLoadingTracker = new GlobalLoadingTracker(
  () => globalLoading.open({}),
  () => globalLoading.close(),
)
