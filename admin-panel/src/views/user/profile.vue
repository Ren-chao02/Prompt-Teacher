<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <!-- 左侧：用户信息卡片 -->
      <el-col :span="8">
        <el-card class="profile-card" shadow="never">
          <div class="avatar-section">
            <el-upload
              class="avatar-uploader"
              action="/api/v1/users/avatar/"
              :show-file-list="false"
              :on-success="handleAvatarSuccess"
              :before-upload="beforeAvatarUpload"
              :headers="uploadHeaders"
            >
              <img v-if="userForm.avatar" :src="userForm.avatar" alt="头像" class="avatar-image" />
              <el-icon v-else class="avatar-placeholder"><Plus /></el-icon>
            </el-upload>
            
            <h3 class="username">{{ userForm.username }}</h3>
            <el-tag :type="getRoleTagType(userForm.role)" size="small">
              {{ getRoleLabel(userForm.role) }}
            </el-tag>
          </div>

          <el-divider />

          <div class="info-list">
            <div class="info-item">
              <span class="label">📧 邮箱</span>
              <span class="value">{{ userForm.email || '未设置' }}</span>
            </div>

            <div class="info-item">
              <span class="label">📱 手机号</span>
              <span class="value">{{ userForm.phone || '未设置' }}</span>
            </div>

            <div class="info-item" v-if="userForm.student_id">
              <span class="label">🎓 学号</span>
              <span class="value">{{ userForm.student_id }}</span>
            </div>

            <div class="info-item" v-if="userForm.major">
              <span class="label">📚 专业</span>
              <span class="value">{{ userForm.major }}</span>
            </div>

            <div class="info-item" v-if="userForm.semester">
              <span class="label">📅 学期</span>
              <span class="value">{{ userForm.semester }}</span>
            </div>

            <div class="info-item">
              <span class="label">⏰ 注册时间</span>
              <span class="value">{{ formatDate(userForm.date_joined) }}</span>
            </div>

            <div class="info-item">
              <span class="label">🔄 最后登录</span>
              <span class="value">{{ formatDate(userForm.last_login) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：编辑表单 -->
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>编辑个人信息</span>
            </div>
          </template>

          <el-form
            ref="formRef"
            :model="userForm"
            :rules="formRules"
            label-width="100px"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="userForm.email" placeholder="请输入邮箱" type="email" />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="userForm.phone" placeholder="请输入手机号" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="学号" prop="student_id">
                  <el-input 
                    v-model="userForm.student_id" 
                    placeholder="仅学生角色需要"
                    :disabled="userForm.role !== 'student'"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="专业" prop="major">
                  <el-input v-model="userForm.major" placeholder="请输入专业" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="学期" prop="semester">
                  <el-input v-model="userForm.semester" placeholder="格式: 2024-2025-1" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item>
              <el-button type="primary" :loading="saveLoading" @click="handleSaveProfile">
                保存修改
              </el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 修改密码卡片 -->
        <el-card shadow="never" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span>修改密码</span>
            </div>
          </template>

          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
          >
            <el-form-item label="当前密码" prop="old_password">
              <el-input
                v-model="passwordForm.old_password"
                type="password"
                show-password
                placeholder="请输入当前密码"
              />
            </el-form-item>

            <el-form-item label="新密码" prop="new_password">
              <el-input
                v-model="passwordForm.new_password"
                type="password"
                show-password
                placeholder="请输入新密码（至少6位）"
                show-strength
              />
            </el-form-item>

            <el-form-item label="确认新密码" prop="new_password_confirm">
              <el-input
                v-model="passwordForm.new_password_confirm"
                type="password"
                show-password
                placeholder="请再次输入新密码"
              />
            </el-form-item>

            <el-form-item>
              <el-button type="warning" :loading="passwordLoading" @click="handleChangePassword">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'
import { getUserInfoApi, changePasswordApi } from '@/api/auth'

const authStore = useAuthStore()

const formRef = ref(null)
const passwordFormRef = ref(null)
const saveLoading = ref(false)
const passwordLoading = ref(false)

const userForm = reactive({
  username: '',
  email: '',
  phone: '',
  avatar: '',
  role: '',
  student_id: '',
  major: '',
  semester: '',
  date_joined: '',
  last_login: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  new_password_confirm: ''
})

const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${authStore.token}`
}))

const formRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

const validatePasswordConfirm = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的新密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度在 6 到 128 个字符', trigger: 'blur' }
  ],
  new_password_confirm: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validatePasswordConfirm, trigger: 'blur' }
  ]
}

onMounted(async () => {
  await fetchUserInfo()
})

async function fetchUserInfo() {
  try {
    const res = await getUserInfoApi()
    const userData = res.data
    
    Object.assign(userForm, {
      username: userData.username || '',
      email: userData.email || '',
      phone: userData.phone || '',
      avatar: userData.avatar || '',
      role: userData.role || '',
      student_id: userData.student_id || '',
      major: userData.major || '',
      semester: userData.semester || '',
      date_joined: userData.date_joined || '',
      last_login: userData.last_login || ''
    })
    
    authStore.user = userData
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

async function handleSaveProfile() {
  if (!formRef.value) return
  
  await formRef.validate(async (valid) => {
    if (!valid) return
    
    saveLoading.value = true
    
    try {
      const updateData = {
        email: userForm.email,
        phone: userForm.phone,
        student_id: userForm.student_id,
        major: userForm.major,
        semester: userForm.semester
      }
      
      const res = await fetch('/api/v1/auth/me/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authStore.token}`
        },
        body: JSON.stringify(updateData)
      })
      
      if (res.ok) {
        ElMessage.success('个人信息更新成功')
        await fetchUserInfo()
      } else {
        throw new Error('更新失败')
      }
    } catch (error) {
      console.error('保存失败:', error)
      ElMessage.error('保存失败，请稍后重试')
    } finally {
      saveLoading.value = false
    }
  })
}

