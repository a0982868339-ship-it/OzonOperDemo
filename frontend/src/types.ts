export type TaskStatus = "PENDING" | "GENERATING" | "COMPLETED" | "FAILED"

export interface RadarItem {
  keyword: string
  demand: number
  supply: number
  index: number
  heat: number
  quadrant: string
}

export interface TaskItem {
  taskId: string
  type: "seo" | "media"
  status: TaskStatus
  result?: Record<string, unknown>
}

export interface SeoPayload {
  product_name: string
  category: string
}

export interface MediaPayload {
  base_prompt: string
}
