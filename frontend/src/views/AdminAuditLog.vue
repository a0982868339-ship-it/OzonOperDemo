<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 p-8 font-sans">
    <div class="flex justify-between items-end mb-8">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white tracking-tight">审计日志 (Audit Log)</h1>
        <p class="text-slate-500 mt-2 text-sm font-medium">记录所有管理员操作 · 共 {{ total }} 条</p>
      </div>
      <a href="/admin/backup/export?table=users" target="_blank"
        class="px-4 py-2 bg-slate-900 dark:bg-slate-700 text-white rounded-xl text-sm font-bold hover:opacity-80 transition">⬇ 导出用户 CSV</a>
    </div>

    <div class="flex gap-3 mb-6">
      <input v-model="filterOp" placeholder="过滤操作员…"
        class="px-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:outline-none dark:text-white w-48" />
      <input v-model="filterAction" placeholder="过滤操作类型…"
        class="flex-1 px-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:outline-none dark:text-white" />
    </div>

    <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
      <div v-if="loading" class="p-12 flex justify-center">
        <div class="w-8 h-8 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
      </div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr class="border-b border-slate-100 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/80">
            <th class="text-left px-5 py-3.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">时间</th>
            <th class="text-left px-5 py-3.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">操作员</th>
            <th class="text-left px-5 py-3.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">操作</th>
            <th class="text-left px-5 py-3.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">目标</th>
            <th class="text-left px-5 py-3.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">详情</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
          <tr v-for="log in filtered" :key="log.id" class="hover:bg-slate-50/60 dark:hover:bg-slate-700/40 transition-colors">
            <td class="px-5 py-3 text-xs text-slate-400 whitespace-nowrap font-mono">{{ fmtDate(log.created_at) }}</td>
            <td class="px-5 py-3 text-sm font-bold text-slate-700 dark:text-slate-200">{{ log.operator }}</td>
            <td class="px-5 py-3">
              <span :class="['px-2 py-0.5 text-[10px] font-bold rounded font-mono', actionStyle(log.action)]">{{ log.action }}</span>
            </td>
            <td class="px-5 py-3 text-xs text-slate-500 font-mono">{{ log.target }}</td>
            <td class="px-5 py-3 text-xs text-slate-400 max-w-xs truncate">{{ log.detail }}</td>
          </tr>
          <tr v-if="filtered.length === 0">
            <td colspan="5" class="py-16 text-center text-slate-400">
              <div class="text-3xl mb-3">📋</div><div class="text-sm">暂无审计记录</div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="total > perPage" class="px-5 py-4 border-t border-slate-100 dark:border-slate-700 flex justify-between items-center text-sm">
        <span class="text-slate-400">第 {{ page }} 页 · 共 {{ total }} 条</span>
        <div class="flex gap-2">
          <button @click="prevPage" :disabled="page <= 1" class="px-3 py-1 rounded-lg border text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-600 disabled:opacity-40 hover:bg-slate-50 transition">上一页</button>
          <button @click="nextPage" :disabled="page * perPage >= total" class="px-3 py-1 rounded-lg border text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-600 disabled:opacity-40 hover:bg-slate-50 transition">下一页</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { apiGet } from '../api/client'
import { ElMessage } from 'element-plus'

const logs = ref<any[]>([])
const loading = ref(true)
const page = ref(1)
const perPage = 50
const total = ref(0)
const filterOp = ref('')
const filterAction = ref('')

const filtered = computed(() => logs.value.filter(l => {
  const op = filterOp.value.toLowerCase()
  const ac = filterAction.value.toLowerCase()
  return (!op || l.operator.toLowerCase().includes(op)) && (!ac || l.action.toLowerCase().includes(ac))
}))

const fmtDate = (s: string) => new Date(s).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })

const actionStyle = (a: string) => {
  if (a.includes('create')) return 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400'
  if (a.includes('delete')) return 'bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400'
  if (a.includes('update') || a.includes('reset')) return 'bg-amber-50 text-amber-600 dark:bg-amber-900/20 dark:text-amber-400'
  return 'bg-slate-100 text-slate-500 dark:bg-slate-700 dark:text-slate-400'
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const res = await apiGet<any>(`/admin/audit-logs?page=${page.value}&per_page=${perPage}`)
    logs.value = res.data
    total.value = res.total
  } catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

const prevPage = () => { if (page.value > 1) { page.value--; fetchLogs() } }
const nextPage = () => { if (page.value * perPage < total.value) { page.value++; fetchLogs() } }

onMounted(fetchLogs)
</script>
