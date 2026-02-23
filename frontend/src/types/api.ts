// API response type definitions

export interface IApiResponse<T> {
  data: T
  success: boolean
  message?: string
}

export interface IApiListResponse<T> {
  data: T[]
  total: number
  page: number
  perPage: number
}

export interface IApiError {
  message: string
  code: string
  details?: Record<string, string[]>
}
