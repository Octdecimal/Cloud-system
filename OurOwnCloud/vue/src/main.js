import { createApp } from 'vue'
import App from './App.vue'
import api from './api.js'
import './assets/style.css'

console.log('>>> main.js 已執行')

const app = createApp(App)
app.provide('api', api)
app.mount('#app')
