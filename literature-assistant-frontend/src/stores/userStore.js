import { defineStore } from 'pinia'
import request from '@/utils/request'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token && !!state.user,
    username: (state) => state.user?.username || '',
    email: (state) => state.user?.email || '',
    aiProvider: (state) => state.user?.aiProvider || 'ollama',
    ollamaBaseUrl: (state) => state.user?.ollamaBaseUrl || '',
    ollamaModel: (state) => state.user?.ollamaModel || '',
    kimiApiKey: (state) => state.user?.kimiApiKey || ''
  },
  
  actions: {
    // 设置认证token
    setToken(token) {
      this.token = token
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    },
    
    // 用户注册
    async register(username, email, password) {
      this.loading = true
      this.error = null
      
      try {
        const response = await request.post('/user/register', {
          username,
          email,
          password
        })
        
        if (response.data.success) {
          return true
        } else {
          throw new Error(response.data.message || '注册失败')
        }
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '注册失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 用户登录
    async login(username, password) {
      this.loading = true
      this.error = null
      
      try {
        const response = await request.post('/user/login', {
          username,
          password
        })
        
        if (response.data.success) {
          const { token, user } = response.data.data
          this.setToken(token)
          this.user = user
          return true
        } else {
          throw new Error(response.data.message || '登录失败')
        }
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '登录失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 获取当前用户信息
    async fetchUserInfo() {
      if (!this.token) {
        return false
      }
      
      this.loading = true
      this.error = null
      
      try {
        const response = await request.get('/user/me')
        
        if (response.data.success) {
          this.user = response.data.data
          return true
        } else {
          throw new Error(response.data.message || '获取用户信息失败')
        }
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '获取用户信息失败'
        // 如果token无效，清除登录状态
        if (error.response?.status === 401) {
          this.logout()
        }
        return false
      } finally {
        this.loading = false
      }
    },
    
    // 更新用户信息
    async updateUserInfo(data) {
      this.loading = true
      this.error = null
      
      try {
        const response = await request.put('/user/me', data)
        
        if (response.data.success) {
          this.user = response.data.data
          return true
        } else {
          throw new Error(response.data.message || '更新用户信息失败')
        }
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '更新用户信息失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 用户登出
    logout() {
      this.user = null
      this.setToken(null)
      this.error = null
    },
    
    // 清除错误
    clearError() {
      this.error = null
    }
  }
})

