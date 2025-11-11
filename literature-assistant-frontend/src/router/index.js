import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import LiteratureListView from '@/views/LiteratureListView.vue'
import LiteratureDetailView from '@/views/LiteratureDetailView.vue'
import LoginView from '@/views/LoginView.vue'
import UserSettingsView from '@/views/UserSettingsView.vue'
import AIModelManageView from '@/views/AIModelManageView.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/',
    name: 'LiteratureList',
    component: LiteratureListView,
    meta: {
      title: '文献列表',
      requiresAuth: true
    }
  },
  {
    path: '/literature/:id',
    name: 'LiteratureDetail',
    component: LiteratureDetailView,
    meta: {
      title: '文献详情',
      requiresAuth: true
    }
  },
  {
    path: '/settings',
    name: 'UserSettings',
    component: UserSettingsView,
    meta: {
      title: '用户设置',
      requiresAuth: true
    }
  },
  {
    path: '/ai-models',
    name: 'AIModelManage',
    component: AIModelManageView,
    meta: {
      title: 'AI模型管理',
      requiresAuth: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 文档管理助手`
  }
  
  const userStore = useUserStore()
  
  // 如果需要认证
  if (to.meta.requiresAuth) {
    // 检查是否已登录
    if (!userStore.token) {
      next('/login')
      return
    }
    
    // 如果有token但没有用户信息，尝试获取
    if (!userStore.user) {
      try {
        await userStore.fetchUserInfo()
      } catch (error) {
        console.error('获取用户信息失败:', error)
        next('/login')
        return
      }
    }
  }
  
  // 如果已登录且访问登录页，重定向到首页
  if (to.path === '/login' && userStore.token) {
    next('/')
    return
  }
  
  next()
})

export default router
