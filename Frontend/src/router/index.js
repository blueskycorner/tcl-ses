import Vue from 'vue'
import Router from 'vue-router'
import store from '../store'
// import HelloWorld from '@/components/HelloWorld'
import login from '@/components/login'
import tcl from '@/components/tcl'

Vue.use(Router)

// let entryUrl = null

const guardTcl = async (to, from, next) => {
  if (store.state.signedIn) {
    next()
  } else {
    next('/login')
  }
}

const guardLogin = async (to, from, next) => {
  if (store.state.signedIn) {
    next('/tcl')
  } else {
    next()
  }
}

export default new Router({
  routes: [
    {
      path: '/',
      name: 'root',
      redirect: '/tcl'
    },
    {
      path: '/login',
      beforeEnter: guardLogin,
      name: 'login',
      component: login
    },
    {
      path: '/tcl',
      beforeEnter: guardTcl,
      name: 'tcl',
      component: tcl
    }
  ]
})
