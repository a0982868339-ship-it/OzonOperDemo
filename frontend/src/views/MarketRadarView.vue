<script setup lang="ts">
import { ref, onMounted, watch } from "vue"
import * as echarts from "echarts"
import { useRadarStore } from "../stores/radar"
import { useThemeStore } from "../stores/theme"
import { storeToRefs } from "pinia"
import { ElMessage } from 'element-plus'

const themeStore = useThemeStore()
const { isDark } = storeToRefs(themeStore)
const radarStore = useRadarStore()
// Fix: Destructure platforms from storeToRefs to ensure reactivity
const { filteredWords, platforms } = storeToRefs(radarStore)

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const selectedWord = ref<string | null>(null)
const analysisLoading = ref(false)
const analysisResult = ref<string | null>(null)

// Initialize Chart
const initChart = () => {
  if (!chartRef.value) return
  // Init ECharts with dark/light theme
  chartInstance = echarts.init(chartRef.value, isDark.value ? 'dark' : undefined)
  
  chartInstance.on('click', (params: any) => {
    // Only drill down/analyze leaf nodes
    if (params.data && params.data.value) {
        handleWordClick(params.data.name, params.data.growth)
    }
  })

  renderChart()
}

// Watch theme changes
watch(isDark, () => {
  if (chartInstance) {
    chartInstance.dispose()
    initChart()
  }
})

// Category emoji prefix map for visual richness
const CATEGORY_ICONS: Record<string, string> = {
  '宠物用品': '🐾',
  '智能家居': '🏠',
  '母婴':    '👶',
  '电子配件': '📱',
  '家居百货': '🛒',
  'general': '📦',
}

// Transform Data for Treemap — group by CATEGORY (product domain)
const transformDataForTreemap = (words: any[]) => {
  const groups: Record<string, any[]> = {}

  words.forEach(w => {
    const cat = w.category || 'general'
    const icon = CATEGORY_ICONS[cat] || '📦'
    const groupKey = `${icon} ${cat}`
    if (!groups[groupKey]) groups[groupKey] = []
    groups[groupKey].push({
      name: w.name,
      value: w.value,
      growth: w.growth_rate,
      path: groupKey + '/' + w.name
    })
  })

  return Object.entries(groups).map(([name, children]) => ({ name, children }))
}

// Render Chart Logic (Treemap)
const renderChart = () => {
  if (!chartInstance) return

  const treeData = transformDataForTreemap(filteredWords.value)

  chartInstance.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      formatter: (params: any) => {
        const d = params.data
        if (!d || !d.value) return ''
        return `
          <div class="font-bold text-lg mb-1">${d.name}</div>
          <div class="flex justify-between gap-4">
            <span>🔥 热度值 (Size):</span>
            <span class="font-mono font-bold">${d.value}</span>
          </div>
          <div class="flex justify-between gap-4">
            <span>📈 增长率 (Color):</span>
            <span class="font-mono font-bold" style="color:${d.growth > 0 ? '#10b981' : '#ef4444'}">
                ${(d.growth * 100).toFixed(0)}%
            </span>
          </div>
          <div class="text-xs text-slate-400 mt-2">点击下钻分析</div>
        `
      }
    },
    series: [{
      type: 'treemap',
      visibleMin: 300,
      label: {
        show: true,
        formatter: '{b}',
        fontSize: 14,
        fontWeight: 'bold',
        color: '#fff' // Always white text on colored tiles
      },
      itemStyle: {
        borderColor: isDark.value ? '#1e293b' : '#fff',
        borderWidth: 2,
        gapWidth: 2
      },
      levels: [
        {
          itemStyle: {
            borderColor: isDark.value ? '#0f172a' : '#f8fafc',
            borderWidth: 4,
            gapWidth: 4
          },
          upperLabel: {
            show: true,
            height: 30,
            color: isDark.value ? '#e2e8f0' : '#334155',
            fontWeight: 'bold',
            fontSize: 16
          }
        },
        {
          colorSaturation: [0.35, 0.5],
          itemStyle: {
            borderWidth: 2,
            gapWidth: 2,
            borderColorSaturation: 0.6
          }
        }
      ],
      data: treeData,
      // Color Mapping based on Growth Rate
      // We manually color the leaf nodes using a visualMap logic or custom color callback
      // But Treemap usually colors by hierarchy. Let's try visualMap for growth.
    }],
    visualMap: {
        min: -0.5,
        max: 1.5,
        dimension: 2, // Assuming growth is dimension index, but Treemap data struct is object.
        // ECharts Treemap uses 'value' for size. For color, we need to map a custom property.
        // Alternatively, use color callback in data item.
        show: true,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: 20,
        inRange: {
            color: ['#ef4444', '#f59e0b', '#10b981'] // Red (Low) -> Amber -> Green (High)
            // Wait, for "Hot" trends, usually Red is Hot. Let's flip or use Crypto style.
            // Crypto: Green = Up, Red = Down.
            // Let's stick to Green = High Growth, Red = Negative/Low Growth.
        },
        textStyle: {
            color: isDark.value ? '#cbd5e1' : '#475569'
        }
    }
  })
  
  // Custom Color injection because visualMap on treemap structure is tricky
  // We'll update the series data to include color directly
  const coloredData = treeData.map(group => ({
      ...group,
      children: group.children.map(child => ({
          ...child,
          itemStyle: {
              color: getGrowthColor(child.growth)
          }
      }))
  }))
  
  chartInstance.setOption({
      series: [{ data: coloredData }],
      visualMap: { show: false } // Hide visualMap if we manual color
  })
}

