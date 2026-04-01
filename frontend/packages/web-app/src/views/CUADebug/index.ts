import { createPinia } from 'pinia'
import { createApp } from 'vue'

import i18next from '@/plugins/i18next'
import http from '@/api/http'
import router from '@/router/index'
import '@/assets/css/default.css'
import '@/assets/css/main.scss'
import '@/utils/event'

import Index from './Index.vue'

http.init()
http.resolveReadyPromise()

const app = createApp(Index)
app.use(createPinia())
app.use(i18next)
app.use(router)
app.mount('#app')
