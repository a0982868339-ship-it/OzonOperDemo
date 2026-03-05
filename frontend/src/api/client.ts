const API_BASE = ""

function authHeader(): Record<string, string> {
  const token = localStorage.getItem("token")
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { headers: { ...authHeader() } })
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`)
  }
  return (await res.json()) as T
}

export async function apiPost<T>(path: string, payload: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload)
  })
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`)
  }
  return (await res.json()) as T
}

export async function apiPatch<T>(path: string, payload: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload)
  })
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`)
  }
  return (await res.json()) as T
}

export async function apiPut<T>(path: string, payload: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeader() },
    body: JSON.stringify(payload)
  })
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`)
  }
  return (await res.json()) as T
}

export async function apiDelete<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "DELETE",
    headers: { ...authHeader() }
  })
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`)
  }
  return (await res.json()) as T
}
