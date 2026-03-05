import { onMounted, onUnmounted } from "vue"
import { useTaskStore } from "../stores/tasks"

export const useTaskPolling = (): void => {
  const taskStore = useTaskStore()
  let timer: number | null = null

  const poll = async () => {
    const pending = taskStore.tasks.filter(
      (task: { status: string }) => task.status === "PENDING" || task.status === "GENERATING"
    )
    for (const task of pending) {
      const res = await taskStore.fetchTask(task.taskId)
      taskStore.updateTask(task.taskId, res.status, res.result)
    }
  }

  onMounted(() => {
    timer = window.setInterval(poll, 3000)
  })

  onUnmounted(() => {
    if (timer) window.clearInterval(timer)
  })
}