async function handleChangePassword() {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.validate(async (valid) => {
    if (!valid) return
    
    try {
      await ElMessageBox.confirm(
        '确定要修改密码吗？修改后需要重新登录！',
        '提示',
        { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
      )
      
      passwordLoading.value = true
      
      await changePasswordApi(passwordForm)
      
      ElMessage.success('密码修改成功，即将跳转到登录页面...')
      
      setTimeout(() => {
        authStore.logout()
        window.location.href = '/admin/login'
      }, 1500)
    } catch (error) {
      if (error !== 'cancel') {
        console.error('修改密码失败:', error)
      }
    } finally {
      passwordLoading.value = false
    }
  })
}

function resetForm() {
  fetchUserInfo()
  
  Object.assign(passwordForm, {
    old_password: '',
    new_password: '',
    new_password_confirm: ''
  })
  
  if (passwordFormRef.value) {
    passwordFormRef.value.resetFields()
  }
}

function handleAvatarSuccess(response) {
  if (response.code === 200) {
    ElMessage.success('头像上传成功')
    userForm.avatar = response.data.avatar
    authStore.user.avatar = response.data.avatar
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

function beforeAvatarUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件！')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB！')
    return false
  }

  return true
}

function getRoleTagType(role) {
  const map = { admin: 'danger', teacher: 'warning', student: '' }
  return map[role] || 'info'
}

function getRoleLabel(role) {
  const map = { admin: '管理员', teacher: '教师', student: '学生' }
  return map[role] || role
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.profile-container {
  padding: 0;
}

.profile-card {
  height: fit-content;
}

.avatar-section {
  text-align: center;
  padding: 30px 0;
}

.avatar-uploader {
  display: inline-block;
  margin-bottom: 16px;
}

.avatar-uploader .avatar-image {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #409EFF;
  cursor: pointer;
}

.avatar-uploader .avatar-placeholder {
  font-size: 28px;
  color: #8c939d;
  width: 120px;
  height: 120px;
  line-height: 120px;
  text-align: center;
  border: 2px dashed #d9d9d9;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
}

.avatar-uploader:hover .avatar-placeholder {
  border-color: #409EFF;
  color: #409EFF;
}

.username {
  margin: 0 0 10px 0;
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.info-list {
  padding: 0 10px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  font-size: 14px;
  color: #909399;
  flex-shrink: 0;
}

.info-item .value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
  text-align: right;
  word-break: break-all;
}

.card-header {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}
</style>
