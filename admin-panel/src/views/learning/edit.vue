<template>
  <div class="learning-edit-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑学习资料' : '新建学习资料' }}</span>
          <div class="header-actions">
            <el-tag v-if="autoSaveStatus === 'saving'" type="warning" size="small">
              保存中...
            </el-tag>
            <el-tag v-else-if="autoSaveStatus === 'saved'" type="success" size="small">
              已自动保存
            </el-tag>
          </div>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <!-- 基本信息 -->
        <el-row :gutter="20">
          <el-col :span="16">
            <el-form-item label="标题" prop="title">
              <el-input
                v-model="formData.title"
                placeholder="请输入学习资料标题（2-200个字符）"
                maxlength="200"
                show-word-limit
                @input="handleFormChange"
              />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="分类" prop="category">
              <el-select
                v-model="formData.category"
                placeholder="请选择分类"
                style="width: 100%"
                @change="handleFormChange"
              >
                <el-option label="基础入门" value="basic" />
                <el-option label="进阶技巧" value="intermediate" />
                <el-option label="高级应用" value="advanced" />
                <el-option label="最佳实践" value="best_practices" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="摘要" prop="summary">
              <el-input
                v-model="formData.summary"
                type="textarea"
                :rows="3"
                placeholder="请输入内容摘要（发布时必填）"
                maxlength="500"
                show-word-limit
                @input="handleFormChange"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- Markdown 编辑器 -->
        <el-form-item label="内容" prop="content">
          <div class="markdown-editor-wrapper">
            <div class="editor-toolbar">
              <span class="editor-tip">支持 Markdown 语法</span>
            </div>
            
            <el-input
              ref="contentEditor"
              v-model="formData.content"
              type="textarea"
              :rows="20"
              placeholder="# 请输入 Markdown 内容

## 支持的语法：

### 标题
# 一级标题
## 二级标题
### 三级标题

### 文本样式
**粗体**、*斜体*、~~删除线~~

### 列表
- 无序列表项
1. 有序列表项

### 链接和图片
[链接文本](URL)
![图片描述](图片URL)

### 代码
`行内代码`

