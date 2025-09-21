import { createApp } from 'vue'

import i18next from '@/plugins/i18next'
import '@/assets/css/default.css'
import '@/assets/css/main.scss'

import App from './App.vue'

const app = createApp(App)

app.use(i18next)
app.mount('#app')
