import type { App } from 'vue'

import { HintIcon, Icon, StarMotion } from './index'

export default (app: App) => {
  app.component('rpa-icon', Icon)
  app.component('rpa-hint-icon', HintIcon)
  app.component('rpa-star-motion', StarMotion)
}
