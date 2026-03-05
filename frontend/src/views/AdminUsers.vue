<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 p-8 font-sans">
    <!-- Header -->
    <div class="flex justify-between items-end mb-8">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white tracking-tight">用户管理 (Users)</h1>
        <p class="text-slate-500 mt-2 text-sm font-medium">共 {{ users.length }} 位成员 · {{ vipCount }} 位 VIP</p>
      </div>
      <button @click="openCreate" class="px-4 py-2.5 bg-slate-900 dark:bg-blue-600 text-white rounded-xl text-sm font-bold hover:opacity-80 transition flex items-center gap-2">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        创建用户
      </button>
    </div>

    <!-- Search + Filter -->
    <div class="flex gap-3 mb-6">
      <input v-model="search" placeholder="搜索用户名 / 邮箱…" class="flex-1 px-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:text-white" />
      <select v-model="filterRole" class="px-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm dark:text-white focus:outline-none">
        <option value="">全部角色</option>
        <option value="admin">Admin</option>
        <option value="operator">Operator</option>
        <option value="member">Member</option>
        <option value="guest">Guest</option>
      </select>
      <select v-model="filterVip" class="px-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm dark:text-white focus:outline-none">
        <option value="">全部</option>
        <option value="vip">VIP 会员</option>
        <option value="free">普通用户</option>
      </select>
    </div>

    <!-- Table -->
    <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
      <div v-if="loading" class="p-12 flex justify-center">
        <div class="w-8 h-8 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
      </div>
      <table v-else class="w-full">
        <thead>
          <tr class="border-b border-slate-100 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/80">
            <th class="text-left px-5 py-3.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">用户</th>
            <th class="text-left px-5 py-3.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">角色</th>
            <th class="text-left px-5 py-3.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">会员</th>
            <th class="text-left px-5 py-3.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Token 额度</th>
            <th class="text-left px-5 py-3.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">状态</th>
            <th class="text-left px-5 py-3.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">最后登录</th>
            <th class="px-5 py-3.5"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
          <tr v-for="u in filtered" :key="u.id" class="hover:bg-slate-50/60 dark:hover:bg-slate-700/40 transition-colors">
            <!-- User -->
            <td class="px-5 py-4">
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold text-white shrink-0"
                  :class="u.role === 'admin' ? 'bg-gradient-to-br from-purple-500 to-indigo-600' : u.role === 'operator' ? 'bg-gradient-to-br from-blue-500 to-cyan-600' : 'bg-gradient-to-br from-slate-400 to-slate-500'">
                  {{ u.username.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <div class="text-sm font-bold text-slate-900 dark:text-white">{{ u.username }}</div>
                  <div class="text-xs text-slate-400">{{ u.email }}</div>
                </div>
              </div>
            </td>
            <!-- Role -->
            <td class="px-5 py-4">
              <span :class="['px-2 py-0.5 text-[10px] font-bold rounded-full border uppercase tracking-wider', roleStyle(u.role)]">{{ u.role }}</span>
            </td>
            <!-- VIP -->
            <td class="px-5 py-4">
              <span v-if="u.is_vip" class="flex items-center gap-1 text-amber-500 font-bold text-xs">
                <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
                VIP
              </span>
              <span v-else class="text-slate-400 text-xs">普通</span>
            </td>
            <!-- Token quota -->
            <td class="px-5 py-4 min-w-32">
              <div v-if="u.token_quota === -1" class="text-xs text-emerald-600 font-bold">∞ 无限额度</div>
              <template v-else>
                <div class="flex justify-between text-xs mb-1">
                  <span class="font-bold" :class="u.quota_warning ? 'text-red-500' : 'text-slate-700 dark:text-slate-200'">
                    {{ fmtTokens(u.tokens_used) }} / {{ fmtTokens(u.token_quota) }}
                  </span>
                  <span :class="u.quota_warning ? 'text-red-500 font-bold' : 'text-slate-400'">{{ u.quota_pct }}%</span>
                </div>
                <div class="w-full h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                  <div class="h-full rounded-full transition-all" :class="u.quota_warning ? 'bg-red-500' : u.quota_pct > 50 ? 'bg-amber-500' : 'bg-blue-500'" :style="{width: Math.min(u.quota_pct, 100) + '%'}"></div>
                </div>
              </template>
            </td>
            <!-- Status -->
            <td class="px-5 py-4">
              <span class="flex items-center gap-1.5 text-xs font-bold" :class="u.is_active ? 'text-emerald-500' : 'text-slate-400'">
                <span class="w-1.5 h-1.5 rounded-full" :class="u.is_active ? 'bg-emerald-500' : 'bg-slate-300'"></span>
                {{ u.is_active ? '正常' : '已禁用' }}
              </span>
            </td>
            <!-- Last login -->
            <td class="px-5 py-4 text-xs text-slate-400">{{ fmtDate(u.last_login_at) }}</td>
            <!-- Actions -->
            <td class="px-5 py-4">
              <div class="flex justify-end gap-2">
                <button @click="editUser(u)" class="px-3 py-1 text-xs font-bold bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition">编辑</button>
                <button @click="toggleActive(u)" class="px-3 py-1 text-xs font-bold rounded-lg transition"
                  :class="u.is_active ? 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-red-50 hover:text-red-600' : 'bg-emerald-50 text-emerald-600 hover:bg-emerald-100'">
                  {{ u.is_active ? '禁用' : '启用' }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit / Create Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-lg p-8 border border-slate-200 dark:border-slate-700">
        <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-6">{{ editingId ? '编辑用户' : '创建用户' }}</h3>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-1.5">用户名</label>
              <input v-model="form.username" class="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20" />
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-1.5">邮箱</label>
              <input v-model="form.email" type="email" class="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20" />
            </div>
          </div>
          <div v-if="!editingId">
            <label class="block text-xs font-bold text-slate-500 uppercase mb-1.5">初始密码</label>
            <input v-model="form.password" type="password" class="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-1.5">角色</label>
              <select v-model="form.role" class="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none">
                <option value="guest">Guest（访客）</option>
                <option value="member">Member（会员）</option>
                <option value="operator">Operator（运营）</option>
                <option value="admin">Admin（管理员）</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-1.5">Token 额度</label>
              <input v-model.number="form.token_quota" type="number" placeholder="-1 = 无限" class="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20" />
            </div>
          </div>
          <div class="flex items-center gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <button @click="form.is_vip = !form.is_vip" :class="['relative w-10 h-5 rounded-full transition-colors', form.is_vip ? 'bg-amber-400' : 'bg-slate-200 dark:bg-slate-600']">
                <span :class="['absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform', form.is_vip ? 'translate-x-5' : '']"></span>
              </button>
              <span class="text-sm font-bold text-slate-700 dark:text-slate-200">🌟 VIP 会员</span>
            </label>
          </div>
          <div v-if="form.is_vip">
            <label class="block text-xs font-bold text-slate-500 uppercase mb-1.5">VIP 到期时间（留空 = 永久）</label>
            <input v-model="form.vip_expires_at" type="date" class="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white focus:outline-none" />
          </div>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button @click="showModal = false" class="px-5 py-2.5 border border-slate-200 dark:border-slate-600 rounded-xl text-sm font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition">取消</button>
          <button @click="submitForm" :disabled="submitting" class="px-5 py-2.5 bg-slate-900 dark:bg-blue-600 text-white rounded-xl text-sm font-bold hover:opacity-80 transition flex items-center gap-2 disabled:opacity-50">
            <span v-if="submitting" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span>{{ editingId ? '保存修改' : '创建用户' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { apiGet, apiPost, apiPut } from '../api/client'
import { ElMessage } from 'element-plus'

interface UserRow {
  id: number; username: string; email: string; role: string;
  is_active: boolean; is_vip: boolean; vip_expires_at: string | null;
  token_quota: number; tokens_used: number; quota_pct: number; quota_warning: boolean;
  last_login_at: string | null; created_at: string;
}

const users     = ref<UserRow[]>([])
const loading   = ref(true)
const search    = ref('')
const filterRole = ref('')
const filterVip  = ref('')
const showModal  = ref(false)
const submitting = ref(false)
const editingId  = ref<number | null>(null)

const form = ref({ username: '', email: '', password: 'Ozon@2025', role: 'member', is_vip: false, token_quota: 100000, vip_expires_at: '' })

const vipCount = computed(() => users.value.filter(u => u.is_vip).length)
const filtered = computed(() => users.value.filter(u => {
  const q = search.value.toLowerCase()
  const matchSearch = !q || u.username.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
  const matchRole = !filterRole.value || u.role === filterRole.value
  const matchVip = !filterVip.value || (filterVip.value === 'vip' ? u.is_vip : !u.is_vip)
  return matchSearch && matchRole && matchVip
}))

const fetchUsers = async () => {
  loading.value = true
  try { users.value = await apiGet<UserRow[]>('/admin/users') }
  catch { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

const roleStyle = (role: string) => {
  const m: Record<string, string> = {
    admin:    'bg-purple-50 text-purple-700 border-purple-100 dark:bg-purple-900/20 dark:text-purple-300 dark:border-purple-800',
    operator: 'bg-blue-50 text-blue-700 border-blue-100 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-800',
    member:   'bg-emerald-50 text-emerald-700 border-emerald-100 dark:bg-emerald-900/20 dark:text-emerald-400 dark:border-emerald-800',
    guest:    'bg-slate-100 text-slate-500 border-slate-200 dark:bg-slate-700 dark:text-slate-400 dark:border-slate-600',
  }
  return m[role] || m.guest
}

const fmtTokens = (n: number) => n >= 1_000_000 ? (n/1_000_000).toFixed(1)+'M' : n >= 1000 ? (n/1000).toFixed(0)+'K' : String(n)
const fmtDate   = (s: string | null) => s ? new Date(s).toLocaleDateString('zh-CN') : '—'

const openCreate = () => {
  editingId.value = null
  form.value = { username: '', email: '', password: 'Ozon@2025', role: 'member', is_vip: false, token_quota: 100000, vip_expires_at: '' }
  showModal.value = true
}

const editUser = (u: UserRow) => {
  editingId.value = u.id
  form.value = { username: u.username, email: u.email, password: '', role: u.role, is_vip: u.is_vip, token_quota: u.token_quota, vip_expires_at: u.vip_expires_at?.slice(0, 10) || '' }
  showModal.value = true
}

const submitForm = async () => {
  submitting.value = true
  try {
    if (editingId.value) {
      await apiPut(`/admin/users/${editingId.value}`, { ...form.value })
      ElMessage.success('已更新')
    } else {
      await apiPost('/admin/users', form.value)
      ElMessage.success('用户已创建')
    }
    showModal.value = false
    await fetchUsers()
  } catch { ElMessage.error('操作失败') }
  finally { submitting.value = false }
}

const toggleActive = async (u: UserRow) => {
  try {
    await apiPut(`/admin/users/${u.id}`, { is_active: !u.is_active })
    await fetchUsers()
    ElMessage.success(`已${u.is_active ? '禁用' : '启用'} ${u.username}`)
  } catch { ElMessage.error('操作失败') }
}

onMounted(fetchUsers)
</script>
