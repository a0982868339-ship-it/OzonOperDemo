<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from "vue"
import * as echarts from "echarts"
import { useMarketStore } from "../stores/market"
import { apiGet } from "../api/client"

const exchangeRateChartRef = ref<HTMLDivElement | null>(null)
const heatmapChartRef = ref<HTMLDivElement | null>(null)
let exchangeRateChart: echarts.ECharts | null = null
let heatmapChart: echarts.ECharts | null = null

const marketStore = useMarketStore()

const hotKeywords = ref([
  { rank: 1, term: "Умная кормушка", trans: "智能喂食器", trend: "+12%" },
  { rank: 2, term: "Зимняя куртка", trans: "冬季夹克", trend: "+8%" },
  { rank: 3, term: "Термос", trans: "保温杯", trend: "+5%" },
  { rank: 4, term: "Наушники", trans: "无线耳机", trend: "+3%" },
  { rank: 5, term: "Кофемашина", trans: "咖啡机", trend: "+2%" }
])

// Fetch live hot keywords from backend
const fetchHotKeywords = async () => {
  try {
    const res = await apiGet<{ keywords: any[], source: string }>('/trends/analysis?limit=5')
    if (res?.keywords?.length) {
      hotKeywords.value = res.keywords.map((k: any, idx: number) => ({
        rank: idx + 1,
        term: k.word,
        trans: '',
        trend: k.trend || '+0%'
      }))
    }
  } catch {
    // silently keep mock data
  }
}

const policyAlerts = ref([
  "Ozon: FBO 发货新规生效，需提前预约入仓",
  "Wildberries: 3月春季大促活动报名通道开启",
  "海关总署: 跨境电商出口退税申报流程优化"
])

const renderExchangeRateChart = () => {
  if (!exchangeRateChartRef.value) return
  exchangeRateChart = echarts.init(exchangeRateChartRef.value)
  exchangeRateChart.setOption({
    grid: { top: 10, bottom: 0, left: -20, right: 0 },
    xAxis: { show: false, type: "category", data: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] },
    yAxis: { show: false, type: "value", min: 11.5, max: 13.5 },
    series: [{
      data: [12.1, 12.3, 12.0, 12.5, 12.8, 12.4, 12.6],
      type: "line",
      smooth: true,
      symbol: "circle",
      symbolSize: 6,
      itemStyle: { color: "#D4AF37", borderColor: "#fff", borderWidth: 2 },
      lineStyle: { width: 3, color: "#D4AF37" },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: "rgba(212, 175, 55, 0.2)" },
          { offset: 1, color: "rgba(212, 175, 55, 0)" }
        ])
      }
    }]
  })
}

const renderHeatmapChart = () => {
  if (!heatmapChartRef.value) return
  heatmapChart = echarts.init(heatmapChartRef.value)
  
  // Mock Heatmap Data
  const categories = ["Pet Supplies", "Winter Gear", "Electronics", "Home Decor", "Beauty", "Auto Parts", "Kids"]
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
  const data = categories.flatMap((cat, i) => 
    days.map((day, j) => [i, j, Math.floor(Math.random() * 100)])
  )

  heatmapChart.setOption({
    tooltip: { position: "top", backgroundColor: "rgba(255,255,255,0.9)", borderColor: "#E5E5E5", textStyle: { color: "#333" } },
    grid: { height: "70%", top: "10%" },
    xAxis: { type: "category", data: categories, splitArea: { show: true, areaStyle: { color: ['rgba(250,250,250,0.3)', 'rgba(200,200,200,0.02)'] } }, axisLine: { lineStyle: { color: "#999" } } },
    yAxis: { type: "category", data: days, splitArea: { show: true }, axisLine: { lineStyle: { color: "#999" } } },
    visualMap: {
      min: 0,
      max: 100,
      calculable: true,
      orient: "horizontal",
      left: "center",
      bottom: "0%",
      inRange: { color: ["#F9FAFB", "#D1D5DB", "#1E293B"] } // Grayscale/Navy premium look
    },
    series: [{
      name: "Discussion Volume",
      type: "heatmap",
      data: data,
      label: { show: false },
      itemStyle: {
        borderColor: '#fff',
        borderWidth: 1,
        emphasis: { shadowBlur: 10, shadowColor: "rgba(0, 0, 0, 0.2)" }
      }
    }]
  })
}

onMounted(() => {
  renderExchangeRateChart()
  renderHeatmapChart()
  fetchHotKeywords()
  window.addEventListener("resize", handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize)
  exchangeRateChart?.dispose()
  heatmapChart?.dispose()
})

const handleResize = () => {
  exchangeRateChart?.resize()
  heatmapChart?.resize()
}
</script>

