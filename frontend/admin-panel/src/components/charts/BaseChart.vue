<template>
  <div ref="chartRef" :style="{ width: '100%', height: height }"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: {
    type: Object,
    required: true,
    default: () => ({})
  },
  height: {
    type: String,
    default: '400px'
  },
  autoResize: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['chart-ready', 'click'])

const chartRef = ref(null)
let chartInstance = null

const initChart = () => {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  
  if (props.option) {
    chartInstance.setOption(props.option)
  }
  
  // 点击事件
  chartInstance.on('click', (params) => {
    emit('click', params)
  })
  
  emit('chart-ready', chartInstance)
}

const updateChart = () => {
  if (!chartInstance) return
  nextTick(() => {
    chartInstance.setOption(props.option, true)
  })
}

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

watch(() => props.option, updateChart, { deep: true })

onMounted(() => {
  initChart()
  
  if (props.autoResize) {
    window.addEventListener('resize', handleResize)
  }
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  
  if (props.autoResize) {
    window.removeEventListener('resize', handleResize)
  }
})

defineExpose({
  getInstance: () => chartInstance,
  resize: handleResize
})
</script>

<style scoped>
/* ECharts 容器样式 */
</style>
