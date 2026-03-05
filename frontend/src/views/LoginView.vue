<script setup lang="ts">
import { ref } from "vue"
import { useUserStore } from "../stores/user"
import { useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { apiPost } from "../api/client"

const userStore = useUserStore()
const router = useRouter()
const loading = ref(false)

const loginForm = ref({
  username: "",
  password: ""
})

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning("请输入用户名和密码")
    return
  }

  loading.value = true
  try {
    const res = await apiPost<{ token: string, role: string }>("/auth/login", {
      username: loginForm.value.username,
      password: loginForm.value.password
    })
    
    userStore.setToken(res.token)
    if (res.role === "admin") {
      ElMessage.success("欢迎回来，管理员")
    } else {
      ElMessage.success("登录成功")
    }
    router.push("/")
  } catch (e) {
    ElMessage.error("用户名或密码错误 (Demo: admin/admin)")
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen w-full flex items-center justify-center bg-slate-950 relative overflow-hidden">
    <!-- Abstract Background -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-blue-600/20 rounded-full blur-[120px] animate-pulse"></div>
      <div class="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] bg-indigo-600/20 rounded-full blur-[120px]"></div>
    </div>

    <!-- Login Card -->
    <div class="relative z-10 w-full max-w-[420px] px-6">
      <div class="bg-white/5 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-2xl">
        <div class="text-center mb-10">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 mb-4 shadow-lg shadow-blue-500/20">
            <span class="text-3xl text-white">◆</span>
          </div>
          <h1 class="text-2xl font-bold text-white tracking-tight">Ozon AI Assistant</h1>
          <p class="text-slate-400 text-sm mt-2 font-inter">俄罗斯跨境电商 AI 一站式平台</p>
        </div>

        <el-form label-position="top" class="space-y-5">
          <div class="space-y-4">
            <div class="space-y-1">
              <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider ml-1">用户名</label>
              <el-input 
                v-model="loginForm.username" 
                placeholder="admin"
                class="premium-input"
              >
                <template #prefix>👤</template>
              </el-input>
            </div>
            <div class="space-y-1">
              <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider ml-1">密码</label>
              <el-input 
                v-model="loginForm.password" 
                type="password" 
                placeholder="••••••••"
                show-password
                class="premium-input"
                @keyup.enter="handleLogin"
              >
                <template #prefix>🔒</template>
              </el-input>
            </div>
          </div>

          <div class="pt-4">
            <el-button 
              type="primary" 
              class="w-full !h-12 !rounded-xl !text-base !font-bold !bg-blue-600 hover:!bg-blue-500 !border-none shadow-lg shadow-blue-600/20 transition-all active:scale-[0.98]"
              :loading="loading"
              @click="handleLogin"
            >
              登录系统
            </el-button>
          </div>
        </el-form>

        <div class="mt-8 text-center border-t border-white/5 pt-6">
          <p class="text-slate-500 text-xs font-inter">
            &copy; 2026 Ozon AI Integration. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.premium-input .el-input__wrapper {
  background-color: rgba(255, 255, 255, 0.03) !important;
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1) inset !important;
  border-radius: 12px !important;
  padding: 8px 12px !important;
  transition: all 0.3s !important;
}
.premium-input .el-input__wrapper.is-focus {
  background-color: rgba(255, 255, 255, 0.05) !important;
  box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.5) inset !important;
}
.premium-input .el-input__inner {
  color: #fff !important;
  font-family: 'Inter', sans-serif !important;
}
.premium-input .el-input__inner::placeholder {
  color: #64748b !important;
}
</style>
