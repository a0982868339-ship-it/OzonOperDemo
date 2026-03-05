<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 p-8 font-sans">
    <div class="flex justify-between items-end mb-8">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white tracking-tight">系统公告 (Notices)</h1>
        <p class="text-slate-500 mt-2 text-sm font-medium">管理全站用户可见的通知公告</p>
      </div>
      <button @click="openCreate" class="px-4 py-2.5 bg-slate-900 dark:bg-blue-600 text-white rounded-xl text-sm font-bold hover:opacity-80 transition flex items-center gap-2">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        发布公告
      </button>
    </div>

    <!-- Notice list -->
    <div class="space-y-4">
      <div v-if="loading" class="p-12 flex justify-center">
        <div class="w-8 h-8 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
      </div>
      <div v-else-if="notices.length === 0" class="py-20 text-center text-slate-400">
        <div class="text-5xl mb-4">📢</div>
        <div class="text-sm">暂无公告 · 点击「发布公告」创建第一条</div>
      </div>
      <div v-for="n in notices" :key="n.id"
        :class="['bg-white dark:bg-slate-800 rounded-2xl border shadow-sm p-6 transition-all', n.pinned ? 'border-amber-200 dark:border-amber-800' : 'border-slate-200 dark:border-slate-700', !n.is_active ? 'opacity-50' : '']">
        <div class="flex items-start gap-4">
          <!-- Type icon -->
          <div :class="['w-10 h-10 rounded-xl flex items-center justify-center text-lg shrink-0', typeStyle(n.notice_type).bg]">
            {{ typeStyle(n.notice_type).icon }}
          </div>
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <span v-if="n.pinned" class="text-amber-500 text-xs font-bold">📌 置顶</span>
              <span :class="['px-2 py-0.5 text-[10px] font-bold rounded uppercase', typeStyle(n.notice_type).badge]">{{ n.notice_type }}</span>
              <span v-if="!n.is_active" class="px-2 py-0.5 text-[10px] font-bold rounded bg-slate-100 text-slate-400">已停用</span>
            </div>
            <h3 class="text-base font-bold text-slate-900 dark:text-white">{{ n.title }}</h3>
            <p class="text-sm text-slate-500 dark:text-slate-400 mt-1 whitespace-pre-line">{{ n.content }}</p>
            <div class="flex items-center gap-4 mt-3 text-[10px] text-slate-400">
              <span>By {{ n.created_by }}</span>
              <span>{{ fmtDate(n.created_at) }}</span>
              <span v-if="n.expires_at">到期：{{ fmtDate(n.expires_at) }}</span>
            </div>
          </div>
          <!-- Actions -->
          <div class="flex gap-2 shrink-0">
            <button @click="editNotice(n)" class="px-3 py-1.5 text-xs font-bold bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-100 transition">编辑</button>
            <button @click="deleteNotice(n.id)" class="px-3 py-1.5 text-xs font-bold bg-red-50 dark:bg-red-900/20 text-red-500 rounded-lg hover:bg-red-100 transition">删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-lg p-8 border border-slate-200 dark:border-slate-700">
        <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-6">{{ editingId ? '编辑公告' : '发布公告' }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase mb-1.5">标题</label>
            <input v-model="form.title" class="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-500 uppercase mb-1.5">内容</label>
            <textarea v-model="form.content" rows="4" class="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none resize-none"></textarea>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-1.5">类型</label>
              <select v-model="form.notice_type" class="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none">
                <option value="info">ℹ️ Info（信息）</option>
                <option value="success">✅ Success（成功）</option>
                <option value="warning">⚠️ Warning（警告）</option>
                <option value="error">❌ Error（错误）</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-1.5">到期时间（可选）</label>
              <input v-model="form.expires_at" type="date" class="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none" />
            </div>
          </div>
          <div class="flex gap-6">
            <label class="flex items-center gap-2 cursor-pointer">
              <button @click="form.is_active = !form.is_active" :class="['relative w-9 h-5 rounded-full transition', form.is_active ? 'bg-blue-500' : 'bg-slate-200 dark:bg-slate-600']">
                <span :class="['absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform', form.is_active ? 'translate-x-4' : '']"></span>
              </button>
              <span class="text-sm font-medium text-slate-700 dark:text-slate-200">启用</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <button @click="form.pinned = !form.pinned" :class="['relative w-9 h-5 rounded-full transition', form.pinned ? 'bg-amber-400' : 'bg-slate-200 dark:bg-slate-600']">
                <span :class="['absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform', form.pinned ? 'translate-x-4' : '']"></span>
              </button>
              <span class="text-sm font-medium text-slate-700 dark:text-slate-200">📌 置顶</span>
            </label>
          </div>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button @click="showModal = false" class="px-5 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl text-sm font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-50 transition">取消</button>
          <button @click="submitForm" :disabled="submitting" class="px-5 py-2.5 bg-slate-900 dark:bg-blue-600 text-white rounded-xl text-sm font-bold hover:opacity-80 transition disabled:opacity-50 flex items-center gap-2">
            <span v-if="submitting" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            {{ editingId ? '保存' : '发布' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete } from '../api/client'
import { ElMessage } from 'element-plus'

const notices   = ref<any[]>([])
const loading   = ref(true)
const showModal = ref(false)
const editingId = ref<number | null>(null)
const submitting = ref(false)
const form = ref({ title: '', content: '', notice_type: 'info', is_active: true, pinned: false, expires_at: '' })

const typeStyle = (t: string) => ({
  info:    { icon: 'ℹ️', bg: 'bg-blue-50 dark:bg-blue-900/20',    badge: 'bg-blue-100 text-blue-600 dark:bg-blue-900/40 dark:text-blue-400' },
  success: { icon: '✅', bg: 'bg-emerald-50 dark:bg-emerald-900/20', badge: 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/40 dark:text-emerald-400' },
  warning: { icon: '⚠️', bg: 'bg-amber-50 dark:bg-amber-900/20',   badge: 'bg-amber-100 text-amber-600 dark:bg-amber-900/40 dark:text-amber-400' },
  error:   { icon: '❌', bg: 'bg-red-50 dark:bg-red-900/20',       badge: 'bg-red-100 text-red-600 dark:bg-red-900/40 dark:text-red-400' },
}[t] || { icon: 'ℹ️', bg: 'bg-blue-50', badge: 'bg-blue-100 text-blue-600' })

const fmtDate = (s: string) => new Date(s).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })

const fetchNotices = async () => {
  loading.value = true
  try { notices.value = await apiGet<any[]>('/admin/notices') }
  catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

const openCreate = () => {
  editingId.value = null
  form.value = { title: '', content: '', notice_type: 'info', is_active: true, pinned: false, expires_at: '' }
  showModal.value = true
}

const editNotice = (n: any) => {
  editingId.value = n.id
  form.value = { title: n.title, content: n.content, notice_type: n.notice_type, is_active: n.is_active, pinned: n.pinned, expires_at: n.expires_at?.slice(0, 10) || '' }
  showModal.value = true
}

const submitForm = async () => {
  submitting.value = true
  try {
    if (editingId.value) { await apiPut(`/admin/notices/${editingId.value}`, form.value); ElMessage.success('已更新') }
    else { await apiPost('/admin/notices', form.value); ElMessage.success('公告已发布') }
    showModal.value = false
    await fetchNotices()
  } catch { ElMessage.error('操作失败') }
  finally { submitting.value = false }
}

const deleteNotice = async (id: number) => {
  try { await apiDelete(`/admin/notices/${id}`); await fetchNotices(); ElMessage.success('已删除') }
  catch { ElMessage.error('删除失败') }
}

onMounted(fetchNotices)
</script>
