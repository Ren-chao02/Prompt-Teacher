import request from './request'

export function getUserList(params) {
  return request({
    url: '/users/',
    method: 'get',
    params
  })
}

export function getUserDetail(id) {
  return request({
    url: `/users/${id}/`,
    method: 'get'
  })
}

export function createUser(data) {
  return request({
    url: '/users/',
    method: 'post',
    data
  })
}

export function updateUser(id, data) {
  return request({
    url: `/users/${id}/`,
    method: 'put',
    data
  })
}

export function deleteUser(id) {
  return request({
    url: `/users/${id}/`,
    method: 'delete'
  })
}

export function batchDeleteUsers(ids) {
  return request({
    url: '/users/bulk_delete/',
    method: 'post',
    data: { ids }
  })
}

export function resetUserPassword(id, newPassword) {
  return request({
    url: `/users/${id}/reset_password/`,
    method: 'post',
    data: { new_password: newPassword }
  })
}

export function changeUserStatus(id, isActive) {
  return request({
    url: `/users/${id}/change_status/`,
    method: 'put',
    data: { is_active: isActive }
  })
}

export function getMyStudents(params) {
  return request({
    url: '/users/my_students/',
    method: 'get',
    params
  })
}

export function getUserStatistics() {
  return request({
    url: '/users/statistics/',
    method: 'get'
  })
}

export function getClassList(params) {
  return request({
    url: '/classes/',
    method: 'get',
    params
  })
}

export function createClass(data) {
  return request({
    url: '/classes/',
    method: 'post',
    data
  })
}

export function updateClass(id, data) {
  return request({
    url: `/classes/${id}/`,
    method: 'put',
    data
  })
}

export function deleteClass(id) {
  return request({
    url: `/classes/${id}/`,
    method: 'delete'
  })
}

export function previewImport(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/users/preview_import/',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000
  })
}

export function confirmImport(rows) {
  return request({
    url: '/users/confirm_import/',
    method: 'post',
    data: { rows },
    showError: false
  })
}

export function downloadImportTemplate() {
  return request({
    url: '/users/download_template/',
    method: 'get',
    responseType: 'blob'
  })
}
