import request from './request'

export function getMaterialList(params) {
  return request({
    url: '/learning/materials/',
    method: 'get',
    params
  })
}

export function getMaterialDetail(id) {
  return request({
    url: `/learning/materials/${id}/`,
    method: 'get'
  })
}

export function createMaterial(data) {
  return request({
    url: '/learning/materials/',
    method: 'post',
    data
  })
}

export function updateMaterial(id, data) {
  return request({
    url: `/learning/materials/${id}/`,
    method: 'put',
    data
  })
}

export function deleteMaterial(id) {
  return request({
    url: `/learning/materials/${id}/`,
    method: 'delete'
  })
}

export function publishMaterial(id) {
  return request({
    url: `/learning/materials/${id}/publish/`,
    method: 'post'
  })
}

export function archiveMaterial(id) {
  return request({
    url: `/learning/materials/${id}/archive/`,
    method: 'post'
  })
}

export function batchDeleteMaterials(ids) {
  return request({
    url: '/learning/materials/bulk_delete/',
    method: 'post',
    data: { ids }
  })
}

export function getMyMaterials(params) {
  return request({
    url: '/learning/materials/my_materials/',
    method: 'get',
    params
  })
}

export function getStatistics() {
  return request({
    url: '/learning/materials/statistics/',
    method: 'get'
  })
}

export function toggleLike(id) {
  return request({
    url: `/learning/materials/${id}/toggle_like/`,
    method: 'post'
  })
}

export function toggleFavorite(id) {
  return request({
    url: `/learning/materials/${id}/toggle_favorite/`,
    method: 'post'
  })
}

export function getMyFavorites(params) {
  return request({
    url: '/learning/materials/my_favorites/',
    method: 'get',
    params
  })
}
