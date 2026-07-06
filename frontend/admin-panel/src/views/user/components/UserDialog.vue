<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑用户' : '新建用户'"
    width="620px"
    :close-on-click-modal="false"
    @update:model-value="$emit('update:visible', $event)"
    @closed="handleClosed"
  >
    <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="角色" prop="role">
            <el-select v-model="formData.role" placeholder="请选择角色" style="width: 100%"
              :disabled="isEdit">
              <el-option label="学生" value="student" />
              <el-option label="教师" value="teacher" />
              <el-option label="管理员" value="admin" />
            </el-select>
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="真实姓名" prop="real_name">
            <el-input v-model="formData.real_name" placeholder="请输入真实姓名" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 学生：学号 -->
      <el-row v-if="formData.role === 'student'" :gutter="20">
        <el-col :span="12">
          <el-form-item label="学号" prop="student_id">
            <el-input v-model="formData.student_id" placeholder="请输入学号" :disabled="isEdit" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="班级" prop="class_info">
            <el-select v-model="formData.class_info" placeholder="选择班级" style="width: 100%" filterable clearable>
              <el-option v-for="c in classList" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 教师：工号 -->
      <el-row v-if="formData.role === 'teacher'" :gutter="20">
        <el-col :span="12">
          <el-form-item label="工号" prop="employee_id">
            <el-input v-model="formData.employee_id" placeholder="请输入工号" :disabled="isEdit" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 管理员：用户名 -->
      <el-row v-if="formData.role === 'admin'" :gutter="20">
        <el-col :span="12">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="formData.username" placeholder="请输入用户名" :disabled="isEdit" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="formData.email" placeholder="请输入邮箱" type="email" />
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
          <el-form-item label="学期" prop="semester">
            <el-input v-model="formData.semester" placeholder="格式: 2024-2025-1" />
          </el-form-item>
        </el-col>
        <el-col v-if="formData.role === 'student'" :span="12">
          <el-form-item label="指导教师" prop="teacher">
            <el-select v-model="formData.teacher" placeholder="请选择指导教师" style="width: 100%" filterable clearable>
              <el-option v-for="t in teacherList" :key="t.id" :label="t.real_name || t.username" :value="t.id" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 新建时显示密码 -->
      <template v-if="!isEdit">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="密码" prop="password">
              <el-input v-model="formData.password" type="password" show-password placeholder="默认: 标识符后6位" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="确认密码" prop="password_confirm">
              <el-input v-model="formData.password_confirm" type="password" show-password placeholder="再次输入密码" />
            </el-form-item>
          </el-col>
        </el-row>
      </template>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="$emit('update:visible', false)">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">{{ isEdit ? '更新' : '创建' }}</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createUser, updateUser, getUserList, getClassList } from '@/api/user'

const props = defineProps({ visible: Boolean, userData: Object, isEdit: Boolean })
const emit = defineEmits(['update:visible', 'success'])

const formRef = ref(null)
const submitLoading = ref(false)
const teacherList = ref([])
const classList = ref([])

const formData = reactive({
  username: '', real_name: '', email: '', phone: '',
  password: '', password_confirm: '', role: 'student',
  student_id: '', employee_id: '', semester: '',
  class_info: null, teacher: null
})

const validatePwdConfirm = (_rule, value, cb) => {
  if (value !== formData.password) cb(new Error('两次密码不一致'))
  else cb()
}

const formRules = {
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
  student_id: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  employee_id: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ min: 6, max: 128, message: '6~128位字符', trigger: 'blur' }],
  password_confirm: [{ validator: validatePwdConfirm, trigger: 'blur' }]
}

// 加载班级列表
async function loadClassList() {
  try {
    const res = await getClassList({ page_size: 200 })
    const payload = res.data || res
    classList.value = payload.results || (Array.isArray(payload) ? payload : [])
  } catch (e) { console.error(e) }
}

// 加载教师列表
async function loadTeacherList() {
  try {
    const res = await getUserList({ role: 'teacher', ordering: 'username', page_size: 200 })
    const payload = res.data || res
    teacherList.value = payload.results || (Array.isArray(payload) ? payload : [])
  } catch (e) { console.error(e) }
}

watch(() => props.visible, async (val) => {
  if (!val) return
  await Promise.all([loadClassList(), loadTeacherList()])

  if (props.isEdit && props.userData) {
    Object.assign(formData, {
      username: props.userData.username || '',
      real_name: props.userData.real_name || '',
      email: props.userData.email || '',
      phone: props.userData.phone || '',
      role: props.userData.role || 'student',
      student_id: props.userData.student_id || '',
      employee_id: props.userData.employee_id || '',
      semester: props.userData.semester || '',
      // class_info/teacher 在序列化器中是 FK，返回的是整数 PK
      class_info: props.userData.class_info || props.userData.class_id || null,
      teacher: props.userData.teacher || null
    })
  } else if (!props.isEdit) {
    resetForm()
  }
})

function resetForm() {
  Object.assign(formData, {
    username: '', real_name: '', email: '', phone: '',
    password: '', password_confirm: '', role: 'student',
    student_id: '', employee_id: '', semester: '',
    class_info: null, teacher: null
  })
  formRef.value?.resetFields()
}

async function handleSubmit() {
  if (!formRef.value) return
  try { await formRef.validate() } catch { return }

  submitLoading.value = true
  try {
    const data = { ...formData }

    // 新建时自动生成 username
    if (!props.isEdit) {
      data.password = data.password || ''
      delete data.password_confirm

      if (data.role === 'student') data.username = data.student_id
      else if (data.role === 'teacher') data.username = data.employee_id
    }

    if (!props.isEdit) {
      await createUser(data)
      ElMessage.success('创建成功')
    } else {
      await updateUser(props.userData.id, data)
      ElMessage.success('更新成功')
    }
    emit('success')
    emit('update:visible', false)
  } catch (e) { console.error(e) }
  finally { submitLoading.value = false }
}

function handleClosed() { resetForm() }
</script>

<style scoped>
.dialog-footer { display: flex; justify-content: flex-end; gap: 12px; }
</style>
