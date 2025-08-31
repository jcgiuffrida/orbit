import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Quasar, Notify, Dialog } from 'quasar'
import HighchartsVue from 'highcharts-vue'

// Import icon libraries
import '@quasar/extras/material-icons/material-icons.css'

// Import Quasar css
import 'quasar/src/css/index.sass'

// Import Material Icons icon set
import iconSet from 'quasar/icon-set/material-icons'

// Assumes your root component is App.vue
// and placed in same folder as main.js
import App from './App.vue'
import router from './router'

const myApp = createApp(App)

myApp.use(createPinia())
myApp.use(router)
myApp.use(HighchartsVue)
myApp.use(Quasar, {
  plugins: {
    Notify,
    Dialog
  },
  config: {
    iconSet: iconSet
  }
})

// Assumes you have a <div id="app"></div> in your index.html
myApp.mount('#app')