// Crypto-style Color Logic: Green = Good/Up, Red = Bad/Down
const getGrowthColor = (growth: number) => {
  // Green intensity for positive growth
  if (growth > 1.0) return '#059669' // Emerald-600 (Super High)
  if (growth > 0.5) return '#10b981' // Emerald-500
  if (growth > 0.0) return '#34d399' // Emerald-400
  
  // Gray for neutral
  if (growth === 0) return '#64748b' 
  
  // Red for negative
  return '#ef4444' // Red-500
}

// Handle Word Click -> Trigger Linguistic Agent
const handleWordClick = async (word: string, growth: number) => {
  selectedWord.value = word
  analysisLoading.value = true
  analysisResult.value = null

  // Simulate WebSocket/API call to Linguistic Agent
  setTimeout(() => {
    analysisResult.value = `
      **"${word}" 深度分析报告**
      
      1. **语义背景**: 在俄罗斯社交媒体上，该词通常与“${growth > 0.8 ? '急需解决的痛点' : '日常护理'}”相关。
      2. **电商应用**: 建议在 Ozon 标题中结合 "${word} + 自动/智能" 组合。
      3. **竞品缺口**: 现有 Top 10 商品中，仅 20% 强调了“静音”特性，这是蓝海切入点。
    `
    analysisLoading.value = false
    ElMessage.success('Linguistic Agent 分析完成')
  }, 1500)
}

// Watchers
watch(filteredWords, () => {
  renderChart()
}, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => chartInstance?.resize())
  // Fetch real data from backend. Falls back to mock automatically.
  radarStore.fetchRadarData()
})
</script>

