import { createRouter, createWebHistory, type RouteRecordRaw, type RouteLocationNormalized } from "vue-router"
import { useUserStore } from "../stores/user"
import Dashboard from "../views/Dashboard.vue"
import AdminControl from "../views/AdminControl.vue"
import AdminUsers from "../views/AdminUsers.vue"
import AdminUsage from "../views/AdminUsage.vue"
import Forbidden from "../views/Forbidden.vue"
import MarketRadarView from "../views/MarketRadarView.vue"
import CreativeStudioView from "../views/CreativeStudioView.vue"
import TaskCenterView from "../views/TaskCenterView.vue"
import LoginView from "../views/LoginView.vue"
import AnalysisView from "../views/AnalysisView.vue"
import ImageGenView from "../views/ImageGenView.vue"
import VideoGenView from "../views/VideoGenView.vue"
import CopywritingView from "../views/CopywritingView.vue"
import PromptStudioView from "../views/PromptStudioView.vue"
import MissionControl from "../views/MissionControl.vue"
import AdminEnvConfig from "../views/AdminEnvConfig.vue"
import AdminNotices from "../views/AdminNotices.vue"
import AdminAuditLog from "../views/AdminAuditLog.vue"
import AdminSystemInfo from "../views/AdminSystemInfo.vue"
import AdminPrompts from "../views/AdminPrompts.vue"

const routes: RouteRecordRaw[] = [
  { path: "/login", name: "login", component: LoginView },
  { path: "/", name: "dashboard", component: Dashboard },
  // 任务指挥台 (Orchestrator)
  { path: "/mission", name: "mission", component: MissionControl },
  { path: "/market-radar", name: "market-radar", component: MarketRadarView },
  { path: "/task-center", name: "task-center", component: TaskCenterView },
  // New Independent Modules
  { path: "/analysis", name: "analysis", component: AnalysisView },
  { path: "/image-gen", name: "image-gen", component: ImageGenView },
  { path: "/video-gen", name: "video-gen", component: VideoGenView },
  { path: "/copywriting", name: "copywriting", component: CopywritingView },
  { path: "/prompt-studio", name: "prompt-studio", component: PromptStudioView },
  // Admin Routes (Sub-menu support)
  { path: "/admin/configs", name: "admin-configs", component: AdminControl, meta: { requiresAdmin: true } },
  { path: "/admin/users", name: "admin-users", component: AdminUsers, meta: { requiresAdmin: true } },
  { path: "/admin/usage", name: "admin-usage", component: AdminUsage, meta: { requiresAdmin: true } },
  { path: "/admin/env-config", name: "admin-env-config", component: AdminEnvConfig, meta: { requiresAdmin: true } },
  { path: "/admin/prompts", name: "admin-prompts", component: AdminPrompts, meta: { requiresAdmin: true } },
  { path: "/admin/notices", name: "admin-notices", component: AdminNotices, meta: { requiresAdmin: true } },
  { path: "/admin/audit-log", name: "admin-audit-log", component: AdminAuditLog, meta: { requiresAdmin: true } },
  { path: "/admin/system-info", name: "admin-system-info", component: AdminSystemInfo, meta: { requiresAdmin: true } },
  // Redirects
  { path: "/admin", redirect: "/admin/configs" },
  { path: "/admin/control", redirect: "/admin/configs" },
  { path: "/403", name: "forbidden", component: Forbidden }
]


export const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to: RouteLocationNormalized) => {
  const user = useUserStore()

  // Public pages
  if (to.path === "/login") return true

  // Check Auth
  if (!user.token) return { path: "/login" }

  if (to.meta.requiresAdmin && user.role !== "admin") {
    return { path: "/" }
  }
  return true
})
