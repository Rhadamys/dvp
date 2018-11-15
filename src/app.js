import Vue from 'vue'
import { router } from './router'
import axios from 'axios'
import { MdApp, MdButton, MdCard, MdContent, MdDivider, 
    MdDrawer, MdIcon, MdList, MdToolbar, MdTooltip } from 'vue-material/dist/components'
import 'vue-material/dist/vue-material.min.css'
import './assets/app.scss'
require("ace-builds/src-noconflict/mode-python")

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