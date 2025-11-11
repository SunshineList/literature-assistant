<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 顶部导航栏 -->
      <el-header v-if="!isLoginPage" class="app-header">
        <div class="header-content">
          <div class="title-section">
            <h1 class="app-title" @click="$router.push('/')">
              <img src="/logo.png" alt="Logo" class="app-logo" />
              文档管理助手
            </h1>
          </div>
          
          <div v-if="userStore.isLoggedIn" class="user-section">
            <span class="username">{{ userStore.username }}</span>
            <el-dropdown @command="handleCommand">
              <el-button type="primary" text>
                <el-icon><UserFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="ai-models">
                    <el-icon><Setting /></el-icon>
                    AI模型管理
                  </el-dropdown-item>
                  <el-dropdown-item command="settings">
                    <el-icon><User /></el-icon>
                    用户设置
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <!-- 主内容区域 -->
      <el-main class="app-main" :class="{ 'no-header': isLoginPage }">
        <ErrorBoundary>
          <router-view />
        </ErrorBoundary>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { UserFilled, Setting, SwitchButton, User } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/userStore'
import ErrorBoundary from './components/ErrorBoundary.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isLoginPage = computed(() => route.path === '/login')

const handleCommand = async (command) => {
  if (command === 'ai-models') {
    router.push('/ai-models')
  } else if (command === 'settings') {
    router.push('/settings')
  } else if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      userStore.logout()
      router.push('/login')
    } catch (error) {
      // 用户取消
    }
  }
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
}

.app-header {
  background: #ffffff;
  color: #333333;
  display: flex;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.08);
  border-bottom: 1px solid #e5e7eb;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app-logo {
  height: 32px;
  width: auto;
}

.app-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: #333333;
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.app-title:hover {
  opacity: 0.8;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.app-main {
  background-color: #f5f7fa;
  padding: 24px;
  min-height: calc(100vh - 60px);
}

.app-main.no-header {
  min-height: 100vh;
  padding: 0;
}
</style>
