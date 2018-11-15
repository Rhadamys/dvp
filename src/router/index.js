import Vue from 'vue'
import Router from 'vue-router'

import Editor from '@/pages/Editor.vue'
import TestS1A from '%/1/A/pages/Editor.vue'
import TestS1B from '%/1/B/pages/Editor.vue'

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
        component: TestS1A
    },
    {
        path:'/B',
        name: 'S1-B',
        component: TestS1B
    }
  ]
})
