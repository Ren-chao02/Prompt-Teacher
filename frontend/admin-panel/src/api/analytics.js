/**
 * 数据分析 API 接口
 */

import request from '@/api/request'

/**
 * 获取数据概览
 * @param {Object} params - 查询参数
 * @param {string} params.period - 时间范围 (7d/30d/90d)
 */
export function getAnalyticsOverview(params = {}) {
  return request({
    url: '/analytics/overview/',
    method: 'get',
    params: {
      period: '30d',
      ...params
    }
  })
}

/**
 * 获取学习进度分析
 * @param {Object} params - 查询参数
 * @param {string} params.user_id - 用户ID (可选)
 * @param {string} params.period - 时间范围
 * @param {string} params.category - 内容分类筛选
 */
export function getLearningProgress(params = {}) {
  return request({
    url: '/analytics/learning_progress/',
    method: 'get',
    params: {
      period: '30d',
      ...params
    }
  })
}

/**
 * 获取练习成绩统计
 * @param {Object} params - 查询参数
 * @param {string} params.user_id - 用户ID (可选)
 * @param {string} params.scenario_id - 场景ID (可选)
 * @param {string} params.score_level - 分数等级
 * @param {string} params.period - 时间范围
 */
export function getPracticeStatistics(params = {}) {
  return request({
    url: '/analytics/practice_statistics/',
    method: 'get',
    params: {
      period: '30d',
      ...params
    }
  })
}

/**
 * 导出数据分析结果
 * @param {Object} data - 导出参数
 * @param {string} data.format - 格式 (excel/csv/pdf)
 * @param {string} data.type - 数据类型 (overview/learning/practice)
 * @param {Object} data.filters - 筛选条件
 */
export function exportAnalyticsData(data) {
  return request({
    url: '/analytics/export/',
    method: 'post',
    data: {
      format: 'excel',
      type: 'overview',
      ...data
    }
  })
}
