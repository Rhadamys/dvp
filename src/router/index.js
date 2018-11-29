import Vue from 'vue'
import Router from 'vue-router'

import Editor from '@/pages/Editor'
import NotFound from '@/pages/NotFound'

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
      path: "*",
      component: NotFound,
    }
  ],
  scrollBehavior: (to) => {
    console.log(to)
    if (to.hash) {
      VueScrollTo.scrollTo(to.hash, 700);
      return {
        selector: to.hash,
        offset: { x: 0, y: 50 },
      }
    }
    return { x: 0, y: 0 }
  },
})
