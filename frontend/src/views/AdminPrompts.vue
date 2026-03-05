<template>
  <div class="h-[calc(100vh-64px)] flex flex-col pt-4 px-6 pb-6 overflow-hidden">
    <div class="flex justify-between items-end mb-4 flex-shrink-0">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <span>提示词工程</span>
          <span class="text-xs font-normal px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded-full dark:bg-indigo-900/50 dark:text-indigo-400">Prompt IDE</span>
        </h1>
        <p class="text-sm text-gray-500 mt-1">版本化管理所有 AI 提示词资产，提供真机沙盒在线调试与一键优化能力。</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCreateModal">新建版本</el-button>
    </div>

    <div class="flex-1 flex gap-4 min-h-0">
      <!-- Left Panel: Prompt List -->
      <div class="w-64 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl flex flex-col overflow-hidden shadow-sm">
        <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 font-medium text-sm text-gray-700 dark:text-gray-300">
          资产库 (Assets)
        </div>
        <div class="flex-1 overflow-y-auto p-2" v-loading="loading">
          <div v-for="(prompts, agent) in groupedPrompts" :key="agent" class="mb-4">
            <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 px-2">{{ agent }}</div>
            <div
              v-for="p in prompts" :key="p.id"
              @click="selectPrompt(p)"
              class="px-3 py-2 rounded-lg cursor-pointer mb-1 border transition-colors relative"
              :class="[
                selectedPrompt?.id === p.id 
                  ? 'bg-indigo-50 border-indigo-200 dark:bg-indigo-900/30 dark:border-indigo-700' 
                  : 'border-transparent hover:bg-gray-50 dark:hover:bg-gray-700/50'
              ]"
            >
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ p.name }}</span>
                <span v-if="p.is_active" class="flex h-2 w-2 relative">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
              </div>
              <div class="text-xs text-gray-500 font-mono mt-1">{{ p.version }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Middle Panel: Editor -->
      <div class="flex-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm flex flex-col min-w-[400px]">
        <div v-if="!selectedPrompt" class="flex-1 flex items-center justify-center text-gray-400 text-sm">
          请从左侧选择一个提示词模板进行编辑
        </div>
        <template v-else>
          <!-- Editor Header -->
          <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-gray-50 dark:bg-gray-800/50">
            <div class="flex items-center gap-3">
              <h2 class="font-medium text-gray-800 dark:text-gray-200">{{ editingPrompt.name }}</h2>
              <el-tag size="small" type="info">{{ editingPrompt.version }}</el-tag>
              <el-tag size="small" :type="editingPrompt.is_active ? 'success' : 'info'" 
                      class="cursor-pointer" @click="handleActivate" v-if="!editingPrompt.is_active">
                {{ editingPrompt.is_active ? '已发布' : '设为生效版本' }}
              </el-tag>
              <el-tag size="small" type="success" v-else>已生效 (线上使用中)</el-tag>
            </div>
            <div class="flex gap-2">
              <el-button size="small" :icon="MagicStick" type="warning" plain @click="openOptimizeModal">AI 魔法优化</el-button>
              <el-button size="small" type="primary" :loading="saving" @click="savePrompt">保存修改</el-button>
            </div>
          </div>

          <!-- Editor Body -->
          <div class="flex-1 overflow-y-auto p-4 space-y-4">
            <div>
              <div class="flex justify-between items-end mb-1">
                <label class="text-sm font-semibold text-gray-700 dark:text-gray-300">系统预设 (System Prompt)</label>
                <div class="text-xs text-gray-400">定义大模型的人设、背景、核心规则。</div>
              </div>
              <el-input
                v-model="editingPrompt.system_prompt"
                type="textarea"
                :rows="6"
                placeholder="例如：你是一个资深的俄罗斯电商选品专家，你需要严格按照以下格式输出数据..."
                class="font-mono text-sm"
              />
            </div>

            <div>
              <div class="flex justify-between items-end mb-1">
                <label class="text-sm font-semibold text-gray-700 dark:text-gray-300">用户模板 (User Template)</label>
                <div class="text-xs text-gray-400">通过双大括号提取变量，例如：&#123;&#123; user_query &#125;&#125;</div>
              </div>
              <el-input
                v-model="editingPrompt.user_template"
                type="textarea"
                :rows="8"
                placeholder="例如：请分析以下用户搜索词：\n搜索词：{{ keyword }}\n要求：列出3个相关竞品。"
                class="font-mono text-sm"
              />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-sm font-semibold text-gray-700 dark:text-gray-300 block mb-1">Model / 模型</label>
                <el-input v-model="editingPrompt.parameters.model_id" placeholder="如：google/gemini-2.5-pro" size="small" />
              </div>
              <div>
                <label class="text-sm font-semibold text-gray-700 dark:text-gray-300 block mb-1">Temperature / 想象力</label>
                <el-slider v-model="editingPrompt.parameters.temperature" :max="2" :step="0.1" show-input size="small" />
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Right Panel: Sandbox -->
      <div v-if="selectedPrompt" class="w-80 bg-gray-900 border border-gray-800 rounded-xl shadow-lg flex flex-col overflow-hidden text-gray-300">
        <div class="px-4 py-3 border-b border-gray-800 flex justify-between items-center bg-gray-950">
          <div class="font-medium text-sm flex items-center gap-2">
            <el-icon><VideoPlay /></el-icon> 在线沙盒 (Sandbox)
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
          <!-- Variable inputs -->
          <div v-if="extractedVariables.length > 0" class="bg-gray-800 p-3 rounded-lg border border-gray-700">
            <h3 class="text-xs text-gray-400 uppercase tracking-widest font-semibold mb-3">模板变量注入</h3>
            <div v-for="v in extractedVariables" :key="v" class="mb-3 last:mb-0">
              <label class="block text-xs text-gray-300 mb-1 font-mono">{{ v }}</label>
              <el-input v-model="sandboxVars[v]" size="small" placeholder="..." />
            </div>
          </div>
          <div v-else class="text-xs text-gray-500 italic text-center py-2">
            当前模板未提取到独立变量
          </div>

          <el-button type="success" class="w-full" :loading="running" @click="runSandbox">
            ▶ 运行测试 (Run)
          </el-button>

          <!-- Result output -->
          <div v-if="sandboxResult" class="mt-2 flex-1 flex flex-col">
            <div class="flex justify-between items-center text-xs text-gray-400 mb-1">
              <span>输出结果</span>
              <span class="text-green-400">{{ sandboxStats.elapsed }}s | ~{{ sandboxStats.tokens }} tokens</span>
            </div>
            <div class="flex-1 bg-black rounded border border-gray-700 p-3 overflow-y-auto text-sm font-mono whitespace-pre-wrap">
              {{ sandboxResult }}
            </div>
          </div>
        </div>
      </div>
    </div>


    <!-- Create Modal -->
    <el-dialog v-model="createVisible" title="新建 Prompt 模板版本" width="500px">
      <el-form label-position="top">
        <el-form-item label="所属 Agent 标识 (owner_agent)">
          <el-select v-model="createForm.owner_agent" filterable allow-create default-first-option placeholder="例如：market_analyst" class="w-full">
            <el-option label="orchestrator (总控调度)" value="orchestrator" />
            <el-option label="scout (市场侦探)" value="scout" />
            <el-option label="analyst (数据精算)" value="analyst" />
            <el-option label="linguistic (语言翻译)" value="linguistic" />
            <el-option label="creative (创意设计)" value="creative" />
            <el-option label="seo (SEO文案)" value="seo" />
            <el-option label="image (商品生图)" value="image" />
            <el-option label="video (视频生成)" value="video" />
            <el-option label="prompt_engineer (提示词工程)" value="prompt_engineer" />
          </el-select>
        </el-form-item>
        <div class="grid grid-cols-2 gap-4">
          <el-form-item label="显示名称 (Name)">
            <el-input v-model="createForm.name" placeholder="如：俄文选品分析" />
          </el-form-item>
          <el-form-item label="版本号 (Version)">
            <el-input v-model="createForm.version" placeholder="如：v1.1" />
          </el-form-item>
        </div>
        <el-form-item>
          <el-checkbox v-model="createForm.is_active">立即上线 (替换原有版本)</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">确认创建</el-button>
      </template>
    </el-dialog>

    <!-- AI Optimize Modal -->
    <el-dialog v-model="optVisible" title="🪄 AI 魔法优化" width="600px">
      <div class="mb-4 text-sm text-gray-600 dark:text-gray-400">
        不知道如何写出结构化的顶级 Prompt？只要输入大白话需求，让元模型 (Meta-Model) 帮你生成。
      </div>
      <el-input
        v-model="optDescription"
        type="textarea"
        :rows="4"
        placeholder="请用白话描述你要大模型完成什么任务？例如：帮我分析 Ozon 的鞋子销量，挑出好卖的类型并给出结论。"
      />
      
      <template #footer>
        <el-button @click="optVisible = false">取消</el-button>
        <el-button type="warning" :loading="optimizing" @click="submitOptimize">
          <el-icon class="mr-1"><MagicStick /></el-icon> 开始魔法优化
        </el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Plus, MagicStick, VideoPlay } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiGet, apiPost, apiPut } from '../api/client'

