<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 p-8 font-sans">

    <!-- Header -->
    <div class="flex justify-between items-end mb-8">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white tracking-tight">环境配置 (Env Config)</h1>
        <p class="text-slate-500 mt-2 text-sm font-medium">平台数据源密钥管理 & 调度策略设置</p>
      </div>
      <div class="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-full shadow-sm text-xs font-medium text-slate-600 dark:text-slate-300">
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        后端连通 · 配置实时入库
      </div>
    </div>

    <div class="grid grid-cols-12 gap-6">

      <!-- ── Left: Platform Keys ── -->
      <div class="col-span-8 space-y-4">
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
          <div class="p-6 border-b border-slate-100 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/80 flex items-center gap-2">
            <span class="w-2 h-6 bg-blue-600 rounded-full"></span>
            <h2 class="text-lg font-bold text-slate-900 dark:text-white">平台数据源配置</h2>
            <span class="ml-auto text-xs text-slate-400">密钥加密存储 · 明文不落地</span>
          </div>

          <!-- Platform Row -->
          <div v-if="loading" class="p-12 flex justify-center">
            <div class="w-8 h-8 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
          </div>

          <div v-else class="divide-y divide-slate-100 dark:divide-slate-700">
            <div
              v-for="p in platforms"
              :key="p.platform"
              class="p-5 flex items-start gap-4 hover:bg-slate-50/60 dark:hover:bg-slate-700/40 transition-colors"
            >
              <!-- Color dot + name -->
              <div class="flex items-center gap-3 w-36 shrink-0 pt-1">
                <span class="w-3 h-3 rounded-full shadow-sm mt-0.5" :style="{ background: p.color }"></span>
                <span class="text-sm font-bold text-slate-800 dark:text-slate-100">{{ p.display_name }}</span>
              </div>

              <!-- Status badge -->
              <div class="shrink-0 pt-1">
                <span :class="['px-2.5 py-1 text-xs font-bold rounded-full border', statusStyle(p.status)]">
                  {{ statusLabel(p) }}
                </span>
              </div>

              <!-- Keys & input area -->
              <div class="flex-1">
                <!-- No key needed -->
                <div v-if="p.required_keys.length === 0" class="text-xs text-slate-400 pt-1">
                  无需 API Key — 自动采集
                </div>

                <!-- Key inputs -->
                <div v-else class="space-y-3">
                  <div v-for="keyName in p.required_keys" :key="keyName">
                    <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">{{ keyName }}</label>
                    <div class="flex gap-2">
                      <div class="relative flex-1">
                        <input
                          :type="showKey[p.platform + '|' + keyName] ? 'text' : 'password'"
                          v-model="keyInputs[p.platform + '|' + keyName]"
                          :placeholder="p.keys_masked[keyName] || '输入密钥…'"
                          class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-lg text-xs font-mono focus:outline-none focus:ring-2 focus:ring-blue-500/20 text-slate-700 dark:text-slate-200 placeholder:text-slate-300 dark:placeholder:text-slate-600"
                        />
                        <button
                          @click="toggleShow(p.platform, keyName)"
                          class="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                        >
                          <svg v-if="showKey[p.platform + '|' + keyName]" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 4.411m0 0L21 21" /></svg>
                          <svg v-else class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Status message -->
                <p v-if="p.status_msg" class="text-[10px] text-slate-400 mt-2">{{ p.status_msg }}</p>
                <p v-if="p.last_tested_at" class="text-[10px] text-slate-400">上次测试：{{ formatTime(p.last_tested_at) }}</p>
              </div>

              <!-- Toggle + action buttons -->
              <div class="shrink-0 flex flex-col items-end gap-2 pt-1">
                <!-- Active toggle -->
                <button
                  @click="toggleActive(p)"
                  :class="['relative w-10 h-5 rounded-full transition-colors duration-200', p.is_active ? 'bg-blue-600' : 'bg-slate-200 dark:bg-slate-600']"
                >
                  <span :class="['absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform duration-200', p.is_active ? 'translate-x-5' : '']"></span>
                </button>

                <!-- Save & Test buttons -->
                <div class="flex gap-1 mt-1">
                  <button
                    v-if="p.required_keys.length > 0"
                    @click="savePlatformKeys(p)"
                    :disabled="savingPlatform === p.platform"
                    class="px-2.5 py-1 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 text-[10px] font-bold rounded-lg hover:opacity-80 transition-opacity disabled:opacity-50"
                  >
                    <span v-if="savingPlatform === p.platform">…</span>
                    <span v-else>保存</span>
                  </button>
                  <button
                    @click="testPlatform(p)"
                    :disabled="testingPlatform === p.platform"
                    class="px-2.5 py-1 bg-blue-50 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-700 text-[10px] font-bold rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/60 transition-colors disabled:opacity-50"
                  >
                    <span v-if="testingPlatform === p.platform" class="inline-block w-3 h-3 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></span>
                    <span v-else>测试</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Right column ── -->
      <div class="col-span-4 space-y-6">

        <!-- Scheduler Config -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6">
          <h2 class="text-lg font-bold text-slate-900 dark:text-white mb-5 flex items-center gap-2">
            <span class="w-2 h-6 bg-amber-500 rounded-full"></span>
            定时采集配置
          </h2>

          <div class="space-y-5" v-if="sched">
            <!-- Collect time -->
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-2">采集时间 (每日)</label>
              <div class="flex gap-2">
                <div class="flex-1">
                  <label class="text-[10px] text-slate-400">时 (0-23)</label>
                  <input v-model.number="sched.collect_hour" type="number" min="0" max="23"
                    class="w-full mt-1 px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-lg text-sm font-mono focus:ring-2 focus:ring-amber-500/20 focus:outline-none dark:text-white" />
                </div>
                <div class="flex items-end pb-2 text-slate-400 font-bold">:</div>
                <div class="flex-1">
                  <label class="text-[10px] text-slate-400">分 (0-59)</label>
                  <input v-model.number="sched.collect_min" type="number" min="0" max="59"
                    class="w-full mt-1 px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-lg text-sm font-mono focus:ring-2 focus:ring-amber-500/20 focus:outline-none dark:text-white" />
                </div>
              </div>
            </div>

            <!-- Summary time -->
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-2">汇总推送时间 (每日)</label>
              <div class="flex gap-2">
                <div class="flex-1">
                  <label class="text-[10px] text-slate-400">时 (0-23)</label>
                  <input v-model.number="sched.summary_hour" type="number" min="0" max="23"
                    class="w-full mt-1 px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-lg text-sm font-mono focus:ring-2 focus:ring-amber-500/20 focus:outline-none dark:text-white" />
                </div>
                <div class="flex items-end pb-2 text-slate-400 font-bold">:</div>
                <div class="flex-1">
                  <label class="text-[10px] text-slate-400">分 (0-59)</label>
                  <input v-model.number="sched.summary_min" type="number" min="0" max="59"
                    class="w-full mt-1 px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-lg text-sm font-mono focus:ring-2 focus:ring-amber-500/20 focus:outline-none dark:text-white" />
                </div>
              </div>
            </div>

            <!-- Timezone -->
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-2">时区</label>
              <select v-model="sched.timezone"
                class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-lg text-sm focus:ring-2 focus:ring-amber-500/20 focus:outline-none dark:text-white">
                <option value="Asia/Shanghai">Asia/Shanghai (北京)</option>
                <option value="Europe/Moscow">Europe/Moscow (莫斯科)</option>
                <option value="UTC">UTC</option>
              </select>
            </div>

            <!-- Webhook -->
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-2">通知 Webhook（钉钉 / 飞书）</label>
              <input v-model="sched.webhook_url" type="text" placeholder="https://oapi.dingtalk.com/robot/send?..."
                class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-600 rounded-lg text-xs font-mono focus:ring-2 focus:ring-amber-500/20 focus:outline-none dark:text-white placeholder:text-slate-300 dark:placeholder:text-slate-600" />
            </div>

            <button
              @click="saveSched"
              :disabled="savingSched"
              class="w-full py-2.5 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 font-bold rounded-xl text-sm hover:opacity-80 transition-opacity flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <span v-if="savingSched" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              <span>保存调度配置</span>
            </button>
          </div>
        </div>

        <!-- Quick Status summary -->
        <div class="bg-slate-900 dark:bg-slate-950 rounded-2xl border border-slate-800 p-6 text-white">
          <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">采集源状态一览</h3>
          <div class="space-y-3">
            <div v-for="p in platforms" :key="p.platform" class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full" :style="{ background: p.color }"></span>
                <span class="text-sm text-slate-200">{{ p.display_name }}</span>
              </div>
              <span :class="['text-xs font-bold px-2 py-0.5 rounded-full', statusDotStyle(p.status)]">
                {{ statusLabel(p) }}
              </span>
            </div>
          </div>
          <div class="mt-5 pt-4 border-t border-slate-800 text-xs text-slate-500">
            采集时间：<span class="font-mono text-amber-400">{{ schedDisplay }}</span>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { apiGet, apiPut, apiPost } from '../api/client'
