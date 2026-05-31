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
  data: {
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
  showLegend: {
    type: Boolean,
    default: true
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
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: props.showLegend ? {
    orient: 'vertical',
    left: 'left',
    top: 'middle'
  } : undefined,
  series: [{
    name: props.title || '分布',
    type: 'pie',
    radius: ['40%', '70%'],
    avoidLabelOverlap: false,
    itemStyle: {
      borderRadius: 10,
      borderColor: '#fff',
      borderWidth: 2
    },
    label: {
      show: true,
      formatter: '{b}: {d}%'
    },
    emphasis: {
      label: {
        show: true,
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    labelLine: {
      show: true
    },
    data: props.data.map(item => ({
      name: item.name || item.label,
      value: item.value || item.count
    }))
  }]
}))
</script>