interface Prompt {
  id: number;
  owner_agent: string;
  name: string;
  version: string;
  system_prompt: string;
  user_template: string;
  parameters: any;
  is_active: boolean;
}

const loading = ref(false)
const rawPrompts = ref<Prompt[]>([])

// Group by agent
const groupedPrompts = computed(() => {
  const groups: Record<string, Prompt[]> = {}
  rawPrompts.value.forEach(p => {
    if (!groups[p.owner_agent]) groups[p.owner_agent] = []
    groups[p.owner_agent].push(p)
  })
  return groups
})

const selectedPrompt = ref<Prompt | null>(null)
const editingPrompt = ref<Prompt | null>(null) // Deep copy for editing

const saving = ref(false)

// Sandbox State
const sandboxVars = reactive<Record<string, string>>({})
const running = ref(false)
const sandboxResult = ref("")
const sandboxStats = reactive({ elapsed: 0, tokens: 0 })

// Create State
const createVisible = ref(false)
const createForm = reactive({
  owner_agent: '',
  name: '',
  version: 'v1.0',
  is_active: false
})

// Optimize State
const optVisible = ref(false)
const optDescription = ref("")
const optimizing = ref(false)


onMounted(fetchPrompts)

async function fetchPrompts() {
  loading.value = true
  try {
    const data = await apiGet('/admin/prompts')
    rawPrompts.value = data
  } catch (e: any) {
    ElMessage.error(e.message || "Failed to load prompts")
  } finally {
    loading.value = false
  }
}

