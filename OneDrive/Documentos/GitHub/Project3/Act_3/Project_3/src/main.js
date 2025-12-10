import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { inject } from "@vercel/analytics"
import App from './App.vue'
import router from './router'
import './main.css'

inject()

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.mount('#app')
