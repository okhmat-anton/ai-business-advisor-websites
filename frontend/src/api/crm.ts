// CRM API client for app.akm-advisor.com
// Uses the same JWT token as the main app (shared cookie / localStorage)

import axios from 'axios'

const CRM_BASE = 'https://app.akm-advisor.com/api/v1'

function getToken(): string | null {
  const match = document.cookie.match(/(?:^|; )akm_auth_token=([^;]*)/)
  const cookieToken = match ? decodeURIComponent(match[1] ?? '') : null
  return cookieToken || localStorage.getItem('auth_token')
}

const crmClient = axios.create({
  baseURL: CRM_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

crmClient.interceptors.request.use((config) => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export interface CrmForm {
  id: string
  name: string
  slug: string
  description?: string
  is_active?: boolean
  fields?: Array<{ label: string; type: string }>
  created_at?: string
  submissions_count?: number
}

export interface CrmFormEmbedCode {
  form_id?: string
  embed_code?: string
  html?: string
  script_tag?: string
  iframe_code?: string
}

/** Fetch all web forms from CRM */
export async function fetchCrmForms(): Promise<CrmForm[]> {
  const res = await crmClient.get('/forms')
  // API may return { items: [...] } or a plain array
  return res.data?.items ?? res.data ?? []
}

/** Fetch embed code snippet for a specific form */
export async function fetchCrmFormEmbedCode(formId: string): Promise<CrmFormEmbedCode> {
  const res = await crmClient.get(`/forms/${formId}/embed-code`)
  return res.data
}
