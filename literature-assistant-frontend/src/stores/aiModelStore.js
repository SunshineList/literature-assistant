import { defineStore } from 'pinia'
import request from '@/utils/request'

export const useAIModelStore = defineStore('aiModel', {
  state: () => ({
    models: [],
    defaultModel: null,
    loading: false,
    error: null
  }),
  
  getters: {
    hasModels: (state) => state.models.length > 0,
    enabledModels: (state) => state.models.filter(m => m.status === 1)
  },
  
  actions: {
    // 获取所有AI模型
    async fetchModels() {
      this.loading = true
      this.error = null
      
      try {
        const response = await request.get('/ai-models')
        
        if (response.data.success) {
          this.models = response.data.data || []
          // 找出默认模型
          this.defaultModel = this.models.find(m => m.isDefault === 1)
          return true
        } else {
          throw new Error(response.data.message || '获取AI模型列表失败')
        }
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '获取AI模型列表失败'
        console.error('获取AI模型列表失败:', error)
        return false
      } finally {
        this.loading = false
      }
    },
    
    // 获取默认AI模型
    async fetchDefaultModel() {
      try {
        const response = await request.get('/ai-models/default')
        
        if (response.data.success) {
          this.defaultModel = response.data.data
          return this.defaultModel
        }
        return null
      } catch (error) {
        console.error('获取默认AI模型失败:', error)
        return null
      }
    },
    
    // 创建AI模型
    async createModel(data) {
      this.loading = true
      this.error = null
      
      try {
        const response = await request.post('/ai-models', data)
        
        if (response.data.success) {
          await this.fetchModels()
          return true
        } else {
          throw new Error(response.data.message || '创建AI模型失败')
        }
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '创建AI模型失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 更新AI模型
    async updateModel(id, data) {
      this.loading = true
      this.error = null
      
      try {
        const response = await request.put(`/ai-models/${id}`, data)
        
        if (response.data.success) {
          await this.fetchModels()
          return true
        } else {
          throw new Error(response.data.message || '更新AI模型失败')
        }
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '更新AI模型失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 删除AI模型
    async deleteModel(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await request.delete(`/ai-models/${id}`)
        
        if (response.data.success) {
          await this.fetchModels()
          return true
        } else {
          throw new Error(response.data.message || '删除AI模型失败')
        }
      } catch (error) {
        this.error = error.response?.data?.message || error.message || '删除AI模型失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 清除错误
    clearError() {
      this.error = null
    }
  }
})

