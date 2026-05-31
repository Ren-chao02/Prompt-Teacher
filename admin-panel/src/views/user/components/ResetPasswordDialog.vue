<template>
  <el-dialog
    :model-value="visible"
    :title="`重置用户 ${user?.username || ''} 的密码`"
    width="450px"
    :close-on-click-modal="false"
    @update:model-value="$emit('update:visible', $event)"
    @closed="handleClosed"
  >
    <el-alert
      title="警告：重置密码后，该用户需要使用新密码重新登录！"
      type="warning"
      show-icon
      :closable="false"
      style="margin-bottom: 20px"
    />

    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
    >
      <el-form-item label="新密码" prop="new_password">
        <el-input
          v-model="formData.new_password"
          type="password"
          show-password
          placeholder="请输入新密码（至少6位）"
          show-strength
        />
      </el-form-item>

      <el-form-item label="确认密码" prop="new_password_confirm">
        <el-input
          v-model="formData.new_password_confirm"
          type="password"
          show-password
          placeholder="请再次输入新密码"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="$emit('update:visible', false)">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确认重置
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { resetUserPassword } from '@/api/user'

const props = defineProps({
  visible: Boolean,
  user: Object
})

const emit = defineEmits(['update:visible', 'success'])

const formRef = ref(null)
const submitLoading = ref(false)

const formData = reactive({
  new_password: '',
  new_password_confirm: ''
})

const validatePasswordConfirm = (rule, value, callback) => {
  if (value !== formData.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const formRules = {
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度在 6 到 128 个字符', trigger: 'blur' }
  ],
  new_password_confirm: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validatePasswordConfirm, trigger: 'blur' }
  ]
}

watch(() => props.visible, (val) => {
  if (!val) return
  
  formData.new_password = ''
  formData.new_password_confirm = ''
  
  if (formRef.value) {
    formRef.value.resetFields()
  }
})

async function handleSubmit() {
  if (!formRef.value || !props.user) return
  
  await formRef.validate(async (valid) => {
    if (!valid) return
    
    submitLoading.value = true
    
    try {
      await resetUserPassword(props.user.id, formData.new_password)
      
      ElMessage.success(`用户 ${props.user.username} 的密码已成功重置`)
      emit('success')
      emit('update:visible', false)
    } catch (error) {
      console.error('重置密码失败:', error)
    } finally {
      submitLoading.value = false
    }
  })
}

function handleClosed() {
  formData.new_password = ''
  formData.new_password_confirm = ''
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
