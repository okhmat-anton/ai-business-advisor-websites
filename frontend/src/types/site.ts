// Site and page type definitions

export interface ISeoSettings {
  title: string
  description: string
  keywords?: string
  ogImage?: string
  canonicalUrl?: string
  noIndex?: boolean
}

export interface IPage {
  id: string
  siteId: string
  title: string
  slug: string
  blocks: string[] // block IDs in order
  htmlContent?: string // raw HTML for imported pages
  seo: ISeoSettings
  status: 'draft' | 'published'
  isMain: boolean
  isHomePage?: boolean
  createdAt: string
  updatedAt: string
}

export interface ISiteGlobalSettings {
  fonts?: {
    heading: string
    body: string
  }
  colors?: {
    primary: string
    secondary: string
    accent: string
    background: string
    text: string
  }
  primaryColor?: string
  fontFamily?: string
  customCss?: string
  headScripts?: string
  favicon?: string
  headerBlockId?: string
  footerBlockId?: string
}

export interface IDomain {
  id: string
  siteId?: string
  domain?: string
  domainName?: string
  sslStatus?: 'none' | 'pending' | 'active' | 'error'
  isPrimary?: boolean
  isVerified?: boolean
  createdAt?: string
}

export interface ISite {
  id: string
  userId: string
  name: string
  description?: string
  subdomain?: string
  favicon?: string
  isPublished?: boolean
  isImported?: boolean
  globalSettings: ISiteGlobalSettings
  domains: IDomain[]
  pages: IPage[]
  status: 'draft' | 'published'
  createdAt: string
  updatedAt: string
}
