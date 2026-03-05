<script setup lang="ts">
import { ref, onMounted, watch } from "vue"
import * as echarts from "echarts"
import { useThemeStore } from "../stores/theme"
import { storeToRefs } from "pinia"
import { apiGet } from "../api/client"

const themeStore = useThemeStore()
const { isDark } = storeToRefs(themeStore)

const chartRef = ref<HTMLElement | null>(null)
const selectedCategory = ref("宠物用品")
let chartInstance: echarts.ECharts | null = null

const isLoadingKeywords = ref(false)
const dataSource = ref<'live' | 'mock'>('mock')

// Hot keyword list — initially mock, replaced by API data
const hotKeywords = ref([
  { word: "Автокормушка (自动喂食器)", score: 98, trend: "+120%" },
  { word: "Лежанка для кошек (猫窝)", score: 85, trend: "+45%" },
  { word: "Игрушка рыба (鱼玩具)", score: 72, trend: "+15%" },
  { word: "Шлейка для собак (狗胸背带)", score: 65, trend: "+8%" },
  { word: "Когтеточка (猫抓板)", score: 60, trend: "-5%" },
])

const marketData = ref([
  { label: "平均售价", value: "₽ 2,450" },
  { label: "竞争强度", value: "中等", color: "text-yellow-600 dark:text-yellow-400" },
  { label: "月搜索量", value: "450K+" },
  { label: "转化率", value: "3.2%" }
])

const initChart = () => {
  if (!chartRef.value) return
  
  if (chartInstance) chartInstance.dispose()
  
  chartInstance = echarts.init(chartRef.value, isDark.value ? 'dark' : undefined)
  chartInstance.setOption({
    backgroundColor: 'transparent',
    title: { 
        text: '近30天搜索趋势', 
        left: 'center',
        textStyle: { color: isDark.value ? '#fff' : '#333' }
    },
    tooltip: { trigger: 'axis' },
    xAxis: { 
        type: 'category', 
        data: ['1日', '5日', '10日', '15日', '20日', '25日', '30日'],
        axisLabel: { color: isDark.value ? '#ccc' : '#666' }
    },
    yAxis: { 
        type: 'value',
        axisLabel: { color: isDark.value ? '#ccc' : '#666' },
        splitLine: { lineStyle: { color: isDark.value ? '#333' : '#eee' } }
    },
    series: [{
      data: [820, 932, 901, 934, 1290, 1330, 1320],
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.1 },
      itemStyle: { color: '#2563eb' }
    }]
  })
}

const fetchKeywords = async () => {
  isLoadingKeywords.value = true
  try {
    const catParam = selectedCategory.value ? `&category=${encodeURIComponent(selectedCategory.value)}` : ''
    const res = await apiGet(`/trends/analysis?limit=8${catParam}`)
    if (res && res.keywords && res.keywords.length > 0) {
      hotKeywords.value = res.keywords
      dataSource.value = res.source === 'live' ? 'live' : 'mock'
    }
  } catch (e) {
    // silently keep mock data
  } finally {
    isLoadingKeywords.value = false
  }
}

watch(isDark, () => {
    initChart()
})

watch(selectedCategory, () => {
    fetchKeywords()
})

onMounted(() => {
    initChart()
    fetchKeywords()
    window.addEventListener("resize", () => chartInstance?.resize())
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 p-8 font-sans transition-colors duration-300">
    <header class="mb-8">
      <h1 class="text-3xl font-bold text-slate-900 dark:text-white">数据选品分析 (Selection)</h1>
      <p class="text-slate-500 dark:text-slate-400 mt-2">基于 Ozon/WB 大盘数据的选品决策支持</p>
    </header>

    <div class="grid grid-cols-12 gap-6">
      <!-- Left: Filter & Hot Keywords -->
      <div class="col-span-4 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 transition-colors duration-300">
        <h2 class="text-lg font-bold text-slate-900 dark:text-white mb-4">热门类目筛选</h2>
        <select v-model="selectedCategory" class="w-full px-4 py-2 border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white rounded-xl mb-6 focus:outline-none focus:border-blue-500">
          <option>宠物用品</option>
          <option>家居收纳</option>
          <option>消费电子</option>
          <option>母婴玩具</option>
        </select>

        <h3 class="text-sm font-bold text-slate-500 dark:text-slate-400 uppercase mb-3">飙升热词 Top 5</h3>
        <div class="space-y-3">
          <div v-for="(item, i) in hotKeywords" :key="i" class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700/50 rounded-xl border border-slate-100 dark:border-slate-700 hover:border-blue-200 dark:hover:border-blue-500 transition-colors cursor-pointer group">
            <div class="flex items-center gap-3">
              <span class="w-6 h-6 flex items-center justify-center rounded-full bg-slate-200 dark:bg-slate-600 text-xs font-bold text-slate-600 dark:text-slate-300 group-hover:bg-blue-600 group-hover:text-white transition-colors">{{ i + 1 }}</span>
              <span class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ item.word }}</span>
            </div>
            <span class="text-xs font-bold text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/30 px-2 py-1 rounded">{{ item.trend }}</span>
          </div>
        </div>
      </div>

      <!-- Right: Charts & Analysis -->
      <div class="col-span-8 space-y-6">
        <!-- Key Metrics -->
        <div class="grid grid-cols-4 gap-4">
          <div v-for="(metric, i) in marketData" :key="i" class="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm transition-colors duration-300">
            <div class="text-xs text-slate-500 dark:text-slate-400 mb-1">{{ metric.label }}</div>
            <div class="text-xl font-bold text-slate-900 dark:text-white" :class="metric.color">{{ metric.value }}</div>
          </div>
        </div>

        <!-- Main Chart -->
        <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm transition-colors duration-300">
          <div ref="chartRef" class="w-full h-80"></div>
        </div>

        <!-- AI Insight -->
        <div class="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-2xl border border-blue-100 dark:border-blue-800 flex items-start gap-4 transition-colors duration-300">
          <div class="w-10 h-10 rounded-full bg-blue-600 flex-shrink-0 flex items-center justify-center text-white">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          </div>
          <div>
            <h3 class="font-bold text-blue-900 dark:text-blue-100 mb-1">AI 选品建议</h3>
            <p class="text-sm text-blue-800 dark:text-blue-200 leading-relaxed">
              当前“自动喂食器”处于需求上升期，且头部品牌垄断度未饱和。建议切入 <strong>带摄像头 + APP控制</strong> 的中高端款式（定价 ₽3000-4500），并重点在 VK 进行“出差/加班”场景的种草推广。
            </p>
            <button class="mt-3 px-4 py-2 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700 transition-colors">
              一键生成该商品全案
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
