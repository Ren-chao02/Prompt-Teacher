import request from './request'

export function loginApi(data) {
  return request({
    url: '/auth/login/',
    method: 'post',
    data
  })
}

export function logoutApi(data) {
  return request({
    url: '/auth/logout/',
    method: 'post',
    data
  })
}

export function getUserInfoApi() {
  return request({
    url: '/auth/me/',
    method: 'get'
  })
}

export function changePasswordApi(data) {
  return request({
    url: '/auth/password/change/',
    method: 'post',
    data
  })
}
