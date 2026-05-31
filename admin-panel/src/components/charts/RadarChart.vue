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
  indicators: {
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
  }
})

defineEmits(['click'])

const chartOption = computed(() => ({
  title: props.title ? {
    text: props.title,
    left: 'center',
    textStyle: { fontSize: 16, fontWeight: 'bold' }
  } : undefined,
  tooltip: {},
  legend: {
    data: props.seriesData.map(s => s.name),
    bottom: 0
  },
  radar: {
    indicator: props.indicators.map(ind => ({
      name: ind.name || ind.text,
      max: ind.max || 100
    })),
    shape: 'polygon',
    splitNumber: 5,
    axisName: {
      color: '#666'
    },
    splitLine: {
      lineStyle: { color: '#ddd' }
    },
    splitArea: {
      areaStyle: { color: ['#f9f9f9', '#ffffff'] }
    }
  },
  series: [{
    type: 'radar',
    data: props.seriesData.map(series => ({
      name: series.name,
      value: series.value || series.data
    }))
  }]
}))
</script>
