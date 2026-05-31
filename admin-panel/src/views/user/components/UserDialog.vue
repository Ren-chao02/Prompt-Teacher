<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑用户' : '新建用户'"
    width="600px"
    :close-on-click-modal="false"
    @update:model-value="$emit('update:visible', $event)"
    @closed="handleClosed"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
      label-position="right"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="用户名" prop="username">
            <el-input 
              v-model="formData.username" 
              placeholder="请输入用户名"
              :disabled="isEdit"
            />
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="formData.email" placeholder="请输入邮箱" type="email" />
          </el-form-item>
        </el-col>
      </el-row>

      <template v-if="!isEdit">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="密码" prop="password">
              <el-input 
                v-model="formData.password" 
                type="password" 
                show-password 
                placeholder="请输入密码"
              />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="确认密码" prop="password_confirm">
              <el-input 
                v-model="formData.password_confirm" 
                type="password" 
                show-password 
                placeholder="请再次输入密码"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </template>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="角色" prop="role">
            <el-select v-model="formData.role" placeholder="请选择角色" style="width: 100%">
              <el-option label="管理员" value="admin" />
              <el-option label="教师" value="teacher" />
              <el-option label="学生" value="student" />
            </el-select>
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="formData.phone" placeholder="请输入手机号" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="学号" prop="student_id">
            <el-input v-model="formData.student_id" placeholder="仅学生角色需要" />
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="专业" prop="major">
            <el-input v-model="formData.major" placeholder="请输入专业" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="学期" prop="semester">
            <el-input v-model="formData.semester" placeholder="格式: 2024-2025-1" />
          </el-form-item>
        </el-col>

        <el-col :span="12" v-if="formData.role === 'student'">
          <el-form-item label="指导教师" prop="teacher">
            <el-select 
              v-model="formData.teacher" 
              placeholder="请选择指导教师" 
              style="width: 100%"
              filterable
            >
              <el-option 
                v-for="teacher in teacherList" 
                :key="teacher.id" 
                :label="teacher.username" 
                :value="teacher.id" 
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="$emit('update:visible', false)">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { createUser, updateUser, getMyStudents } from '@/api/user'

const props = defineProps({
  visible: Boolean,
  userData: Object,
  isEdit: Boolean
})

const emit = defineEmits(['update:visible', 'success'])

const formRef = ref(null)
const submitLoading = ref(false)
const teacherList = ref([])

const formData = reactive({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  role: 'student',
  phone: '',
  student_id: '',
  major: '',
  semester: '',
  teacher: null
})

const validatePasswordConfirm = (rule, value, callback) => {
  if (value !== formData.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 150, message: '用户名长度在 3 到 150 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度在 6 到 128 个字符', trigger: 'blur' }
  ],
  password_confirm: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePasswordConfirm, trigger: 'blur' }
  ]
}

watch(() => props.visible, (val) => {
  if (val && props.isEdit && props.userData) {
    Object.assign(formData, {
      username: props.userData.username || '',
      email: props.userData.email || '',
      role: props.userData.role || 'student',
      phone: props.userData.phone || '',
      student_id: props.userData.student_id || '',
      major: props.userData.major || '',
      semester: props.userData.semester || '',
      teacher: props.userData.teacher || null
    })
  } else if (val && !props.isEdit) {
    resetForm()
  }
})

watch(() => formData.role, async (role) => {
  if (role === 'student') {
    try {
      const res = await getMyStudents({ ordering: 'username' })
      const users = res.data.results || res.data
      teacherList.value = users.filter(u => u.role === 'admin' || u.role === 'teacher')
    } catch (error) {
      console.error('获取教师列表失败:', error)
    }
  }
}, { immediate: true })

function resetForm() {
  Object.assign(formData, {
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    role: 'student',
    phone: '',
    student_id: '',
    major: '',
    semester: '',
    teacher: null
  })
  
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.validate(async (valid) => {
    if (!valid) return
    
    submitLoading.value = true
    
    try {
      let data = { ...formData }
      
      if (!props.isEdit) {
        await createUser(data)
        ElMessage.success('用户创建成功')
      } else {
        delete data.password
        delete data.password_confirm
        
        await updateUser(props.userData.id, data)
        ElMessage.success('用户信息更新成功')
      }
      
      emit('success')
      emit('update:visible', false)
    } catch (error) {
      console.error('操作失败:', error)
    } finally {
      submitLoading.value = false
    }
  })
}

function handleClosed() {
  resetForm()
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
