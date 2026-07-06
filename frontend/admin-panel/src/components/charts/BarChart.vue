<template>
  <BaseChart
    :option="chartOption"
    :height="height"
    @click="$emit('click', $event)"
  />
</template>

<script setup>
import { computed } from 'vue'
import BaseChart from './BaseChart.vue'

const props = defineProps({
  xAxisData: {
    type: Array,
    default: () => []
  },
  seriesData: {
    type: Array,
    default: () => []
  },
  title: {
    type: String,
    default: ''
  },
  height: {
    type: String,
    default: '400px'
  },
  horizontal: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click'])

const chartOption = computed(() => ({
  title: props.title ? {
    text: props.title,
    left: 'center',
    textStyle: { fontSize: 16, fontWeight: 'bold' }
  } : undefined,
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: props.horizontal ? {
    type: 'value'
  } : {
    type: 'category',
    data: props.xAxisData,
    axisLabel: {
      rotate: props.xAxisData.length > 8 ? 45 : 0
    }
  },
  yAxis: props.horizontal ? {
    type: 'category',
    data: props.xAxisData
  } : {
    type: 'value'
  },
  series: [{
    data: props.seriesData,
    type: 'bar',
    itemStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: '#409EFF' },
        { offset: 1, color: '#79bbff' }
      ]),
      borderRadius: [4, 4, 0, 0]
    },
    barWidth: props.xAxisData.length > 10 ? '60%' : '50%'
  }]
}))
</script>

<script>
import * as echarts from 'echarts'
</script>