import { ElMessage } from 'element-plus'

interface PlatformInfo {
  platform:       string
  display_name:   string
  color:          string
  is_active:      boolean
  status:         string
  status_msg:     string | null
  required_keys:  string[]
  keys_masked:    Record<string, string>
  last_tested_at: string | null
  updated_at:     string | null
}

interface SchedConfig {
  collect_hour: number
  collect_min:  number
  summary_hour: number
  summary_min:  number
  timezone:     string
  webhook_url:  string | null
}

const platforms     = ref<PlatformInfo[]>([])
const loading       = ref(true)
const keyInputs     = ref<Record<string, string>>({})
const showKey       = ref<Record<string, boolean>>({})
const savingPlatform = ref('')
const testingPlatform = ref('')
const sched         = ref<SchedConfig | null>(null)
const savingSched   = ref(false)

const schedDisplay = computed(() => {
  if (!sched.value) return '--'
  const h  = String(sched.value.collect_hour).padStart(2, '0')
  const m  = String(sched.value.collect_min).padStart(2, '0')
  const h2 = String(sched.value.summary_hour).padStart(2, '0')
  const m2 = String(sched.value.summary_min).padStart(2, '0')
  return `${h}:${m} 采集 / ${h2}:${m2} 汇总`
})

const fetchPlatforms = async () => {
  loading.value = true
  try {
    const res = await apiGet<PlatformInfo[]>('/admin/env/platforms')
    platforms.value = res
  } catch (e) {
    ElMessage.error('加载平台配置失败')
  } finally {
    loading.value = false
  }
}

