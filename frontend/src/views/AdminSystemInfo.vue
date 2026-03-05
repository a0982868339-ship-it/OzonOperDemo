<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 p-8 font-sans">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-slate-900 dark:text-white tracking-tight">系统信息 (System Info)</h1>
      <p class="text-slate-500 mt-2 text-sm font-medium">服务器运行状态 · 数据导出 · 一键操作</p>
    </div>

    <div class="grid grid-cols-12 gap-6">
      <!-- Left: Stats + Info -->
      <div class="col-span-8 space-y-6">
        <!-- Real-time stats -->
        <div class="grid grid-cols-4 gap-4">
          <div v-for="stat in statCards" :key="stat.label"
            class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">{{ stat.label }}</div>
            <div class="text-2xl font-bold font-mono" :class="stat.color">{{ stat.value }}</div>
          </div>
        </div>

        <!-- System version info -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6">
          <h3 class="text-base font-bold text-slate-900 dark:text-white mb-5 flex items-center gap-2">
            <span class="w-2 h-5 bg-blue-500 rounded-full"></span>应用信息
          </h3>
          <div class="grid grid-cols-2 gap-4">
            <div v-for="info in sysInfo" :key="info.label" class="flex justify-between py-3 border-b border-slate-100 dark:border-slate-700 last:border-0">
              <span class="text-sm text-slate-500">{{ info.label }}</span>
              <span class="text-sm font-bold font-mono text-slate-800 dark:text-slate-200">{{ info.value }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Data Export + Actions -->
      <div class="col-span-4 space-y-5">
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6">
          <h3 class="text-base font-bold text-slate-900 dark:text-white mb-5 flex items-center gap-2">
            <span class="w-2 h-5 bg-emerald-500 rounded-full"></span>数据导出
          </h3>
          <div class="space-y-3">
            <a v-for="exp in exports" :key="exp.label" :href="exp.url" target="_blank"
              class="flex items-center justify-between p-4 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer group">
              <div class="flex items-center gap-3">
                <span class="text-xl">{{ exp.icon }}</span>
                <div>
                  <div class="text-sm font-bold text-slate-800 dark:text-slate-200">{{ exp.label }}</div>
                  <div class="text-xs text-slate-400">{{ exp.desc }}</div>
                </div>
              </div>
              <svg class="w-4 h-4 text-slate-400 group-hover:text-blue-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
            </a>
          </div>
        </div>

        <!-- Server time -->
        <div class="bg-slate-900 dark:bg-slate-950 rounded-2xl p-6 border border-slate-800 text-white">
          <div class="text-xs text-slate-400 uppercase tracking-wider mb-3">服务器时间 (UTC)</div>
          <div class="text-2xl font-mono font-bold text-emerald-400">{{ serverTime }}</div>
          <div class="text-xs text-slate-500 mt-2">运行时长: {{ uptime }}</div>
          <div class="mt-4 flex items-center gap-2 text-xs text-slate-400">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            服务在线运行中
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { apiGet } from '../api/client'
import { ElMessage } from 'element-plus'

const stats   = ref<any>({})
const info    = ref<any>({})
const serverTime = ref('--:--:--')
const uptime  = ref('--')
let timer: ReturnType<typeof setInterval>

const statCards = computed(() => [
  { label: '总用户数',   value: stats.value.total_users    ?? '--', color: 'text-slate-900 dark:text-white' },
  { label: 'VIP 会员',  value: stats.value.vip_users      ?? '--', color: 'text-amber-500' },
  { label: '今日采集',  value: stats.value.today_keywords ?? '--', color: 'text-blue-500' },
  { label: 'Token 消耗', value: fmtNum(stats.value.total_tokens ?? 0), color: 'text-indigo-500' },
])

const sysInfo = computed(() => [
  { label: '应用版本',    value: info.value.app_version    ?? '--' },
  { label: 'Python',      value: info.value.python_version ?? '--' },
  { label: '系统平台',   value: info.value.platform       ?? '--' },
  { label: '运行时长',   value: uptime.value },
])

const exports = [
  { label: '用户数据',     icon: '👤', desc: '所有用户基本信息 CSV',     url: '/admin/backup/export?table=users' },
  { label: '热词数据',     icon: '🔥', desc: '最新 5000 条热词 CSV',      url: '/admin/backup/export?table=keywords' },
  { label: '用量日志',     icon: '📊', desc: 'Token 调用明细 CSV',          url: '/admin/backup/export?table=usage' },
]

const fmtNum = (n: number) => n >= 1_000_000 ? (n/1_000_000).toFixed(1)+'M' : n >= 1000 ? (n/1000).toFixed(0)+'K' : String(n ?? 0)

const fetchData = async () => {
  try {
    const [s, i] = await Promise.all([
      apiGet<any>('/admin/system/stats'),
      apiGet<any>('/admin/system/info'),
    ])
    stats.value  = s
    info.value   = i
    uptime.value = i.uptime
  } catch { /* silent */ }
}

const tickTime = () => {
  serverTime.value = new Date().toISOString().slice(11, 19)
}

onMounted(() => {
  fetchData()
  tickTime()
  timer = setInterval(tickTime, 1000)
})
onUnmounted(() => clearInterval(timer))
</script>
