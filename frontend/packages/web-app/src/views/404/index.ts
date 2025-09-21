import { createApp } from 'vue'

import i18next from '@/plugins/i18next'
import '@/assets/css/default.css'

import Index from './Index.vue'

const app = createApp(Index)

app.use(i18next)
app.mount('#app-404')
