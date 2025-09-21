import { createPinia } from 'pinia'
import { createApp } from 'vue'

import i18next from '@/plugins/i18next'

// 导入默认事件处理
import '@/utils/event'
import '@/assets/css/default.css'

import Index from './Index.vue'

const app = createApp(Index)

app.use(createPinia())
app.use(i18next)
app.mount('#app-batch')
