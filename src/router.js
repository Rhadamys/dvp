import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

import Editor from './pages/Editor.vue'
import TestS1A from 'Tests/1/A/pages/Editor.vue'
import TestS1A from 'Tests/1/B/pages/Editor.vue'

const router = new VueRouter({
    mode: 'history',
    routes: [
        {
            path: '/',
            name: 'inicio',
            component: Editor,
        },
        {
            path:'/A',
            name: 'S1-A',
            component: TestS1A
        },
        {
            path:'/B',
            name: 'S1-B',
            component: TestS1A
        }
    ]
})

export { router }