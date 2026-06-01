import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api/modules'

export const useUserStore = defineStore('user', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const token = ref(localStorage.getItem('access_token') || '')

  const isLoggedIn = computed(() => !!token.value)

  async function login(credentials) {
    const res = await authAPI.login(credentials)
    if (res.code === 200) {
      user.value = res.data.user
      token.value = res.data.access_token
      localStorage.setItem('user', JSON.stringify(res.data.user))
      localStorage.setItem('access_token', res.data.access_token)
      localStorage.setItem('refresh_token', res.data.refresh_token)
    }
    return res
  }

  async function register(data) {
    const res = await authAPI.register(data)
    if (res.code === 200) {
      user.value = res.data.user
      token.value = res.data.access_token
      localStorage.setItem('user', JSON.stringify(res.data.user))
      localStorage.setItem('access_token', res.data.access_token)
      localStorage.setItem('refresh_token', res.data.refresh_token)
    }
    return res
  }

  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('user')
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, token, isLoggedIn, login, register, logout }
})
