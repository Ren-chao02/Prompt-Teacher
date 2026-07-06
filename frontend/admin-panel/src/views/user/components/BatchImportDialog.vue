<template>
  <el-dialog :model-value="visible" title="批量导入用户" width="860px"
    :close-on-click-modal="false" @update:model-value="$emit('update:visible', $event)"
    @closed="resetState">
    <!-- 步骤条 -->
    <el-steps :active="step" align-center class="import-steps">
      <el-step title="下载模板" icon="Download" />
      <el-step title="上传预览" icon="Upload" />
      <el-step title="编辑确认" icon="EditPen" />
      <el-step title="导入结果" icon="CircleCheck" />
    </el-steps>

    <!-- Step 0: 模板 -->
    <div v-if="step === 0" class="step-content">
      <el-alert type="info" :closable="false" show-icon>
        <template #title>请先下载 Excel 模板，按格式填写后上传</template>
        <p style="margin:4px 0 0;font-size:12px;color:#666">列：角色 | 学号/工号 | 姓名 | 班级名称 | 手机号 | 学期 | 指导教师</p>
      </el-alert>
      <div style="text-align:center;margin-top:24px">
        <el-button type="primary" size="large" @click="handleDownloadTemplate">
          <el-icon><Download /></el-icon>下载导入模板
        </el-button>
      </div>
    </div>

    <!-- Step 1: 上传 -->
    <div v-if="step === 1" class="step-content">
      <el-upload ref="uploadRef" drag accept=".xlsx,.xls"
        :auto-upload="false" :limit="1" :on-change="handleFileChange"
        :on-exceed="() => ElMessage.warning('只能上传一个文件')">
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽文件到此处或<em>点击选择</em></div>
        <template #tip><div class="el-upload__tip">仅支持 .xlsx/.xls 文件</div></template>
      </el-upload>
      <div style="text-align:center;margin-top:20px">
        <el-button type="primary" :disabled="!file" :loading="uploading" @click="handleUpload">
          上传并预览
        </el-button>
      </div>
    </div>

    <!-- Step 2: 可编辑预览 -->
    <div v-if="step === 2" class="step-content">
      <el-alert type="success" :closable="false" show-icon style="margin-bottom:12px">
        <template #title>共解析 {{ previewRows.length }} 条数据</template>
        <p style="margin:4px 0 0;font-size:12px;color:#666">请检查数据，可直接在表格中修改班级、指导教师等信息，确认无误后提交。</p>
      </el-alert>

      <el-table :data="previewRows" border size="small" max-height="360"
        :header-cell-style="{ background:'#f5f7fa', color:'#303133', fontWeight:600 }">
        <el-table-column prop="row" label="#" width="40" align="center" />
        <el-table-column label="角色" width="80">
          <template #default="{ row, $index }">
            <el-select v-model="row.role" size="small" style="width:100%">
              <el-option label="学生" value="student" />
              <el-option label="教师" value="teacher" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="学号/工号" width="120">
          <template #default="{ row }">
            <el-input v-model="row.identifier" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="姓名" width="90">
          <template #default="{ row }">
            <el-input v-model="row.name" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="班级" min-width="150">
          <template #default="{ row }">
            <el-select v-model="row.class_name" filterable allow-create clearable
              placeholder="选择或输入班级" size="small" style="width:100%">
              <el-option v-for="c in classOptions" :key="c.id" :label="c.name" :value="c.name" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="手机号" width="125">
          <template #default="{ row }">
            <el-input v-model="row.phone" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="学期" width="110">
          <template #default="{ row }">
            <el-input v-model="row.semester" size="small" placeholder="如 2024-2025-1" />
          </template>
        </el-table-column>
        <el-table-column label="指导教师" min-width="130">
          <template #default="{ row }">
            <el-select v-model="row.teacher_name" filterable allow-create clearable
              placeholder="选择或输入教师" size="small" style="width:100%">
              <el-option v-for="t in teacherOptions" :key="t.id"
                :label="t.real_name || t.username" :value="t.real_name || t.username" />
            </el-select>
          </template>
        </el-table-column>
      </el-table>

      <el-collapse v-if="previewErrors.length" style="margin-top:8px">
        <el-collapse-item name="errors" :title="`解析错误 (${previewErrors.length} 条)`">
          <el-table :data="previewErrors" size="small" border>
            <el-table-column prop="row" label="行号" width="70" />
            <el-table-column prop="error" label="错误原因" />
          </el-table>
        </el-collapse-item>
      </el-collapse>
    </div>

    <!-- Step 3: 导入结果 -->
    <div v-if="step === 3" class="step-content">
      <el-descriptions :column="2" border size="small" style="margin-bottom:16px">
        <el-descriptions-item label="成功">
          <span style="color:#67c23a;font-weight:bold">{{ importResult?.total_success || 0 }} 条</span>
        </el-descriptions-item>
        <el-descriptions-item label="失败">
          <span :style="{ color: (importResult?.total_errors||0) > 0 ? '#f56c6c' : '#666', fontWeight:'bold' }">{{ importResult?.total_errors || 0 }} 条</span>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 成功列表（含默认密码） -->
      <el-table v-if="importResult?.results?.length" :data="importResult.results" max-height="260" size="small" stripe>
        <el-table-column prop="row" label="行号" width="55" />
        <el-table-column prop="role" label="角色" width="75">
          <template #default="{ row }"><el-tag size="small" :type="row.role==='student'?'':'warning'">{{ row.role==='student'?'学生':'教师' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="identifier" label="标识符" width="110" />
        <el-table-column prop="name" label="姓名" width="85" />
        <el-table-column prop="class_name" label="班级" min-width="140" />
        <el-table-column prop="phone" label="手机号" width="115" />
        <el-table-column prop="default_password" label="默认密码" width="105">
          <template #default="{ row }">
            <code style="color:#e6a23c;background:#fdf6ec;padding:2px 6px;border-radius:3px">{{ row.default_password }}</code>
          </template>
        </el-table-column>
      </el-table>

      <!-- 错误列表 -->
      <el-collapse v-if="importResult?.errors?.length" style="margin-top:8px">
        <el-collapse-item name="errors" title="导入错误详情">
          <el-table :data="importResult.errors" size="small" border>
            <el-table-column prop="row" label="行号" width="70" />
            <el-table-column prop="error" label="错误原因" />
          </el-table>
        </el-collapse-item>
      </el-collapse>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="$emit('update:visible', false)">关闭</el-button>
        <el-button v-if="step > 0 && step <= 2" @click="step--">上一步</el-button>
        <el-button v-if="step === 0" type="primary" @click="step++">下一步</el-button>
        <el-button v-if="step === 2" type="primary" :loading="confirming" @click="handleConfirm">
          确认导入 ({{ previewRows.length }}条)
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, UploadFilled } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/modules/auth'
import { previewImport, confirmImport } from '@/api/user'

