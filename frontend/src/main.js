import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Quasar, Notify, Dialog } from 'quasar'

// Import icon libraries
import '@quasar/extras/material-icons/material-icons.css'

// Import Quasar css
import 'quasar/src/css/index.sass'

// Assumes your root component is App.vue
// and placed in same folder as main.js
import App from './App.vue'
import router from './router'

const myApp = createApp(App)

myApp.use(createPinia())
myApp.use(router)
myApp.use(Quasar, {
  plugins: {
    Notify,
    Dialog
  }
})

// Assumes you have a <div id="app"></div> in your index.html
myApp.mount('#app')