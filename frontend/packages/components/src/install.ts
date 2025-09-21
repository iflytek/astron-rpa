import type { App } from 'vue'

import { HintIcon, Icon } from './index'

export default (app: App) => {
  app.component('rpa-icon', Icon)
  app.component('rpa-hint-icon', HintIcon)
}
