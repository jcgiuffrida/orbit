<template>
  <div class="monthly-chart">
    <div v-if="!data || data.length === 0" class="text-body2 text-grey-6 text-center q-pa-lg">
      No activity data available
    </div>
    <div v-else>
      <highcharts 
        :options="chartOptions" 
        :style="{ height: '400px', width: '100%' }"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

const chartOptions = computed(() => {
  if (!props.data || props.data.length === 0) {
    return {}
  }

  // Extract categories (month names) and data series
  const categories = props.data.map(item => item.month_name)
  const conversationsData = props.data.map(item => item.conversations)
  const contactAttemptsData = props.data.map(item => item.contact_attempts)

  return {
    chart: {
      type: 'line',
      backgroundColor: 'transparent',
      spacingTop: 20,
      spacingBottom: 20,
      spacingLeft: 20,
      spacingRight: 20
    },
    title: {
      text: null
    },
    xAxis: {
      categories: categories,
      lineColor: '#e0e0e0',
      tickColor: '#e0e0e0',
      labels: {
        style: {
          color: '#666',
          fontSize: '12px'
        }
      }
    },
    yAxis: {
      title: {
        text: 'Count',
        style: {
          color: '#666'
        }
      },
      min: 0,
      gridLineColor: '#f0f0f0',
      labels: {
        style: {
          color: '#666',
          fontSize: '12px'
        }
      }
    },
    tooltip: {
      shared: true,
      backgroundColor: '#ffffff',
      borderColor: '#e0e0e0',
      borderRadius: 8,
      shadow: true,
      useHTML: true,
      formatter: function() {
        const monthName = this.points && this.points.length > 0 ? this.points[0].category : this.x
        let tooltipText = `<div style="text-align: center; margin-bottom: 5px; font-weight: bold;">${monthName}</div>`
        if (this.points) {
          this.points.forEach(point => {
            tooltipText += `<div style="margin: 2px 0;"><span style="color:${point.color}; font-size: 14px;">●</span> ${point.series.name}: <b>${point.y}</b></div>`
          })
        }
        return tooltipText
      }
    },
    legend: {
      align: 'center',
      verticalAlign: 'bottom',
      borderWidth: 0,
      itemStyle: {
        color: '#666',
        fontSize: '12px'
      }
    },
    plotOptions: {
      line: {
        lineWidth: 3,
        states: {
          hover: {
            lineWidth: 4
          }
        }
      }
    },
    series: [
      {
        name: 'Conversations',
        data: conversationsData,
        color: '#1976d2',
        marker: {
          fillColor: '#1976d2'
        }
      },
      {
        name: 'Pings',
        data: contactAttemptsData,
        color: '#424242',
        marker: {
          fillColor: '#424242'
        }
      }
    ],
    credits: {
      enabled: false
    },
    responsive: {
      rules: [{
        condition: {
          maxWidth: 500
        },
        chartOptions: {
          legend: {
            layout: 'horizontal',
            align: 'center',
            verticalAlign: 'bottom'
          },
          xAxis: {
            labels: {
              rotation: -45,
              style: {
                fontSize: '10px'
              }
            }
          }
        }
      }]
    }
  }
})
</script>

<style scoped>
.monthly-chart {
  width: 100%;
  min-height: 400px;
}
</style>