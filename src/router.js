import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

import Editor from './pages/Editor.vue'

const router = new VueRouter({
    mode: 'history',
    routes: [
        {
            path: '/',
            name: 'inicio',
            component: Editor,
        },
    ]
})

export { router }