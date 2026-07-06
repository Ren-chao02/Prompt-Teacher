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
  smooth: {
    type: Boolean,
    default: true
  },
  showArea: {
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
    axisPointer: { type: 'cross' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: props.xAxisData,
    boundaryGap: false
  },
  yAxis: {
    type: 'value',
    name: ''
  },
  series: [{
    data: props.seriesData,
    type: 'line',
    smooth: props.smooth,
    areaStyle: props.showArea ? {
      opacity: 0.3
    } : undefined,
    itemStyle: {
      color: '#409EFF'
    },
    lineStyle: {
      width: 2
    }
  }]
}))
</script>
