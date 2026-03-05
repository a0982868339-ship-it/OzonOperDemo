import { defineStore } from "pinia"
import { ref } from "vue"

function decodeRoleFromToken(token: string | null): string {
  if (!token) return "user"
  const parts = token.split(".")
  if (parts.length !== 3) return "user"
  try {
    const payload = JSON.parse(atob(parts[1].replace(/-/g, "+").replace(/_/g, "/")))
    return String(payload.role || "user")
  } catch {
    return "user"
  }
}

export const useUserStore = defineStore("user", () => {
  const token = ref<string | null>(localStorage.getItem("token"))
  const role = ref<string>(decodeRoleFromToken(token.value))

  const setToken = (t: string | null): void => {
    token.value = t
    if (t) localStorage.setItem("token", t)
    else localStorage.removeItem("token")
    role.value = decodeRoleFromToken(t)
  }

  return { token, role, setToken }
})
