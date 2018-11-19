import Vue from 'vue'
import Router from 'vue-router'

import Editor from '@/pages/Editor.vue'

Vue.use(Router)

export default new Router({
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
        redirect: '/',
    },
    {
        path:'/B',
        name: 'S1-B',
        redirect: '/',
    }
  ]
})