const fetchSched = async () => {
  try {
    sched.value = await apiGet<SchedConfig>('/admin/env/scheduler')
  } catch (e) {
    ElMessage.error('加载调度配置失败')
  }
}

const statusLabel = (p: PlatformInfo) => {
  if (p.status === 'no_key_needed') return '✅ 自动'
  if (p.status === 'configured')    return '✅ 已配置'
  if (p.status === 'error')         return '❌ 错误'
  return '⚪ 等配置'
}

const statusStyle = (status: string) => {
  if (status === 'configured' || status === 'no_key_needed')
    return 'bg-emerald-50 text-emerald-700 border-emerald-100 dark:bg-emerald-900/20 dark:text-emerald-400 dark:border-emerald-800'
  if (status === 'error')
    return 'bg-red-50 text-red-600 border-red-100 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800'
  return 'bg-slate-100 text-slate-500 border-slate-200 dark:bg-slate-700 dark:text-slate-400 dark:border-slate-600'
}

const statusDotStyle = (status: string) => {
  if (status === 'configured' || status === 'no_key_needed') return 'bg-emerald-900/60 text-emerald-400'
  if (status === 'error') return 'bg-red-900/60 text-red-400'
  return 'bg-slate-700 text-slate-400'
}

const toggleShow = (platform: string, keyName: string) => {
  const k = `${platform}|${keyName}`
  showKey.value[k] = !showKey.value[k]
}

const toggleActive = async (p: PlatformInfo) => {
  try {
    const res = await apiPut<PlatformInfo>(`/admin/env/platforms/${p.platform}`, { is_active: !p.is_active })
    Object.assign(p, res)
    ElMessage.success(`${p.display_name} 已${p.is_active ? '启用' : '停用'}`)
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const savePlatformKeys = async (p: PlatformInfo) => {
  const keys: Record<string, string> = {}
  for (const keyName of p.required_keys) {
    const v = keyInputs.value[`${p.platform}|${keyName}`]
    if (v) keys[keyName] = v
  }
  if (Object.keys(keys).length === 0) {
    ElMessage.warning('请输入至少一个密钥')
    return
  }
  savingPlatform.value = p.platform
  try {
    const res = await apiPut<PlatformInfo>(`/admin/env/platforms/${p.platform}`, { keys })
    Object.assign(p, res)
    // Clear inputs after save
    for (const keyName of p.required_keys) {
      keyInputs.value[`${p.platform}|${keyName}`] = ''
    }
    ElMessage.success(`${p.display_name} 密钥已加密保存`)
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    savingPlatform.value = ''
  }
}

const testPlatform = async (p: PlatformInfo) => {
  testingPlatform.value = p.platform
  try {
    const res = await apiPost<{ status: string; msg: string }>(`/admin/env/platforms/${p.platform}/test`, {})
    p.status     = res.status
    p.status_msg = res.msg
    if (res.status === 'configured') ElMessage.success(`${p.display_name}：${res.msg}`)
    else ElMessage.warning(`${p.display_name}：${res.msg}`)
  } catch (e) {
    ElMessage.error(`测试 ${p.display_name} 失败`)
  } finally {
    testingPlatform.value = ''
  }
}

const saveSched = async () => {
  if (!sched.value) return
  savingSched.value = true
  try {
    await apiPut('/admin/env/scheduler', sched.value)
    ElMessage.success('调度配置已保存并立即生效')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    savingSched.value = false
  }
}

const formatTime = (iso: string) => {
  const d = new Date(iso)
  return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  await Promise.all([fetchPlatforms(), fetchSched()])
})
</script>