function selectPrompt(p: Prompt) {
  selectedPrompt.value = p
  editingPrompt.value = JSON.parse(JSON.stringify(p))
  
  // Keep existing sandbox vars if keys match, else clear
  const newKeys = extractedVariables.value
  for (const k of Object.keys(sandboxVars)) {
    if (!newKeys.includes(k)) delete sandboxVars[k]
  }
  sandboxResult.value = ""
}

// Automatically extract {{ var_name }} from user_template
const extractedVariables = computed(() => {
  if (!editingPrompt.value?.user_template) return []
  const regex = /\{\{\s*([a-zA-Z0-9_]+)\s*\}\}/g
  const matches = [...editingPrompt.value.user_template.matchAll(regex)]
  // Deduplicate
  return Array.from(new Set(matches.map(m => m[1])))
})

async function savePrompt() {
  if (!editingPrompt.value) return
  saving.value = true
  try {
    const res = await apiPut(`/admin/prompts/${editingPrompt.value.id}`, {
      system_prompt: editingPrompt.value.system_prompt,
      user_template: editingPrompt.value.user_template,
      parameters: editingPrompt.value.parameters,
      name: editingPrompt.value.name
    })
    ElMessage.success("保存成功")
    // Update raw list
    const idx = rawPrompts.value.findIndex(p => p.id === res.id)
    if (idx !== -1) rawPrompts.value[idx] = res
    selectedPrompt.value = res
  } catch (e: any) {
    ElMessage.error(e.message || "保存失败")
  } finally {
    saving.value = false
  }
}

async function handleActivate() {
  if (!editingPrompt.value) return
  try {
    await apiPost(`/admin/prompts/${editingPrompt.value.id}/activate`)
    ElMessage.success("已发布该版本为线上生效版本")
    await fetchPrompts()
    if (selectedPrompt.value) {
      selectPrompt(rawPrompts.value.find(p => p.id === selectedPrompt.value!.id)!)
    }
  } catch(e: any) {
    ElMessage.error(e.message)
  }
}

function openCreateModal() {
  createForm.owner_agent = ''
  createForm.name = ''
  createForm.version = 'v1.0'
  createForm.is_active = false
  if (selectedPrompt.value) {
    createForm.owner_agent = selectedPrompt.value.owner_agent
    createForm.name = selectedPrompt.value.name + " (Copy)"
  }
  createVisible.value = true
}

async function submitCreate() {
  if (!createForm.owner_agent || !createForm.name || !createForm.version) {
    return ElMessage.warning("请填写完整信息")
  }
  try {
    const payload = {
      ...createForm,
      system_prompt: selectedPrompt.value?.system_prompt || "You are an expert AI agent.",
      user_template: selectedPrompt.value?.user_template || "{{ input }}",
      parameters: selectedPrompt.value?.parameters || { temperature: 0.7, model_id: "google/gemini-2.5-pro" }
    }
    const res = await apiPost('/admin/prompts', payload)
    ElMessage.success("创建成功")
    createVisible.value = false
    await fetchPrompts()
    selectPrompt(res)
  } catch (e: any) {
    ElMessage.error(e.message || "创建失败")
  }
}

async function runSandbox() {
  if (!editingPrompt.value) return
  running.value = true
  sandboxResult.value = "思考中..."
  try {
    const payload = {
      system_prompt: editingPrompt.value.system_prompt,
      user_template: editingPrompt.value.user_template,
      parameters: editingPrompt.value.parameters,
      variables: sandboxVars
    }
    const res = await apiPost('/admin/prompts/sandbox', payload)
    sandboxResult.value = res.result
    sandboxStats.elapsed = res.elapsed
    sandboxStats.tokens = res.estimated_tokens
  } catch (e: any) {
    sandboxResult.value = `[执行报错]\n${e.message}`
  } finally {
    running.value = false
  }
}

function openOptimizeModal() {
  optDescription.value = ""
  optVisible.value = true
}

async function submitOptimize() {
  if (!optDescription.value) return ElMessage.warning("请描述你的需求")
  optimizing.value = true
  try {
    const res = await apiPost('/admin/prompts/optimize', { description: optDescription.value })
    if (editingPrompt.value) {
      editingPrompt.value.system_prompt = res.system_prompt
      editingPrompt.value.user_template = res.user_template
      ElMessage.success("魔法施法完毕，Prompt 已重写！别忘了点击保存。")
    }
    optVisible.value = false
  } catch (e: any) {
    ElMessage.error(`优化失败: ${e.message}`)
  } finally {
    optimizing.value = false
  }
}
</script>
