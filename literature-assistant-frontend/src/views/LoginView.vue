<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <img src="/logo.png" alt="Logo" class="logo" />
        <h1 class="title">文档管理助手</h1>
        <p class="subtitle">{{ isLogin ? '欢迎回来' : '创建新账号' }}</p>
      </div>
      
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleSubmit"
        class="login-form"
        @keydown.enter.native="handleSubmit"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="formData.username"
            placeholder="请输入用户名"
            clearable
          />
        </el-form-item>
        
        <el-form-item v-if="!isLogin" label="邮箱" prop="email">
          <el-input
            v-model="formData.email"
            type="email"
            placeholder="请输入邮箱"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item v-if="!isLogin" label="确认密码" prop="confirmPassword">
          <el-input
            v-model="formData.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item class="submit-button">
          <el-button
            type="primary"
            :loading="userStore.loading"
            @click="handleSubmit"
            size="large"
            class="login-button"
          >
            {{ isLogin ? '登录' : '注册' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="toggle-mode">
        <span class="toggle-text">{{ isLogin ? '还没有账号？' : '已有账号？' }}</span>
        <el-button
          link
          type="primary"
          @click="toggleMode"
          class="toggle-button"
        >
          {{ isLogin ? '立即注册' : '立即登录' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/userStore'

const router = useRouter()
const userStore = useUserStore()

const isLogin = ref(true)
const formRef = ref(null)

const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== formData.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = reactive({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
})

const toggleMode = () => {
  isLogin.value = !isLogin.value
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    if (isLogin.value) {
      // 登录
      await userStore.login(formData.username, formData.password)
      ElMessage.success('登录成功')
      router.push('/')
    } else {
      // 注册
      await userStore.register(formData.username, formData.email, formData.password)
      ElMessage.success('注册成功，请登录')
      isLogin.value = true
      formRef.value?.resetFields()
    }
  } catch (error) {
    ElMessage.error(error.message || (isLogin.value ? '登录失败' : '注册失败'))
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: moveBackground 20s linear infinite;
}

@keyframes moveBackground {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(50px, 50px);
  }
}

.login-box {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  position: relative;
  z-index: 1;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.title {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.login-form {
  margin-bottom: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.submit-button {
  margin-top: 24px;
  margin-bottom: 0;
}

.login-button {
  width: 100%;
  height: 44px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.login-button:active {
  transform: translateY(0);
}

.toggle-mode {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.toggle-text {
  font-size: 14px;
  color: #606266;
  margin-right: 8px;
}

.toggle-button {
  font-size: 14px;
  font-weight: 600;
}

.toggle-button:hover {
  text-decoration: underline;
}
</style>

