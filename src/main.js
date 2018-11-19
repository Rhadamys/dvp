// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import axios from 'axios'
import VueMaterial from 'vue-material'
import 'vue-material/dist/vue-material.min.css'
require('@/assets/styles/base.scss')
require('@/assets/styles/app.scss')

Vue.use(VueMaterial)

// Encabezados CSRF Token
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
// Axios por defecto para requests
Vue.prototype.$http = axios

// Formato de fechas
Date.prototype.toString = function() {
    const day = this.getDate()
    const month = this.getMonth() + 1
    const year = this.getFullYear()
    const hours = this.getHours()
    const mins = this.getMinutes()
    return day + '/' + month + '/' + year + ' ' + (hours < 10 ? '0': '') + hours + ':' + (mins < 10 ? '0': '') + mins
}

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
new Vue({
    el: '#app',
    router,
    components: { App },
    template: '<App/>'
})
