<template>
  <div class="ai-model-manage">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>AI模型管理</h2>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            添加模型
          </el-button>
        </div>
      </template>
      
      <el-alert
        v-if="aiModelStore.error"
        :title="aiModelStore.error"
        type="error"
        :closable="true"
        @close="aiModelStore.clearError()"
        class="mb-16"
      />
      
      <el-table
        :data="aiModelStore.models"
        :loading="aiModelStore.loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="模型名称" width="180" />
        
        <el-table-column prop="modelName" label="实际模型" width="180" />
        
        <el-table-column prop="baseUrl" label="API地址" min-width="250">
          <template #default="{ row }">
            <el-tooltip :content="row.baseUrl" placement="top">
              <div class="text-truncate">{{ row.baseUrl }}</div>
            </el-tooltip>
          </template>
        </el-table-column>
        
        <el-table-column prop="maxTokens" label="Max Tokens" width="120" align="center" />
        
        <el-table-column prop="isDefault" label="默认" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.isDefault === 1" type="success" size="small">是</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              v-if="row.isDefault !== 1"
              type="primary"
              link
              size="small"
              @click="setDefault(row)"
            >
              设为默认
            </el-button>
            <el-button
              type="primary"
              link
              size="small"
              @click="editModel(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              @click="deleteModel(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingModel ? '编辑AI模型' : '添加AI模型'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="formData.name" placeholder="例如：通义千问" />
        </el-form-item>
        
        <el-form-item label="API地址" prop="baseUrl">
          <el-input v-model="formData.baseUrl" placeholder="例如：https://dashscope.aliyuncs.com/compatible-mode/v1" />
          <div class="form-tip">OpenAI兼容的API地址</div>
        </el-form-item>
        
        <el-form-item label="API密钥" prop="apiKey">
          <el-input
            v-model="formData.apiKey"
            type="password"
            show-password
            placeholder="如果不需要可留空（如本地Ollama）"
          />
        </el-form-item>
        
        <el-form-item label="模型名称" prop="modelName">
          <el-input v-model="formData.modelName" placeholder="例如：qwen-plus" />
          <div class="form-tip">实际调用的模型名称</div>
        </el-form-item>
        
        <el-form-item label="Max Tokens" prop="maxTokens">
          <el-input-number v-model="formData.maxTokens" :min="1" :max="100000" />
        </el-form-item>
        
        <el-form-item label="Temperature" prop="temperature">
          <el-input v-model="formData.temperature" placeholder="0.0 - 2.0" />
          <div class="form-tip">控制输出的随机性，0-2之间</div>
        </el-form-item>
        
        <el-form-item label="设为默认">
          <el-switch v-model="formData.isDefault" />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="模型描述（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="aiModelStore.loading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useAIModelStore } from '@/stores/aiModelStore'

const aiModelStore = useAIModelStore()

const showCreateDialog = ref(false)
const editingModel = ref(null)
const formRef = ref(null)

const formData = reactive({
  name: '',
  baseUrl: '',
  apiKey: '',
  modelName: '',
  maxTokens: 4096,
  temperature: '0.7',
  isDefault: false,
  description: ''
})

const rules = reactive({
  name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  baseUrl: [
    { required: true, message: '请输入API地址', trigger: 'blur' }
  ],
  modelName: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  maxTokens: [
    { required: true, message: '请输入Max Tokens', trigger: 'blur' }
  ],
  temperature: [
    { required: true, message: '请输入Temperature', trigger: 'blur' }
  ]
})

const resetForm = () => {
  formData.name = ''
  formData.baseUrl = ''
  formData.apiKey = ''
  formData.modelName = ''
  formData.maxTokens = 4096
  formData.temperature = '0.7'
  formData.isDefault = false
  formData.description = ''
  editingModel.value = null
}

const editModel = (model) => {
  editingModel.value = model
  formData.name = model.name
  formData.baseUrl = model.baseUrl
  formData.apiKey = model.apiKey || ''
  formData.modelName = model.modelName
  formData.maxTokens = model.maxTokens
  formData.temperature = model.temperature
  formData.isDefault = model.isDefault === 1
  formData.description = model.description || ''
  showCreateDialog.value = true
}

const setDefault = async (model) => {
  try {
    await aiModelStore.updateModel(model.id, { isDefault: true })
    ElMessage.success('设置默认模型成功')
  } catch (error) {
    ElMessage.error(error.message || '设置默认模型失败')
  }
}

const deleteModel = async (model) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模型 "${model.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await aiModelStore.deleteModel(model.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    const data = {
      name: formData.name,
      baseUrl: formData.baseUrl,
      apiKey: formData.apiKey || null,
      modelName: formData.modelName,
      maxTokens: formData.maxTokens,
      temperature: formData.temperature,
      isDefault: formData.isDefault,
      description: formData.description || null
    }
    
    if (editingModel.value) {
      await aiModelStore.updateModel(editingModel.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await aiModelStore.createModel(data)
      ElMessage.success('创建成功')
    }
    
    showCreateDialog.value = false
    resetForm()
  } catch (error) {
    if (error.message) {
      ElMessage.error(error.message)
    }
  }
}

onMounted(() => {
  aiModelStore.fetchModels()
})
</script>

<style scoped>
.ai-model-manage {
  max-width: 1400px;
  margin: 0 auto;
}

.page-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.5;
}

.mb-16 {
  margin-bottom: 16px;
}
</style>

