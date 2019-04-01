import Vue from 'vue'
import Router from 'vue-router'
import store from '../store'
import HelloWorld from '@/components/HelloWorld'
import login from '@/components/login'
import tcl from '@/components/tcl'

Vue.use(Router)

let entryUrl = null

const guard = async (to, from, next) => {
  if (store.state.signedIn) {
    if (entryUrl) {
      const url = entryUrl
      entryUrl = null
      return next(url) // goto stored url
    } else {
      return next() // all is fine
    }
  }

  await store.dispatch('checkAuth')
  // we use await as this async request has to finish
  // before we can be sure

  if (store.state.signedIn) {
    next()
  } else {
    entryUrl = to.path // store entry url before redirect
    next('/login')
  }
}

export default new Router({
  routes: [
    {
      path: '/',
      name: 'HelloWorld',
      component: HelloWorld
    },
    {
      path: '/login',
      name: 'login',
      component: login
    },
    {
      path: '/tcl',
      beforeEnter: guard,
      name: 'tcl',
      component: tcl
    }
  ]
})
