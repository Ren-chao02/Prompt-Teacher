import request from './request'

export function getScenarioList(params) {
  return request({
    url: '/practice/scenarios/',
    method: 'get',
    params
  })
}

export function getScenarioDetail(id) {
  return request({
    url: `/practice/scenarios/${id}/`,
    method: 'get'
  })
}

export function createScenario(data) {
  return request({
    url: '/practice/scenarios/',
    method: 'post',
    data
  })
}

export function updateScenario(id, data) {
  return request({
    url: `/practice/scenarios/${id}/`,
    method: 'put',
    data
  })
}

export function deleteScenario(id) {
  return request({
    url: `/practice/scenarios/${id}/`,
    method: 'delete'
  })
}

export function publishScenario(id, action = 'publish') {
  return request({
    url: `/practice/scenarios/${id}/publish/`,
    method: 'post',
    data: { action }
  })
}

export function getTopicList(params) {
  return request({
    url: '/practice/topics/',
    method: 'get',
    params
  })
}

export function getTopicsByScenario(scenarioId) {
  return request({
    url: `/practice/topics/by_scenario/?scenario_id=${scenarioId}`,
    method: 'get'
  })
}

export function getTopicDetail(id) {
  return request({
    url: `/practice/topics/${id}/`,
    method: 'get'
  })
}

export function createTopic(data) {
  return request({
    url: '/practice/topics/',
    method: 'post',
    data
  })
}

export function updateTopic(id, data) {
  return request({
    url: `/practice/topics/${id}/`,
    method: 'put',
    data
  })
}

export function deleteTopic(id) {
  return request({
    url: `/practice/topics/${id}/`,
    method: 'delete'
  })
}

export function getRecordList(params) {
  return request({
    url: '/practice/records/',
    method: 'get',
    params
  })
}

export function getRecordDetail(id) {
  return request({
    url: `/practice/records/${id}/`,
    method: 'get'
  })
}

export function createRecord(data) {
  return request({
    url: '/practice/records/',
    method: 'post',
    data
  })
}

export function updateRecord(id, data) {
  return request({
    url: `/practice/records/${id}/`,
    method: 'put',
    data
  })
}

export function deleteRecord(id) {
  return request({
    url: `/practice/records/${id}/`,
    method: 'delete'
  })
}

export function getMyRecords(params) {
  return request({
    url: '/practice/records/my_records/',
    method: 'get',
    params
  })
}

export function getPracticeStatistics() {
  return request({
    url: '/practice/records/statistics/',
    method: 'get',
    showError: false
  })
}
