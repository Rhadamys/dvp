import Vue from 'vue'
import { router } from './router'
import axios from 'axios'
import VueMaterial from 'vue-material'
import 'vue-material/dist/vue-material.min.css'
import './assets/app.scss'

Vue.use(VueMaterial);

import App from './App.vue'

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
new Vue({
    el: '#app',
    router,
    render: h => h(App)
})