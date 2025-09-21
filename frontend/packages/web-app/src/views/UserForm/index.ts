import { createPinia } from 'pinia'
import { createApp } from 'vue'

import i18next from '@/plugins/i18next'
import '@/assets/css/default.css'

import '@/utils/event'

import Index from './Index.vue'

const app = createApp(Index)
app.use(createPinia())

app.use(i18next)
app.mount('#user-form')
