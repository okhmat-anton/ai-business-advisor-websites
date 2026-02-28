/**
 * API layer switcher.
 * Uses real API when VITE_USE_MOCK=false, otherwise falls back to mock.
 *
 * Set VITE_USE_MOCK=false in .env or .env.local to use the real backend.
 */

import type { ISite, IPage, IDomain } from '@/types/site'
import type { IBlock, IBlockTemplate } from '@/types/block'
import type { DomainVerifyResult } from './real'

const useMock = import.meta.env.VITE_USE_MOCK !== 'false'

// API function types
type FetchSites = () => Promise<ISite[]>
type FetchSite = (siteId: string) => Promise<ISite | null>
type CreateSite = (name: string, description?: string, isImported?: boolean) => Promise<ISite>
type UpdateSite = (siteId: string, data: Partial<ISite>) => Promise<ISite | null>
type DeleteSite = (siteId: string) => Promise<boolean>
type CreatePage = (siteId: string, title: string, slug: string) => Promise<IPage | null>
type UpdatePage = (siteId: string, pageId: string, data: Partial<IPage>) => Promise<IPage | null>
type DeletePage = (siteId: string, pageId: string) => Promise<boolean>
type FetchPageBlocks = (pageId: string) => Promise<IBlock[]>
type SavePageBlocks = (pageId: string, blocks: IBlock[]) => Promise<boolean>
type FetchBlockTemplates = () => Promise<IBlockTemplate[]>
type PublishPage = (siteId: string, pageId: string) => Promise<boolean>
type PublishSite = (siteId: string) => Promise<boolean>
type AddDomain = (siteId: string, domainName: string) => Promise<IDomain>
type RemoveDomain = (siteId: string, domainId: string) => Promise<boolean>
type VerifyDomain = (siteId: string, domainId: string) => Promise<DomainVerifyResult>
type EnableSsl = (siteId: string, domainId: string) => Promise<{ status: string; message: string }>
type FetchServerInfo = () => Promise<{ serverIp: string }>
type UploadFile = (file: File, projectId?: string) => Promise<{ url: string; filename: string }>

let _fetchSites: FetchSites
let _fetchSite: FetchSite
let _createSite: CreateSite
let _updateSite: UpdateSite
let _deleteSite: DeleteSite
let _createPage: CreatePage
let _updatePage: UpdatePage
let _deletePage: DeletePage
let _fetchPageBlocks: FetchPageBlocks
let _savePageBlocks: SavePageBlocks
let _fetchBlockTemplates: FetchBlockTemplates
let _publishPage: PublishPage
let _publishSite: PublishSite
let _addDomain: AddDomain
let _removeDomain: RemoveDomain
let _verifyDomain: VerifyDomain
let _enableSsl: EnableSsl
let _fetchServerInfo: FetchServerInfo
let _uploadFile: UploadFile

if (useMock) {
  const m = await import('./mock')
  _fetchSites = m.fetchSites
  _fetchSite = m.fetchSite
  _createSite = m.createSite
  _updateSite = m.updateSite
  _deleteSite = m.deleteSite
  _createPage = m.createPage
  _updatePage = m.updatePage
  _deletePage = m.deletePage
  _fetchPageBlocks = m.fetchPageBlocks
  _savePageBlocks = m.savePageBlocks
  _fetchBlockTemplates = m.fetchBlockTemplates
  _publishPage = m.publishPage
  _publishSite = m.publishSite
  _addDomain = m.addDomain
  _removeDomain = m.removeDomain
  _verifyDomain = m.verifyDomain
  _enableSsl = m.enableSsl
  _fetchServerInfo = m.fetchServerInfo
  _uploadFile = m.uploadFile
} else {
  const r = await import('./real')
  _fetchSites = r.fetchSites
  _fetchSite = r.fetchSite
  _createSite = r.createSite
  _updateSite = r.updateSite
  _deleteSite = r.deleteSite
  _createPage = r.createPage
  _updatePage = r.updatePage
  _deletePage = r.deletePage
  _fetchPageBlocks = r.fetchPageBlocks
  _savePageBlocks = r.savePageBlocks
  _fetchBlockTemplates = r.fetchBlockTemplates
  _publishPage = r.publishPage
  _publishSite = r.publishSite
  _addDomain = r.addDomain
  _removeDomain = r.removeDomain
  _verifyDomain = r.verifyDomain
  _enableSsl = r.enableSsl
  _fetchServerInfo = r.fetchServerInfo
  _uploadFile = r.uploadFile
}

export const fetchSites = _fetchSites
export const fetchSite = _fetchSite
export const createSite = _createSite
export const updateSite = _updateSite
export const deleteSite = _deleteSite
export const createPage = _createPage
export const updatePage = _updatePage
export const deletePage = _deletePage
export const fetchPageBlocks = _fetchPageBlocks
export const savePageBlocks = _savePageBlocks
export const fetchBlockTemplates = _fetchBlockTemplates
export const publishPage = _publishPage
export const publishSite = _publishSite
export const addDomain = _addDomain
export const removeDomain = _removeDomain
export const verifyDomain = _verifyDomain
export const enableSsl = _enableSsl
export const fetchServerInfo = _fetchServerInfo
export const uploadFile = _uploadFile