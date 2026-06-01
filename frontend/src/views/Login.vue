<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">📁 智能文件/书签管理系统</h1>
      <h2 class="login-subtitle">用户登录</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="用户名/邮箱" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名或邮箱" size="large" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large"
            show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="handleLogin" style="width: 100%">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <p class="login-footer">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名或邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.login(form)
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch { /* 拦截器已处理 */ }
  finally { loading.value = false }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}
.login-title {
  text-align: center;
  font-size: 22px;
  margin-bottom: 6px;
  color: #303133;
}
.login-subtitle {
  text-align: center;
  font-size: 14px;
  font-weight: normal;
  color: #909399;
  margin-bottom: 30px;
}
.login-footer {
  text-align: center;
  margin-top: 16px;
  color: #909399;
  font-size: 14px;
}
</style>
