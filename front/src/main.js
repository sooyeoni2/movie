import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import 'bootstrap/dist/css/bootstrap.min.css'; // 부트스트랩 CSS 임포트
import 'bootstrap'; // 부트스트랩 JS 임포트

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
