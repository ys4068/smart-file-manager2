import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { noAuth: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { noAuth: true },
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘' },
      },
      {
        path: 'files',
        name: 'Files',
        component: () => import('@/views/Files.vue'),
        meta: { title: '文件管理' },
      },
      {
        path: 'bookmarks',
        name: 'Bookmarks',
        component: () => import('@/views/Bookmarks.vue'),
        meta: { title: '书签管理' },
      },
      {
        path: 'tags',
        name: 'Tags',
        component: () => import('@/views/Tags.vue'),
        meta: { title: '标签管理' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (!to.meta.noAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