\`\`\`
代码块
\`\`\`

> 引用文本
"
              class="markdown-editor"
              @input="handleContentChange"
            />
            
            <div class="editor-footer">
              <span class="word-count">
                字数: {{ formData.content.length }} | 
                预计阅读: {{ readingTime }} 分钟
              </span>
            </div>
          </div>
        </el-form-item>

        <!-- 其他信息 -->
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="排序权重">
              <el-input-number
                v-model="formData.order_index"
                :min="0"
                :max="9999"
                style="width: 100%"
                @change="handleFormChange"
              />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="状态">
              <el-select
                v-model="formData.status"
                style="width: 100%"
                @change="handleFormChange"
              >
                <el-option label="草稿" value="draft" />
                <el-option label="已发布" value="published" />
                <el-option label="已下架" value="archived" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="封面图片">
              <el-input
                v-model="formData.cover_image"
                placeholder="请输入封面图片 URL（可选）"
                clearable
                @input="handleFormChange"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="标签">
              <div class="tags-input-wrapper">
                <el-tag
                  v-for="(tag, index) in formData.tags"
                  :key="index"
                  closable
                  size="small"
                  @close="handleRemoveTag(index)"
                  style="margin-right: 4px; margin-bottom: 4px;"
                >
                  {{ tag }}
                </el-tag>
                
                <el-input
                  v-if="tagInputVisible"
                  ref="tagInputRef"
                  v-model="tagInputValue"
                  size="small"
                  style="width: 100px; margin-right: 4px;"
                  @keyup.enter="handleAddTag"
                  @blur="handleAddTag"
                />
                
                <el-button 
                  v-else 
                  size="small" 
                  @click="showTagInput"
                >
                  + 添加标签
                </el-button>
                
                <span class="tags-tip" v-if="formData.tags.length >= 5">
                  （最多10个标签）
                </span>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 操作按钮 -->
        <el-form-item>
          <div class="form-actions">
            <el-button @click="handleSaveDraft('draft')" :loading="saveLoading">
              💾 保存草稿
            </el-button>
            <el-button 
              type="primary" 
              @click="handlePublish" 
              :loading="publishLoading"
              :disabled="!isFormValid"
            >
              🚀 {{ isEdit ? '更新并发布' : '发布' }}
            </el-button>
            <el-button @click="$router.back()">
              ← 返回列表
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      title="内容预览"
      width="80%"
      top="5vh"
    >
      <div class="preview-content" v-html="previewHtml"></div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  createMaterial,
  updateMaterial,
  getMaterialDetail
} from '@/api/learning'

const route = useRoute()
const router = useRouter()

const formRef = ref(null)
const contentEditor = ref(null)
const tagInputRef = ref(null)
const saveLoading = ref(false)
const publishLoading = ref(false)
const autoSaveTimer = ref(null)
const autoSaveStatus = ref('idle')
const previewVisible = ref(false)
const previewHtml = ref('')
const tagInputVisible = ref(false)
const tagInputValue = ref('')

const isEdit = computed(() => !!route.params.id)

const formData = reactive({
  title: '',
  summary: '',
  content: '',
  category: 'basic',
  status: 'draft',
  cover_image: '',
  tags: [],
  order_index: 0
})

const formRules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 2, max: 200, message: '标题长度在 2 到 200 个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入内容', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ]
}

const isFormValid = computed(() => {
  return (
    formData.title.trim().length >= 2 &&
    formData.content.trim().length > 0 &&
    formData.category !== ''
  )
})

const readingTime = computed(() => {
  const minutes = Math.ceil(formData.content.length / 100)
  return Math.max(1, minutes)
})

onMounted(async () => {
  if (isEdit.value) {
    await fetchMaterialData()
  }
  
  loadDraft()
  startAutoSave()
})

onUnmounted(() => {
  stopAutoSave()
})

async function fetchMaterialData() {
  try {
    const res = await getMaterialDetail(route.params.id)
    const data = res.data
    
    Object.assign(formData, {
      title: data.title || '',
      summary: data.summary || '',
      content: data.content || '',
      category: data.category || 'basic',
      status: data.status || 'draft',
      cover_image: data.cover_image || '',
      tags: data.tags || [],
      order_index: data.order_index || 0
    })
  } catch (error) {
    console.error('获取学习资料详情失败:', error)
    ElMessage.error('获取数据失败')
  }
}

function handleFormChange() {
  saveDraft()
}

function handleContentChange() {
  saveDraft()
}

let draftSaveTimer = null
function saveDraft() {
  if (draftSaveTimer) clearTimeout(draftSaveTimer)
  
  draftSaveTimer = setTimeout(() => {
    const draftKey = `learning_draft_${route.params.id || 'new'}`
    localStorage.setItem(draftKey, JSON.stringify({
      ...formData,
      savedAt: new Date().toISOString()
    }))
  }, 1000)
}

function loadDraft() {
  const draftKey = `learning_draft_${route.params.id || 'new'}`
  const draftStr = localStorage.getItem(draftKey)
  
  if (draftStr && !isEdit.value) {
    try {
      const draft = JSON.parse(draftStr)
      
      if (confirm(`发现未保存的草稿（保存于 ${new Date(draft.savedAt).toLocaleString()}），是否恢复？`)) {
        Object.assign(formData, {
          title: draft.title || '',
          summary: draft.summary || '',
          content: draft.content || '',
          category: draft.category || 'basic',
          status: draft.status || 'draft',
          cover_image: draft.cover_image || '',
          tags: draft.tags || [],
          order_index: draft.order_index || 0
        })
        
        ElMessage.success('已恢复草稿')
      }
    } catch (e) {
      console.error('加载草稿失败:', e)
    }
  }
}

function startAutoSave() {
  if (autoSaveTimer.value) return
  
  autoSaveTimer.value = setInterval(() => {
    if (isFormValid.value && !isEdit.value) {
      handleAutoSave()
    }
  }, 30000)
}

function stopAutoSave() {
  if (autoSaveTimer.value) {
    clearInterval(autoSaveTimer.value)
    autoSaveTimer.value = null
  }
}

async function handleAutoSave() {
  if (!isFormValid.value) return
  
  autoSaveStatus.value = 'saving'
  
  try {
    await createMaterial({
      ...formData,
      status: 'draft'
    })
    
    autoSaveStatus.value = 'saved'
    
    setTimeout(() => {
      autoSaveStatus.value = 'idle'
    }, 3000)
  } catch (error) {
    console.error('自动保存失败:', error)
    autoSaveStatus.value = 'idle'
  }
}

async function handleSaveDraft(status = 'draft') {
  if (!formRef.value) return
  
  await formRef.validate(async (valid) => {
    if (!valid) return
    
    saveLoading.value = true
    
    try {
      const data = { ...formData, status }
      
      if (isEdit.value) {
        await updateMaterial(route.params.id, data)
        ElMessage.success('草稿保存成功')
      } else {
        const res = await createMaterial(data)
        ElMessage.success('创建成功，即将跳转到编辑页面...')
        
        setTimeout(() => {
          router.replace(`/learning/edit/${res.data.id}`)
        }, 1000)
      }
      
      localStorage.removeItem(`learning_draft_${route.params.id || 'new'}`)
    } catch (error) {
      console.error('保存失败:', error)
      ElMessage.error('保存失败，请检查表单')
    } finally {
      saveLoading.value = false
    }
  })
}

async function handlePublish() {
  if (!formRef.value) return
  
  await formRef.validate(async (valid) => {
    if (!valid) return
    
    if (!formData.summary.trim()) {
      ElMessage.warning('发布前请填写摘要')
      return
    }
    
    publishLoading.value = true
    
    try {
      const data = { ...formData, status: 'published' }
      
      if (isEdit.value) {
        await updateMaterial(route.params.id, data)
        ElMessage.success('内容已发布！')
      } else {
        const res = await createMaterial(data)
        ElMessage.success('创建并发布成功！')
        
        setTimeout(() => {
          router.push('/learning/list')
        }, 1500)
        return
      }
      
      localStorage.removeItem(`learning_draft_${route.params.id || 'new'}`)
      
      setTimeout(() => {
        router.push('/learning/list')
      }, 1000)
    } catch (error) {
      console.error('发布失败:', error)
      ElMessage.error('发布失败，请检查表单')
    } finally {
      publishLoading.value = false
    }
  })
}

function showTagInput() {
  tagInputVisible.value = true
  nextTick(() => {
    tagInputRef.value?.focus()
  })
}

function handleAddTag() {
  const tag = tagInputValue.value.trim()
  
  if (!tag) {
    tagInputVisible.value = false
    return
  }
  
  if (formData.tags.length >= 10) {
    ElMessage.warning('最多添加10个标签')
    tagInputVisible.value = false
    tagInputValue.value = ''
    return
  }
  
  if (tag.length > 20) {
    ElMessage.warning('标签长度不能超过20个字符')
    return
  }
  
  if (formData.tags.includes(tag)) {
    ElMessage.warning('该标签已存在')
    tagInputValue.value = ''
    return
  }
  
  formData.tags.push(tag)
  tagInputValue.value = ''
  tagInputVisible.value = false
  
  saveDraft()
}

function handleRemoveTag(index) {
  formData.tags.splice(index, 1)
  saveDraft()
}
</script>

<style scoped>
.learning-edit-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.markdown-editor-wrapper {
  width: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.editor-toolbar {
  background-color: #f5f7fa;
  padding: 8px 16px;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.editor-tip {
  font-size: 13px;
  color: #909399;
}

.markdown-editor {
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  border: none !important;
  box-shadow: none !important;
}

.markdown-editor:focus {
  outline: none;
  border: none !important;
  box-shadow: none !important;
}

.editor-footer {
  background-color: #f5f7fa;
  padding: 8px 16px;
  border-top: 1px solid #dcdfe6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.word-count {
  font-size: 13px;
  color: #909399;
}

.tags-input-wrapper {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  padding: 4px 0;
}

.tags-tip {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.preview-content {
  max-height: 70vh;
  overflow-y: auto;
  padding: 20px;
  line-height: 1.8;
}
</style>
