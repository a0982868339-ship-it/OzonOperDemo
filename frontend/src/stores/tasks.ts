import { defineStore } from "pinia"
import { ref } from "vue"
import { apiGet, apiPost } from "../api/client"
import type { TaskItem, SeoPayload, MediaPayload, TaskStatus } from "../types"

interface TaskResponse {
  task_id: string
  status: TaskStatus
  result?: Record<string, unknown>
}

export const useTaskStore = defineStore("tasks", () => {
  const tasks = ref<TaskItem[]>([])

  const createSeoTask = async (payload: SeoPayload): Promise<TaskItem> => {
    const data = await apiPost<TaskResponse>("/ai/seo", payload)
    const item: TaskItem = {
      taskId: data.task_id,
      type: "seo",
      status: data.status
    }
    tasks.value.unshift(item)
    return item
  }

  const createMediaTask = async (payload: MediaPayload): Promise<TaskItem> => {
    const data = await apiPost<TaskResponse>("/ai/media", payload)
    const item: TaskItem = {
      taskId: data.task_id,
      type: "media",
      status: data.status
    }
    tasks.value.unshift(item)
    return item
  }

  const updateTask = (taskId: string, status: TaskStatus, result?: Record<string, unknown>): void => {
    const target = tasks.value.find((task: TaskItem) => task.taskId === taskId)
    if (!target) return
    target.status = status
    if (result) {
      target.result = result
    }
  }

  const fetchTask = async (taskId: string): Promise<TaskResponse> => {
    return apiGet<TaskResponse>(`/ai/tasks/${taskId}`)
  }

  return {
    tasks,
    createSeoTask,
    createMediaTask,
    updateTask,
    fetchTask
  }
})
