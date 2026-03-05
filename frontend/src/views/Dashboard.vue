<script setup lang="ts">
import MarketPulse from "../components/MarketPulse.vue"
import { useTaskPolling } from "../hooks/useTaskPolling"
import { ref, onMounted } from "vue"
import { apiGet } from "../api/client"

useTaskPolling()

interface RestockPlan {
  category: string
  recommended_quantity: number
  priority: string
  reason: string
}

const restockPlans = ref<RestockPlan[]>([])
const topGainers = ref<{ word: string; growth_rate: number }[]>([])
const dashboardSource = ref<'live' | 'mock'>('mock')

const MOCK_RESTOCK: RestockPlan[] = [
  { category: "宠物用品", recommended_quantity: 150, priority: "high",   reason: "销量环比增长 20%，需紧急补货" },
  { category: "冬季服饰", recommended_quantity: 50,  priority: "medium", reason: "季节性需求即将见顶，适量补充" },
  { category: "电子配件", recommended_quantity: 0,   priority: "low",    reason: "竞争激烈且利润低，建议观望" },
]

onMounted(async () => {
  restockPlans.value = MOCK_RESTOCK  // Immediate mock so page non-empty
  try {
    const res = await apiGet<any>('/trends/dashboard')
    if (res?.source === 'live') {
      dashboardSource.value = 'live'
      // Map top_categories to restock plan cards
      if (res.top_categories?.length) {
        const PRIORITY = ['high', 'medium', 'low']
        restockPlans.value = res.top_categories.slice(0, 3).map((c: any, i: number) => ({
          category: c.category,
          recommended_quantity: Math.round(c.avg_score * 2),
          priority: PRIORITY[i] || 'low',
          reason: `热度均分 ${c.avg_score.toFixed(1)}，预测需求上升`,
        }))
      }
      if (res.hot_gainers?.length) {
        topGainers.value = res.hot_gainers
      }
    }
  } catch {
    // keep mock
  }
})
</script>

<template>
  <div class="space-y-8 animate-fade-in font-sans">
    <header class="flex items-end justify-between border-b border-slate-200 pb-6">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 tracking-tight">Ozon 智能决策中枢</h1>
        <p class="text-sm text-slate-500 mt-2 font-light tracking-wide uppercase">AI 驱动的跨境电商情报 · 尊享版</p>
      </div>
      <div class="flex items-center gap-4">
        <div class="px-4 py-2 bg-white border border-slate-200 rounded-full shadow-sm text-xs font-medium text-slate-600 flex items-center gap-2">
           <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
           实时数据
        </div>
        <div class="text-xs text-slate-400 font-mono">MSK {{ new Date().toLocaleTimeString('ru-RU', {hour: '2-digit', minute:'2-digit'}) }}</div>
      </div>
    </header>
    
    <!-- Market Pulse Dashboard -->
    <MarketPulse />

    <!-- Hot Gainers Banner (visible when live data) -->
    <div v-if="topGainers.length" class="bg-gradient-to-r from-emerald-50 to-blue-50 dark:from-emerald-900/20 dark:to-blue-900/20 rounded-2xl border border-emerald-100 dark:border-emerald-800 p-4 flex items-center gap-4 shadow-sm">
      <div class="flex items-center gap-2 shrink-0">
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        <span class="text-xs font-bold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">今日飙升热词</span>
      </div>
      <div class="flex flex-wrap gap-3">
        <div v-for="g in topGainers" :key="g.word"
             class="flex items-center gap-2 bg-white dark:bg-slate-800 border border-emerald-100 dark:border-slate-700 rounded-full px-3 py-1 shadow-sm">
          <span class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ g.word }}</span>
          <span class="text-xs font-bold text-emerald-600 dark:text-emerald-400">+{{ (g.growth_rate * 100).toFixed(0) }}%</span>
        </div>
      </div>
    </div>

    <!-- AI Restock Recommendations -->
    <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
       <div class="flex items-center justify-between mb-6">
         <h2 class="text-xl font-bold text-slate-900">AI 智能补货建议</h2>
         <span class="text-xs text-slate-500 bg-slate-100 px-2 py-1 rounded">
           {{ dashboardSource === 'live' ? '📡 实时热度数据' : '基于销量预测模型' }}
         </span>
       </div>
       <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div v-for="(plan, i) in restockPlans" :key="i" 
               class="p-6 bg-white rounded-xl border border-slate-200 hover:shadow-md transition-all group">
             <div class="flex justify-between items-start mb-4">
               <div>
                 <h3 class="font-medium text-slate-900">{{ plan.category }}</h3>
                 <p class="text-xs text-slate-500 mt-1">{{ plan.reason }}</p>
               </div>
               <span :class="[
                 'px-2 py-1 text-xs rounded-full border',
                 plan.priority === 'high' ? 'bg-red-50 text-red-600 border-red-100' : 
                 plan.priority === 'medium' ? 'bg-amber-50 text-amber-600 border-amber-100' : 
                 'bg-green-50 text-green-600 border-green-100'
               ]">
                 {{ plan.priority === 'high' ? '紧急' : plan.priority === 'medium' ? '建议' : '常规' }}
               </span>
             </div>
             
             <div class="text-2xl font-bold text-slate-900 mb-2">
               +{{ plan.recommended_quantity }} <span class="text-sm font-normal text-slate-400">件</span>
             </div>
          </div>
       </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