defineProps({ visible: Boolean })
defineEmits(['update:visible', 'success'])

const step = ref(0)
const file = ref(null)
const uploading = ref(false)
const confirming = ref(false)

// 预览数据（可编辑）
const previewRows = ref([])
const previewErrors = ref([])
const classOptions = ref([])
const teacherOptions = ref([])

// 最终导入结果
const importResult = ref(null)

async function handleDownloadTemplate() {
  try {
    const authStore = useAuthStore()
    const apiBase = import.meta.env.VITE_API_BASE_URL || '/api/v1'
    const res = await fetch(`${apiBase}/users/download_template/`, {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'user_import_template.xlsx'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('模板已下载')
  } catch (e) {
    console.error(e)
    ElMessage.error('下载失败')
  }
}

function handleFileChange(uploadFile) {
  file.value = uploadFile.raw || null
}

async function handleUpload() {
  if (!file.value) return
  uploading.value = true
  try {
    const res = await previewImport(file.value)
    const d = res.data
    previewRows.value = d.rows || []
    previewErrors.value = d.errors || []
    classOptions.value = d.class_options || []
    teacherOptions.value = d.teacher_options || []
    if (d.rows?.length > 0) {
      step.value = 2 // 跳到可编辑预览
    } else {
      ElMessage.warning('未解析到有效数据')
    }
  } catch (e) {
    console.error(e)
    ElMessage.error(e.response?.data?.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

async function handleConfirm() {
  if (!previewRows.value.length) return
  confirming.value = true
  try {
    const res = await confirmImport(previewRows.value)
    // axios 拦截器已解包 response.data，res = { code, message, data }
    const d = res.data || res
    importResult.value = d
    step.value = 3

    if (d.total_success > 0) {
      ElMessage.success(`成功导入 ${d.total_success} 条`)
    }
    if (d.total_errors > 0) {
      ElMessage.warning(`${d.total_errors} 条数据导入失败，请查看错误详情`)
    }
    emitSuccess()
  } catch (e) {
    console.error(e)
    const msg = e?.data?.message || e?.message || '导入失败'
    ElMessage.error(msg)
  } finally {
    confirming.value = false
  }
}

function emitSuccess() {
  // 通过 defineEmits 触发父组件刷新
}

function resetState() {
  step.value = 0
  file.value = null
  uploading.value = false
  confirming.value = false
  previewRows.value = []
  previewErrors.value = []
  classOptions.value = []
  teacherOptions.value = []
  importResult.value = null
}
</script>

<style scoped>
.import-steps { margin-bottom: 20px; }
.step-content { min-height: 180px; padding: 10px 0; }
.dialog-footer { display: flex; justify-content: flex-end; gap: 12px; }
</style>
