<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <span class="logo-icon">📁</span>
        <span class="logo-text">智能管理</span>
      </div>
      <el-menu :default-active="activeMenu" router :collapse="false" class="sidebar-menu">
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/files">
          <el-icon><FolderOpened /></el-icon>
          <span>文件管理</span>
        </el-menu-item>
        <el-menu-item index="/bookmarks">
          <el-icon><Collection /></el-icon>
          <span>书签管理</span>
        </el-menu-item>
        <el-menu-item index="/tags">
          <el-icon><PriceTag /></el-icon>
          <span>标签管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <div class="main-area">
      <el-header class="topbar">
        <div class="topbar-left">
          <h3>{{ $route.meta.title || '仪表盘' }}</h3>
        </div>
        <div class="topbar-right">
          <el-dropdown trigger="click">
            <span class="user-info">
              <el-avatar :size="32" icon="UserFilled" />
              <span class="username">{{ userStore.user?.username || '用户' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <div class="content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}
.sidebar {
  background: #304156;
  color: #fff;
  overflow-y: auto;
  flex-shrink: 0;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.logo-icon { font-size: 24px; }
.logo-text { font-size: 16px; font-weight: 600; }
.sidebar-menu {
  border-right: none;
  background: transparent;
}
.sidebar-menu .el-menu-item {
  color: #bfcbd9;
}
.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-menu-item.is-active {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.topbar {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 24px;
}
.topbar-left h3 {
  margin: 0;
  font-size: 18px;
}
.topbar-right {
  display: flex;
  align-items: center;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}
.user-info:hover { background: #f5f7fa; }
.content {
  flex: 1;
  padding: 20px 24px;
  overflow-y: auto;
  background: #f0f2f5;
}
</style>
