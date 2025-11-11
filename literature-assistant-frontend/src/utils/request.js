/**
 * Axios 请求配置
 * 统一处理请求拦截、响应拦截、错误处理
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建axios实例
const request = axios.create({
  baseURL: '/api',
  timeout: 60000, // 60秒超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从localStorage获取最新的token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    // 如果是FormData，让浏览器自动设置Content-Type
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('响应错误:', error)
    
    // 处理网络错误
    if (!error.response) {
      ElMessage.error('网络连接失败，请检查网络设置')
      return Promise.reject(error)
    }
    
    const { status, data } = error.response
    console.log(status, data)
    
    // 处理各种HTTP状态码
    switch (status) {
      case 401:
        // 未授权，清除token并跳转到登录页
        ElMessage.error(data?.message || '登录已过期，请重新登录')
        localStorage.removeItem('token')
        delete axios.defaults.headers.common['Authorization']
        
        // 避免重复跳转
        if (router.currentRoute.value.path !== '/login') {
          router.push('/login')
        }
        break
        
      case 403:
        ElMessage.error(data?.message || '没有权限访问')
        break
        
      case 404:
        ElMessage.error(data?.message || '请求的资源不存在')
        break
        
      case 500:
        ElMessage.error(data?.message || '服务器错误，请稍后重试')
        break
        
      default:
        ElMessage.error(data?.message || `请求失败 (${status})`)
    }
    
    return Promise.reject(error)
  }
)

export default request

