<template>
  <div class="class-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>班级管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>新建班级
          </el-button>
        </div>
      </template>

      <!-- 筛选 -->
      <el-form :inline="true" :model="filters" class="filter-bar">
        <el-form-item label="年级">
          <el-input v-model="filters.grade" placeholder="如 2024" clearable style="width:140px" />
        </el-form-item>
        <el-form-item label="专业">
          <el-input v-model="filters.major" placeholder="搜索专业" clearable style="width:160px" />
        </el-form-item>
        <el-form-item label="班级">
          <el-input v-model="filters.search" placeholder="搜索班级名" clearable style="width:160px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table v-loading="loading" :data="classList" stripe border>
        <el-table-column prop="name" label="班级名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="grade" label="年级" width="100" sortable />
        <el-table-column prop="major" label="专业" width="180" show-overflow-tooltip />
        <el-table-column prop="class_number" label="班号" width="80" />
        <el-table-column prop="student_count" label="学生数" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ row.student_count }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除该班级？" @confirm="handleDelete(row.id)">
              <template #reference><el-button size="small" link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          :page-size="pagination.pageSize"
          :total="pagination.total"
          layout="total, prev, pager, next"
          background
          @current-change="fetchData"
        />
      </div>
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑班级' : '新建班级'" width="500px"
      :close-on-click-modal="false" @closed="resetForm">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="班级名称" prop="name">
          <el-input v-model="formData.name" placeholder="如：计算机科学2301班" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="年级" prop="grade">
              <el-input v-model="formData.grade" placeholder="如：2024" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="班号" prop="class_number">
              <el-input v-model="formData.class_number" placeholder="如：01" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="专业" prop="major">
          <el-input v-model="formData.major" placeholder="如：计算机科学与技术" />
        </el-form-item>
        <el-form-item label="备注" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getClassList, createClass, updateClass, deleteClass } from '@/api/user'

const loading = ref(false)
const submitLoading = ref(false)
const classList = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

const filters = reactive({ grade: '', major: '', search: '' })
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const formData = reactive({ name: '', grade: '', major: '', class_number: '', description: '' })
const formRules = {
  name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }],
}

onMounted(() => { fetchData() })

async function fetchData() {
  loading.value = true
  try {
    const params = { ...filters, search: filters.search, page: pagination.page, page_size: pagination.pageSize }
    const res = await getClassList(params)
    const data = res.data.results || res.data
    if (Array.isArray(data)) {
      classList.value = data
      pagination.total = res.data.count || data.length
    }
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function resetFilters() {
  Object.assign(filters, { grade: '', major: '', search: '' })
  pagination.page = 1
  fetchData()
}

function handleCreate() {
  isEdit.value = false
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  editId.value = row.id
  Object.assign(formData, { name: row.name, grade: row.grade || '', major: row.major || '', class_number: row.class_number || '', description: row.description || '' })
  dialogVisible.value = true
}

function resetForm() {
  Object.assign(formData, { name: '', grade: '', major: '', class_number: '', description: '' })
  formRef.value?.resetFields()
}

async function handleSubmit() {
  if (!formRef.value) return
  try { await formRef.validate() } catch { return }

  submitLoading.value = true
  try {
    if (isEdit.value) {
      await updateClass(editId.value, formData)
      ElMessage.success('更新成功')
    } else {
      await createClass(formData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e) { console.error(e) }
  finally { submitLoading.value = false }
}

async function handleDelete(id) {
  try {
    await deleteClass(id)
    ElMessage.success('已删除')
    fetchData()
  } catch (e) { console.error(e) }
}
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.filter-bar { margin-bottom: 16px; }
.pagination-wrapper { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
