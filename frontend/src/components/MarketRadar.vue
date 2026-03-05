<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from "vue"
import * as echarts from "echarts"
import type { RadarItem } from "../types"
import { useMarketStore } from "../stores/market"
import { useTaskStore } from "../stores/tasks"

const chartRef = ref<HTMLDivElement | null>(null)
const chartInstance = ref<echarts.ECharts | null>(null)
const marketStore = useMarketStore()
const taskStore = useTaskStore()

const bubbleSize = (item: RadarItem): number => {
  const base = Math.max(1, item.index)
  return Math.min(40, 10 + base * 6)
}

const renderChart = (items: RadarItem[]): void => {
  if (!chartInstance.value) return
  const seriesData = items.map((item) => [
    item.supply,
    item.demand,
    bubbleSize(item),
    item.keyword,
    item.index,
    item.quadrant
  ])
  chartInstance.value.setOption({
    tooltip: {
      formatter: (params: any) =>
        `${params.data[3]}<br/>需求: ${params.data[1]}<br/>竞争: ${params.data[0]}<br/>指数: ${params.data[4]}`
    },
    xAxis: { name: "竞争指数", type: "value" },
    yAxis: { name: "需求热度", type: "value" },
    series: [
      {
        type: "scatter",
        data: seriesData,
        symbolSize: (val: number[]) => val[2],
        itemStyle: { color: "#005bff" }
      }
    ]
  })
}

const startGeneration = async () => {
  if (!marketStore.selected) return
  await taskStore.createSeoTask({
    product_name: marketStore.selected.keyword,
    category: marketStore.selected.quadrant
  })
  await taskStore.createMediaTask({
    base_prompt: `Product showcase of ${marketStore.selected.keyword}`
  })
}

onMounted(() => {
  if (!chartRef.value) return
  chartInstance.value = echarts.init(chartRef.value)
  renderChart(marketStore.radarItems)
  chartInstance.value.on("click", (params: any) => {
    const keyword = params.data?.[3]
    const match = marketStore.radarItems.find((item: RadarItem) => item.keyword === keyword)
    if (match) {
      marketStore.select(match)
    }
  })
})

watch(
  () => marketStore.radarItems,
  (items: RadarItem[]) => renderChart(items)
)

onBeforeUnmount(() => {
  chartInstance.value?.dispose()
})
</script>

<template>
  <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col gap-6">
    <div>
      <h2 class="text-lg font-semibold">选品象限</h2>
      <p class="text-sm text-slate-500">需求 vs 竞争，气泡大小 = 增长率</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2">
        <div ref="chartRef" class="h-80 w-full"></div>
      </div>
      <div class="rounded-xl border border-slate-200 p-4 bg-slate-50">
        <div class="text-sm font-semibold text-slate-700">商品指标</div>
        <div v-if="marketStore.selected" class="mt-4 space-y-2 text-sm text-slate-600">
          <div class="text-base font-semibold text-slate-900">{{ marketStore.selected.keyword }}</div>
          <div>需求热度: {{ marketStore.selected.demand }}</div>
          <div>竞争指数: {{ marketStore.selected.supply }}</div>
          <div>供需评分: {{ marketStore.selected.index }}</div>
          <div>象限: {{ marketStore.selected.quadrant }}</div>
        </div>
        <div v-else class="mt-4 text-sm text-slate-400">选择气泡查看详情</div>
        <el-button class="mt-4 w-full" type="primary" @click="startGeneration">
          开始 AI 生成
        </el-button>
      </div>
    </div>
  </div>
</template>
