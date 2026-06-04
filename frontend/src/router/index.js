import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/Login.vue"),
    meta: { title: "登录" },
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("@/views/Register.vue"),
    meta: { title: "注册" },
  },
  {
    path: "/",
    component: () => import("@/views/Layout.vue"),
    redirect: "/dashboard",
    children: [
      {
        path: "dashboard",
        name: "Dashboard",
        component: () => import("@/views/Dashboard.vue"),
        meta: { title: "仪表盘" },
      },
      {
        path: "files",
        name: "Files",
        component: () => import("@/views/Files.vue"),
        meta: { title: "文件管理" },
      },
      {
        path: "bookmarks",
        name: "Bookmarks",
        component: () => import("@/views/Bookmarks.vue"),
        meta: { title: "书签管理" },
      },
      {
        path: "search",
        name: "Search",
        component: () => import("@/views/Search.vue"),
        meta: { title: "智能搜索" },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  if (to.path !== "/login" && to.path !== "/register" && !token) {
    next("/login");
  } else {
    next();
  }
});

export default router;
