import { createPinia } from 'pinia'
import { createApp } from 'vue'

// 样式导入
import '@/assets/css/default.css'
import '@/assets/css/main.scss'

// 插件导入
import i18next from '@/plugins/i18next'
import sentry from '@/plugins/sentry'

// 工具导入
import '@/utils/event'

// 路由导入
import router from '@/router/index'

// 组件导入
import App from './App.vue'
import '@/auth/index'

const app = createApp(App)

app.use(createPinia())
app.use(sentry)
app.use(i18next)
app.use(router)

app.mount('#app')