<template>
  <div class="h-screen bg-slate-50 dark:bg-slate-900 flex flex-col font-sans overflow-hidden transition-colors duration-300">
    
    <!-- Header -->
    <header class="px-8 py-6 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center z-10 shadow-sm transition-colors duration-300">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-3">
          <span class="w-3 h-8 bg-indigo-600 rounded-full"></span>
          选品雷达 (Market Radar)
        </h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1 pl-6 font-medium">Market Treemap · 市场权重与增长热力图</p>
      </div>
      <div class="flex items-center gap-4">
         <div class="flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600">
           <span class="w-2 h-2 rounded-full animate-pulse" :class="radarStore.dataSource === 'live' ? 'bg-emerald-500' : 'bg-slate-400'"></span>
           <span class="text-xs font-bold text-slate-600 dark:text-slate-300">
             {{ radarStore.dataSource === 'live' ? 'LIVE DATA' : 'DEMO DATA' }}
           </span>
           <span v-if="radarStore.lastUpdated" class="text-xs text-slate-400">({{ radarStore.lastUpdated }})</span>
         </div>
      </div>
    </header>

    <div class="flex-1 flex overflow-hidden">
      
      <!-- Left: Filter Slicers -->
      <aside class="w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 p-6 flex flex-col gap-6 z-10 transition-colors duration-300">
        <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Data Sources</div>
        <div class="space-y-3">
          <div 
            v-for="(platform, idx) in platforms" 
            :key="platform.name"
            @click="radarStore.togglePlatform(idx)"
            class="flex items-center justify-between p-3 rounded-xl border transition-all cursor-pointer select-none group"
            :class="platform.active 
              ? 'bg-slate-50 dark:bg-slate-700 border-slate-300 dark:border-slate-600 shadow-sm' 
              : 'bg-white dark:bg-slate-800 border-slate-100 dark:border-slate-700 opacity-60 hover:opacity-100'"
          >
            <div class="flex items-center gap-3">
              <span 
                class="w-3 h-3 rounded-full transition-colors"
                :style="{ backgroundColor: platform.active ? platform.color : '#cbd5e1' }"
              ></span>
              <span class="font-bold text-slate-700 dark:text-slate-200 text-sm">{{ platform.name }}</span>
            </div>
            
            <!-- Toggle Switch Visual -->
            <div 
              class="w-10 h-5 rounded-full relative transition-colors duration-300"
              :class="platform.active ? 'bg-slate-900 dark:bg-slate-950' : 'bg-slate-200 dark:bg-slate-600'"
            >
              <div 
                class="absolute top-1 w-3 h-3 bg-white rounded-full transition-transform duration-300"
                :class="platform.active ? 'left-6' : 'left-1'"
              ></div>
            </div>
          </div>
        </div>

        <div class="mt-auto p-4 bg-slate-900 dark:bg-black rounded-xl text-white">
          <div class="text-xs font-mono opacity-50 mb-2">UNIFIED SCORE</div>
          <div class="text-2xl font-bold font-mono text-emerald-400">98.4%</div>
          <div class="text-[10px] mt-1 opacity-70">Confidence Level</div>
        </div>
      </aside>

      <!-- Center: Treemap Canvas -->
      <main class="flex-1 relative bg-slate-50 dark:bg-slate-900 flex items-center justify-center overflow-hidden transition-colors duration-300">
        <!-- Background Grid -->
        <div class="absolute inset-0 bg-[radial-gradient(#e2e8f0_1px,transparent_1px)] dark:bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:24px_24px] opacity-30"></div>
        
        <div ref="chartRef" class="w-full h-full p-4 z-0"></div>

        <!-- Legend Overlay -->
        <div class="absolute bottom-8 right-8 flex gap-4 bg-white/90 dark:bg-slate-800/90 backdrop-blur-md p-3 rounded-xl border border-slate-200 dark:border-slate-700 shadow-lg text-xs font-bold transition-colors duration-300">
           <div class="flex items-center gap-2 text-emerald-600 dark:text-emerald-400">
             <span class="w-3 h-3 bg-emerald-500 rounded-sm"></span> High Growth
           </div>
           <div class="flex items-center gap-2 text-slate-500 dark:text-slate-400">
             <span class="w-3 h-3 bg-slate-500 rounded-sm"></span> Stable
           </div>
           <div class="flex items-center gap-2 text-red-500 dark:text-red-400">
             <span class="w-3 h-3 bg-red-500 rounded-sm"></span> Decline
           </div>
        </div>
      </main>

      <!-- Right: Analysis Panel (Slide-over) -->
      <aside class="w-96 bg-white dark:bg-slate-800 border-l border-slate-200 dark:border-slate-700 shadow-xl z-20 flex flex-col transition-transform duration-500 transform"
        :class="selectedWord ? 'translate-x-0' : 'translate-x-full'"
      >
        <div v-if="selectedWord" class="flex flex-col h-full">
          <div class="p-6 border-b border-slate-100 dark:border-slate-700 flex justify-between items-start bg-slate-50/50 dark:bg-slate-800/50">
             <div>
               <div class="text-xs font-bold text-slate-500 uppercase mb-1">Deep Dive Analysis</div>
               <h2 class="text-2xl font-bold text-slate-900 dark:text-white">{{ selectedWord }}</h2>
             </div>
             <button @click="selectedWord = null" class="p-2 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-full transition-colors">
               <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
             </button>
          </div>

          <div class="flex-1 p-6 overflow-y-auto">
             <div v-if="analysisLoading" class="flex flex-col items-center justify-center h-64 space-y-4">
               <div class="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
               <p class="text-sm font-bold text-slate-600 dark:text-slate-400 animate-pulse">Linguistic Agent is analyzing...</p>
             </div>
             
             <div v-else-if="analysisResult" class="prose prose-sm prose-slate dark:prose-invert">
                <div class="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800 rounded-xl p-4 mb-6">
                  <h3 class="text-indigo-900 dark:text-indigo-300 font-bold m-0 flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                    AI Insight
                  </h3>
                  <div class="mt-2 text-indigo-800 dark:text-indigo-200 leading-relaxed whitespace-pre-line">
                    {{ analysisResult }}
                  </div>
                </div>

                <div class="space-y-4">
                   <button class="w-full py-3 bg-slate-900 dark:bg-slate-700 text-white rounded-xl font-bold hover:bg-slate-800 dark:hover:bg-slate-600 transition-colors shadow-lg shadow-slate-200 dark:shadow-none">
                     一键生成相关文案
                   </button>
                   <button class="w-full py-3 bg-white dark:bg-transparent border-2 border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-xl font-bold hover:border-slate-300 dark:hover:border-slate-500 transition-colors">
                     查看 Ozon 竞品数据
                   </button>
                </div>
             </div>
          </div>
        </div>
      </aside>

    </div>
  </div>
</template>

<style scoped>
/* No extra styles needed, utilizing Tailwind utility classes */
</style>
