<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 p-8 font-sans">
    <div class="flex justify-between items-end mb-8">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white tracking-tight">API 用量统计 (Usage)</h1>
        <p class="text-slate-500 mt-2 text-sm font-medium">Token 消耗与成本分析 · 用户额度监控</p>
      </div>
      <div class="flex items-center gap-3">
        <select v-model="days" @change="fetchData" class="px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm dark:text-white focus:outline-none">
          <option :value="7">近 7 天</option>
          <option :value="30">近 30 天</option>
        </select>
        <a href="/admin/backup/export?table=usage" target="_blank" class="px-4 py-2 bg-slate-900 dark:bg-blue-600 text-white rounded-xl text-sm font-bold hover:opacity-80 transition">⬇ 导出 CSV</a>
      </div>
    </div>

    <!-- Overview Cards -->
    <div class="grid grid-cols-3 gap-6 mb-8">
      <div class="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
        <div class="text-xs font-bold opacity-80 uppercase tracking-wider mb-2">总消耗成本 (Est.)</div>
        <div class="text-4xl font-bold font-mono">${{ summary.total_cost.toFixed(4) }}</div>
        <div class="mt-3 text-sm opacity-80">{{ summary.total_calls }} 次 API 调用</div>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
        <div class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">总 Token 消耗</div>
        <div class="text-4xl font-bold font-mono text-slate-900 dark:text-white">{{ fmtNum(summary.total_tokens) }}</div>
        <div class="mt-3 text-sm text-slate-500">All Agents 合计</div>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
        <div class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Agent 数量</div>
        <div class="text-4xl font-bold font-mono text-slate-900 dark:text-white">{{ totals.length }}</div>
        <div class="mt-3 text-sm text-slate-500">活跃 Agent</div>
      </div>
    </div>

    <div class="grid grid-cols-12 gap-6">
      <!-- Left: Agent breakdown -->
      <div class="col-span-7 space-y-6">
        <!-- Agent usage bars -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6">
          <h3 class="text-base font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
            <span class="w-2 h-5 bg-indigo-500 rounded-full"></span>Agent Token 消耗排行
          </h3>
          <div v-if="totals.length === 0" class="py-10 text-center text-slate-400">
            <div class="text-4xl mb-3">📊</div>
            <div class="text-sm">暂无调用记录 · 开始使用 AI Agent 后将显示统计</div>
          </div>
          <div v-else class="space-y-5">
            <div v-for="t in totals" :key="t.agent">
              <div class="flex justify-between mb-1.5 text-sm">
                <span class="font-bold text-slate-700 dark:text-slate-200">{{ t.agent }}</span>
                <span class="font-mono text-slate-500">{{ fmtNum(t.tokens) }} tokens · ${{ t.cost }}</span>
              </div>
              <div class="w-full h-2.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                <div class="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-700"
                  :style="{width: (maxTokens > 0 ? t.tokens/maxTokens*100 : 0) + '%'}"></div>
              </div>
              <div class="text-[10px] text-slate-400 mt-1">{{ t.calls }} 次调用</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: User quota -->
      <div class="col-span-5">
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 h-full">
          <h3 class="text-base font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
            <span class="w-2 h-5 bg-amber-500 rounded-full"></span>用户额度监控
          </h3>
          <div class="space-y-5">
            <div v-for="u in userQuota" :key="u.email">
              <div class="flex items-center justify-between mb-1.5">
                <div class="flex items-center gap-2">
                  <div class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold text-white"
                    :class="u.role === 'admin' ? 'bg-purple-500' : u.role === 'operator' ? 'bg-blue-500' : 'bg-slate-400'">
                    {{ u.username.charAt(0).toUpperCase() }}
                  </div>
                  <span class="text-sm font-bold text-slate-700 dark:text-slate-200">{{ u.username }}</span>
                  <span v-if="u.is_vip" class="text-amber-400 text-xs">⭐</span>
                </div>
                <span v-if="u.token_quota < 0" class="text-emerald-500 text-xs font-bold">∞</span>
                <span v-else class="text-xs font-bold" :class="u.quota_pct >= 80 ? 'text-red-500' : 'text-slate-500'">{{ u.quota_pct }}%</span>
              </div>
              <div v-if="u.token_quota > 0" class="w-full h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all duration-500"
                  :class="u.quota_pct >= 80 ? 'bg-red-500' : u.quota_pct >= 50 ? 'bg-amber-500' : 'bg-emerald-500'"
                  :style="{width: Math.min(u.quota_pct, 100) + '%'}"></div>
              </div>
              <div class="text-[10px] text-slate-400 mt-0.5" v-if="u.token_quota > 0">
                {{ fmtNum(u.tokens_used) }} / {{ fmtNum(u.token_quota) }}
                <span v-if="u.quota_pct >= 80" class="text-red-400 font-bold ml-1">⚠ 超额预警</span>
              </div>
            </div>
            <div v-if="userQuota.length === 0" class="py-8 text-center text-slate-400 text-sm">暂无用户数据</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { apiGet } from '../api/client'
import { ElMessage } from 'element-plus'

const days = ref(7)
const summary   = ref({ total_tokens: 0, total_cost: 0, total_calls: 0 })
const totals    = ref<any[]>([])
const userQuota = ref<any[]>([])

const maxTokens = computed(() => Math.max(...totals.value.map(t => t.tokens), 1))

const fmtNum = (n: number) => n >= 1_000_000 ? (n/1_000_000).toFixed(2)+'M' : n >= 1000 ? (n/1000).toFixed(1)+'K' : String(n)

const fetchData = async () => {
  try {
    const res = await apiGet<any>(`/admin/system/usage?days=${days.value}`)
    summary.value   = res.summary
    totals.value    = res.totals
    userQuota.value = res.user_quota
  } catch { ElMessage.error('加载用量数据失败') }
}

onMounted(fetchData)
</script>
