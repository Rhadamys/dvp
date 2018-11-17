// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import axios from 'axios'
import { MdApp, MdButton, MdCard, MdContent, MdDivider, 
    MdDrawer, MdIcon, MdList, MdToolbar, MdTooltip } from 'vue-material/dist/components'
import 'vue-material/dist/vue-material.min.css'
require('@/assets/styles/app.scss')

Vue.use(MdApp)
Vue.use(MdButton)
Vue.use(MdCard)
Vue.use(MdContent)
Vue.use(MdDivider)
Vue.use(MdDrawer)
Vue.use(MdIcon)
Vue.use(MdList)
Vue.use(MdToolbar)
Vue.use(MdTooltip)

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
Vue.prototype.$http = axios

Vue.mixin({
    methods: {
        formData: function(object) {
            var fd = new FormData()
            for (var key in object)
                fd.append(key, object[key])
            return fd
        }
    }
})

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
