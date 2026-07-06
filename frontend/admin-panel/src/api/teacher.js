/**
 * 教师工作台 API 接口
 */

import request from '@/api/request'

/**
 * 获取教师工作台概览数据
 * @param {Object} params - 查询参数
 * @param {number} params.class_id - 班级ID（可选）
 * @param {string} params.period - 时间范围 7d/30d/90d/all
 */
export function getWorkspaceData(params = {}) {
  return request({
    url: '/teacher/workspace/',
    method: 'get',
    params: {
      period: '30d',
      ...params
    }
  })
}

/**
 * 获取学生详情
 * @param {number} id - 学生用户ID
 * @param {Object} params - 查询参数
 * @param {string} params.period - 时间范围
 */
export function getStudentDetail(id, params = {}) {
  return request({
    url: `/teacher/student/${id}/`,
    method: 'get',
    params: {
      period: '30d',
      ...params
    }
  })
}
