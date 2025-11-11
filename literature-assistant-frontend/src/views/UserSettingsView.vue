<template>
  <div class="settings-container">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <h2>用户设置</h2>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <!-- 基本信息 -->
        <el-tab-pane label="基本信息" name="basic">
          <el-form
            ref="basicFormRef"
            :model="basicForm"
            :rules="basicRules"
            label-width="120px"
          >
            <el-form-item label="用户名">
              <el-input v-model="userStore.user.username" disabled />
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input
                v-model="basicForm.email"
                placeholder="请输入邮箱"
                clearable
              />
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                :loading="userStore.loading"
                @click="handleUpdateBasicInfo"
              >
                保存
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 修改密码 -->
        <el-tab-pane label="修改密码" name="password">
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="120px"
          >
            <el-form-item label="新密码" prop="password">
              <el-input
                v-model="passwordForm.password"
                type="password"
                placeholder="请输入新密码"
                show-password
                clearable
              />
            </el-form-item>
            
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                placeholder="请再次输入新密码"
                show-password
                clearable
              />
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                :loading="userStore.loading"
                @click="handleUpdatePassword"
              >
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/userStore'

const userStore = useUserStore()

const activeTab = ref('basic')
const basicFormRef = ref(null)
const passwordFormRef = ref(null)
const aiFormRef = ref(null)

const basicForm = reactive({
  email: ''
})

const passwordForm = reactive({
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const basicRules = reactive({
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
})

const passwordRules = reactive({
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
})

const loadUserData = () => {
  if (userStore.user) {
    basicForm.email = userStore.user.email
  }
}

const handleUpdateBasicInfo = async () => {
  try {
    await basicFormRef.value.validate()
    await userStore.updateUserInfo({ email: basicForm.email })
    ElMessage.success('基本信息更新成功')
  } catch (error) {
    if (error.message) {
      ElMessage.error(error.message)
    }
  }
}

const handleUpdatePassword = async () => {
  try {
    await passwordFormRef.value.validate()
    await userStore.updateUserInfo({ password: passwordForm.password })
    ElMessage.success('密码修改成功')
    passwordFormRef.value.resetFields()
  } catch (error) {
    if (error.message) {
      ElMessage.error(error.message)
    }
  }
}

onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.settings-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px;
}

.settings-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.5;
}

.form-tip a {
  color: #409eff;
  text-decoration: none;
}

.form-tip a:hover {
  text-decoration: underline;
}

:deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>