<template>
  <div class="space-y-6 font-inter text-stone-800">
    <!-- Top Row: Metrics (Bento Grid) -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      
      <!-- Exchange Rate Card -->
      <div class="bg-white/80 backdrop-blur-xl border border-white/50 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-500 group relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-amber-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div class="relative z-10">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xs font-bold text-stone-400 uppercase tracking-widest">汇率 • RUB/CNY</h3>
            <span class="text-[10px] font-bold text-emerald-600 bg-emerald-50/80 px-2 py-0.5 rounded-full border border-emerald-100">+1.2%</span>
          </div>
          <div class="flex items-baseline gap-2 mb-6">
            <span class="text-4xl font-medium text-stone-900 tracking-tight">12.64</span>
            <span class="text-xs text-stone-400 font-medium">实时汇率</span>
          </div>
          <div ref="exchangeRateChartRef" class="h-16 w-full opacity-80 group-hover:opacity-100 transition-opacity"></div>
        </div>
      </div>

      <!-- Hot Keywords Card -->
      <div class="bg-white/80 backdrop-blur-xl border border-white/50 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-500 group relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-stone-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div class="relative z-10">
          <h3 class="text-xs font-bold text-stone-400 uppercase tracking-widest mb-5">热搜词 • VK/Ozon</h3>
          <ul class="space-y-4">
            <li v-for="item in hotKeywords" :key="item.rank" class="flex items-center justify-between group/item">
              <div class="flex items-center gap-4">
                <span class="flex items-center justify-center w-5 h-5 rounded-full bg-stone-100 text-stone-500 text-[10px] font-bold group-hover/item:bg-stone-800 group-hover/item:text-white transition-colors">{{ item.rank }}</span>
                <div class="flex flex-col">
                  <span class="text-sm text-stone-600 font-medium group-hover/item:text-stone-900 transition-colors">{{ item.term }}</span>
                  <span class="text-[10px] text-stone-400">{{ item.trans }}</span>
                </div>
              </div>
              <span class="text-[10px] text-stone-400 font-mono">{{ item.trend }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Policy Alerts Card -->
      <div class="bg-stone-900 text-white border border-stone-800 rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-all duration-500 relative overflow-hidden flex flex-col">
        <div class="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <h3 class="text-xs font-bold text-stone-500 uppercase tracking-widest mb-5">情报 • 政策预警</h3>
        <div class="flex-1 overflow-hidden relative">
          <div class="absolute inset-0 animate-marquee space-y-4">
            <div v-for="(alert, index) in policyAlerts" :key="index" class="p-4 bg-white/5 border-l-2 border-amber-500/50 backdrop-blur-sm rounded-r-lg hover:bg-white/10 transition-colors">
              <p class="text-xs text-stone-300 leading-relaxed font-light tracking-wide">{{ alert }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Core Component: Trending Heatmap -->
    <div class="bg-white/80 backdrop-blur-xl border border-white/50 rounded-2xl p-8 shadow-lg min-h-[450px] relative overflow-hidden">
      <div class="absolute top-0 right-0 w-64 h-64 bg-stone-100/50 rounded-full blur-3xl -z-10"></div>
      <div class="flex items-center justify-between mb-8">
        <div>
           <h2 class="text-xl font-bold text-stone-900 tracking-tight">社媒舆情热力图</h2>
           <p class="text-xs text-stone-500 mt-1 uppercase tracking-wider">周度分析 · 俄罗斯全网</p>
        </div>
        <div class="flex items-center gap-3 bg-stone-50 px-3 py-1.5 rounded-full border border-stone-200">
          <div class="flex gap-1">
             <span class="w-2 h-2 rounded-full bg-slate-200"></span>
             <span class="w-2 h-2 rounded-full bg-slate-400"></span>
             <span class="w-2 h-2 rounded-full bg-slate-800"></span>
          </div>
          <span class="text-[10px] text-stone-400 font-medium uppercase">热度指数</span>
        </div>
      </div>
      <div ref="heatmapChartRef" class="h-80 w-full"></div>
    </div>

    <!-- Floating Agent Bubble (Refined) -->
    <div class="fixed bottom-8 right-8 z-50 group">
      <div class="relative">
        <!-- Expanded Card -->
        <div class="absolute bottom-16 right-0 w-80 bg-white/95 backdrop-blur-2xl border border-stone-200 rounded-2xl shadow-2xl p-6 transform scale-0 opacity-0 group-hover:scale-100 group-hover:opacity-100 transition-all duration-500 origin-bottom-right ease-out">
          <div class="flex items-center gap-3 mb-4 border-b border-stone-100 pb-4">
            <div class="w-8 h-8 bg-stone-900 rounded-lg flex items-center justify-center text-amber-400 text-sm">✦</div>
            <div>
              <span class="block text-sm font-bold text-stone-900">每日简报</span>
              <span class="text-[10px] text-stone-400 uppercase tracking-wider">AI 自动生成</span>
            </div>
          </div>
          <div class="space-y-3">
             <div class="text-xs text-stone-600 leading-relaxed pl-3 border-l-2 border-emerald-500">
               <strong class="text-emerald-700 block mb-1">机会</strong>
               受莫斯科降温影响，宠物服饰需求激增 200%。
             </div>
             <div class="text-xs text-stone-600 leading-relaxed pl-3 border-l-2 border-red-500">
               <strong class="text-red-700 block mb-1">风险</strong>
               电子产品类目竞争加剧，建议优化广告投放。
             </div>
          </div>
        </div>

        <!-- Bubble Button -->
        <button class="w-14 h-14 bg-stone-900 text-amber-400 rounded-full shadow-2xl flex items-center justify-center hover:scale-110 transition-transform duration-300 hover:shadow-amber-500/20 border border-stone-700">
          <span class="text-xl">✦</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes marquee {
  0% { transform: translateY(0); }
  100% { transform: translateY(-100%); }
}
</style>
