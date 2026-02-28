/**
 * Real API module - calls FastAPI backend.
 * Same interface as mock.ts for seamless switching.
 */

import apiClient from './index'
import type { ISite, IPage, IDomain } from '@/types/site'
import type { IBlock, IBlockTemplate } from '@/types/block'

// ========== Sites ==========

export async function fetchSites(): Promise<ISite[]> {
  const { data } = await apiClient.get('/sites')
  return data
}

export async function fetchSite(siteId: string): Promise<ISite | null> {
  try {
    const { data } = await apiClient.get(`/sites/${siteId}`)
    return data
  } catch {
    return null
  }
}

export async function createSite(name: string, description?: string, isImported?: boolean): Promise<ISite> {
  const { data } = await apiClient.post('/sites', { name, description, is_imported: isImported || false })
  return data
}

export async function updateSite(siteId: string, updates: Partial<ISite>): Promise<ISite | null> {
  try {
    const { data } = await apiClient.patch(`/sites/${siteId}`, updates)
    return data
  } catch {
    return null
  }
}

export async function deleteSite(siteId: string): Promise<boolean> {
  try {
    await apiClient.delete(`/sites/${siteId}`)
    return true
  } catch {
    return false
  }
}

// ========== Pages ==========

export async function createPage(siteId: string, title: string, slug: string): Promise<IPage | null> {
  try {
    const { data } = await apiClient.post(`/sites/${siteId}/pages`, { title, slug })
    return data
  } catch {
    return null
  }
}

export async function updatePage(siteId: string, pageId: string, updates: Partial<IPage>): Promise<IPage | null> {
  try {
    const { data } = await apiClient.patch(`/sites/${siteId}/pages/${pageId}`, updates)
    return data
  } catch {
    return null
  }
}

export async function deletePage(siteId: string, pageId: string): Promise<boolean> {
  try {
    await apiClient.delete(`/sites/${siteId}/pages/${pageId}`)
    return true
  } catch {
    return false
  }
}

// ========== Blocks ==========

export async function fetchPageBlocks(pageId: string): Promise<IBlock[]> {
  const { data } = await apiClient.get(`/pages/${pageId}/blocks`)
  return data
}

export async function savePageBlocks(pageId: string, blocks: IBlock[]): Promise<boolean> {
  try {
    await apiClient.put(`/pages/${pageId}/blocks`, { blocks })
    return true
  } catch {
    return false
  }
}

export async function fetchBlockTemplates(): Promise<IBlockTemplate[]> {
  const { data } = await apiClient.get('/block-templates')
  return data
}

// ========== Publish ==========

export async function publishPage(siteId: string, pageId: string): Promise<boolean> {
  try {
    await apiClient.post(`/sites/${siteId}/pages/${pageId}/publish`)
    return true
  } catch {
    return false
  }
}

export async function publishSite(siteId: string): Promise<boolean> {
  try {
    await apiClient.post(`/sites/${siteId}/publish`)
    return true
  } catch {
    return false
  }
}

// ========== Uploads ==========

const EXTERNAL_API_BASE = import.meta.env.VITE_EXTERNAL_APP_URL || 'https://app.akm-advisor.com'
const UPLOAD_PROJECT_ID = import.meta.env.VITE_UPLOAD_PROJECT_ID || 'site-builder'

export async function uploadFile(file: File, projectId?: string): Promise<{ url: string; filename: string }> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('project_id', projectId || UPLOAD_PROJECT_ID)

  // Upload goes directly to the external app API which handles S3 storage
  const { data } = await apiClient.post(
    `${EXTERNAL_API_BASE}/api/v1/files/upload`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  // External API returns file metadata; url field may vary
  const url: string = data.url || data.file_url || data.download_url || data.path || ''
  const filename: string = data.filename || data.name || file.name
  return { url, filename }
}

// ========== Domains ==========

export async function addDomain(siteId: string, domainName: string): Promise<IDomain> {
  const { data } = await apiClient.post(`/sites/${siteId}/domains`, { domainName })
  return data
}

export async function removeDomain(siteId: string, domainId: string): Promise<boolean> {
  try {
    await apiClient.delete(`/sites/${siteId}/domains/${domainId}`)
    return true
  } catch {
    return false
  }
}

export interface DomainVerifyResult {
  isVerified: boolean
  domainName: string
  resolvedIps: string[]
  expectedIp: string
  message: string
}

export async function verifyDomain(siteId: string, domainId: string): Promise<DomainVerifyResult> {
  const { data } = await apiClient.post(`/sites/${siteId}/domains/${domainId}/verify`)
  return data
}

export async function enableSsl(siteId: string, domainId: string): Promise<{ status: string; message: string }> {
  const { data } = await apiClient.post(`/sites/${siteId}/domains/${domainId}/ssl`)
  return data
}

export async function fetchServerInfo(): Promise<{ serverIp: string }> {
  const { data } = await apiClient.get('/server-info')
  return data
}

