import { createApp } from 'vue'
import App from './App.vue'
import router from './router/router'
import './style.css'

;(function initTheme() {
  const root = document.documentElement
  const stored = localStorage.getItem('agicomm-theme')
  if (stored === 'light') root.classList.remove('dark')
  else if (stored === 'dark') root.classList.add('dark')
  else root.classList.add('dark')
})()

const app = createApp(App)
app.use(router)
app.mount('#app')