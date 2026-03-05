<script setup lang="ts">
import { ref } from "vue"
import axios from "axios"

const rawInput = ref("为 Ozon 平台上的智能猫砂盆生成商品标题和关键词")
const mode = ref("seo")
const loading = ref(false)
const result = ref<any>(null)
const error = ref("")

const modeOptions = [
  { value: "seo", label: "🛒 SEO 电商文案", color: "emerald" },
  { value: "video", label: "🎬 视频生成脚本", color: "amber" },
  { value: "ad", label: "📣 社媒广告文案", color: "blue" },
  { value: "roleplay", label: "🤖 AI 角色扮演", color: "purple" },
]

const modeExamples: Record<string, string> = {
  seo: "为 Ozon 平台上的智能猫砂盆生成商品标题和关键词",
  video: "猫咪在客厅使用智能猫砂盆，展示自动清洁功能",
  ad: "在 VK 上推广宠物用品，目标用户是 25-40 岁的养猫人士",
  roleplay: "一个专业的 Ozon 电商运营顾问，帮助中国卖家开拓俄罗斯市场",
}

const selectMode = (m: string) => {
  mode.value = m
  rawInput.value = modeExamples[m]
}

const generate = async () => {
  if (!rawInput.value.trim()) return
  loading.value = true
  error.value = ""
  result.value = null

  try {
    const res = await axios.post("/ai/prompt-engineer", {
      raw_input: rawInput.value,
      mode: mode.value,
    })
    result.value = res.data
  } catch (e: any) {
    error.value = e?.response?.data?.detail || "生成失败，请检查 AI 配置"
  } finally {
    loading.value = false
  }
}

const copyText = (text: string) => {
  navigator.clipboard.writeText(text)
}

const modeColor: Record<string, string> = {
  seo: "emerald",
  video: "amber",
  ad: "blue",
  roleplay: "purple",
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 p-8 font-sans transition-colors duration-300">
    <header class="mb-8">
      <h1 class="text-3xl font-bold text-slate-900 dark:text-white">✨ Prompt Studio</h1>
      <p class="text-slate-500 dark:text-slate-400 mt-1">AI 提示词工程师 · 把原始需求优化为专业 LLM Prompt</p>
    </header>

    <div class="grid grid-cols-12 gap-8">
      <!-- 左侧控制区 -->
      <div class="col-span-5 space-y-5">
        <!-- 模式选择 -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
          <p class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">选择 Prompt 类型</p>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="opt in modeOptions"
              :key="opt.value"
              @click="selectMode(opt.value)"
              :class="[
                'px-4 py-3 rounded-xl text-sm font-bold border-2 transition-all text-left',
                mode === opt.value
                  ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300'
                  : 'border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-500'
              ]"
            >{{ opt.label }}</button>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
          <label class="block">
            <span class="text-sm font-bold text-slate-700 dark:text-slate-300 block mb-2">描述你的原始需求</span>
            <textarea
              v-model="rawInput"
              rows="5"
              class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-sm dark:text-white resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
              placeholder="用中文简单描述你想要做什么..."
            ></textarea>
          </label>
          <p class="text-xs text-slate-400 dark:text-slate-500 mt-2">💡 可以直接用中文描述，AI 会生成专业的英文 Prompt</p>
        </div>

        <div v-if="error" class="px-4 py-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl text-sm">
          {{ error }}
        </div>

        <button
          @click="generate"
          :disabled="loading || !rawInput.trim()"
          class="w-full py-4 bg-indigo-600 dark:bg-indigo-500 text-white font-bold rounded-xl hover:bg-indigo-700 dark:hover:bg-indigo-600 transition-all active:scale-[0.98] disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg"
        >
          <span v-if="loading" class="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full"></span>
          <span>{{ loading ? 'AI 正在优化 Prompt...' : '✨ 生成专业 Prompt' }}</span>
        </button>
      </div>

      <!-- 右侧结果区 -->
      <div class="col-span-7 space-y-4">
        <!-- 空状态 -->
        <div v-if="!result && !loading" class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-16 flex flex-col items-center justify-center text-slate-400 shadow-sm min-h-[400px]">
          <div class="text-6xl mb-4">✨</div>
          <p class="font-bold text-lg text-slate-500 dark:text-slate-400 text-center">选择类型，输入需求</p>
          <p class="text-sm mt-2 text-center opacity-60">AI 将把你的简单描述变成专业的 LLM Prompt</p>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-16 flex flex-col items-center justify-center shadow-sm min-h-[400px]">
          <div class="w-14 h-14 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mx-auto mb-6"></div>
          <div class="text-indigo-500 font-mono text-sm tracking-widest animate-pulse">OPTIMIZING PROMPT...</div>
        </div>

        <template v-if="result">
          <!-- 优化后的 Prompt -->
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
            <div class="flex justify-between items-center mb-3">
              <div>
                <span class="text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">Optimized Prompt</span>
                <span class="ml-2 text-xs px-2 py-0.5 bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 rounded-full font-bold">{{ result.mode_name }}</span>
              </div>
              <button @click="copyText(result.optimized_prompt)" class="text-xs font-bold text-slate-400 hover:text-indigo-500 transition-colors px-3 py-1 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-900/20">
                复制 Prompt
              </button>
            </div>
            <pre class="text-sm text-slate-700 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-700/50 p-4 rounded-xl whitespace-pre-wrap font-mono text-xs">{{ result.optimized_prompt }}</pre>
          </div>

          <!-- 可替换变量 -->
          <div v-if="result.variables?.length" class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
            <p class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">可替换变量 Variables</p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="v in result.variables"
                :key="v"
                class="px-3 py-1.5 bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 rounded-lg text-xs font-mono font-bold border border-amber-200 dark:border-amber-800"
              >{{ '{' + v + '}' }}</span>
            </div>
          </div>

          <!-- 解释 -->
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
            <p class="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider mb-3">为什么这样优化？</p>
            <p class="text-sm text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">{{ result.explanation }}</p>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
