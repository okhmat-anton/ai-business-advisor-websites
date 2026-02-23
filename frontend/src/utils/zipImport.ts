// ZIP import utility - parses uploaded ZIP archive and creates site structure
import JSZip from 'jszip'
import { v4 as uuidv4 } from 'uuid'
import type { IBlock } from '@/types/block'
import type { IPage } from '@/types/site'
import { BlockCategory, DEFAULT_BLOCK_SETTINGS } from '@/types/block'

export interface ZipImportResult {
  siteName: string
  pages: ImportedPage[]
  assets: ImportedAsset[]
}

export interface ImportedPage {
  title: string
  slug: string
  htmlContent: string
  blocks: IBlock[]
  isMain: boolean
}

export interface ImportedAsset {
  path: string
  type: 'image' | 'style' | 'script' | 'font' | 'other'
  content: Blob
  url?: string // objectURL for preview
}

/**
 * Parse a ZIP file and extract site structure
 */
export async function parseZipFile(file: File): Promise<ZipImportResult> {
  // Read file as ArrayBuffer first — passing File directly can fail in some environments
  const arrayBuffer = await file.arrayBuffer()
  const zip = await JSZip.loadAsync(arrayBuffer)
  const siteName = file.name.replace(/\.zip$/i, '')

  const pages: ImportedPage[] = []
  const assets: ImportedAsset[] = []

  // Detect root directory (some ZIPs have a wrapper folder)
  const rootPrefix = detectRootPrefix(zip)

  // Collect all files
  const htmlFiles: string[] = []
  const assetFiles: string[] = []

  zip.forEach((relativePath, entry) => {
    if (entry.dir) return
    const cleanPath = relativePath.replace(rootPrefix, '')
    if (!cleanPath) return

    if (cleanPath.match(/\.html?$/i)) {
      htmlFiles.push(relativePath)
    } else {
      assetFiles.push(relativePath)
    }
  })

  // Process assets first (images, CSS, JS, fonts)
  for (const assetPath of assetFiles) {
    const entry = zip.file(assetPath)
    if (!entry) continue

    const cleanPath = assetPath.replace(rootPrefix, '')
    const blob = await entry.async('blob')
    const assetType = classifyAsset(cleanPath)

    const objectURL = assetType === 'image' ? URL.createObjectURL(blob) : undefined

    assets.push({
      path: cleanPath,
      type: assetType,
      content: blob,
      url: objectURL,
    })
  }

  // Process HTML files
  for (const htmlPath of htmlFiles) {
    const entry = zip.file(htmlPath)
    if (!entry) continue

    const cleanPath = htmlPath.replace(rootPrefix, '')
    const htmlContent = await entry.async('string')
    const title = extractPageTitle(htmlContent) || cleanPath.replace(/\.html?$/i, '')
    const slug = cleanPath
      .replace(/\.html?$/i, '')
      .replace(/[^a-z0-9-]/gi, '-')
      .toLowerCase()

    // Determine if main page
    const isMain = cleanPath.match(/^index\.html?$/i) !== null

    // Parse HTML into blocks
    const blocks = parseHtmlToBlocks(htmlContent, assets)

    pages.push({
      title,
      slug: slug === 'index' ? '' : slug,
      htmlContent,
      blocks,
      isMain,
    })
  }

  // If no main page found, mark the first one
  if (pages.length > 0 && !pages.some((p) => p.isMain)) {
    const firstPage = pages[0]
    if (firstPage) firstPage.isMain = true
  }

  // Sort: main page first
  pages.sort((a, b) => (a.isMain ? -1 : b.isMain ? 1 : 0))

  return { siteName, pages, assets }
}

/**
 * Detect if all files share a common root directory
 */
function detectRootPrefix(zip: JSZip): string {
  const paths: string[] = []
  zip.forEach((path) => paths.push(path))

  if (paths.length === 0) return ''

  // Check if all paths start with a common directory
  const firstPath = paths[0]
  if (!firstPath) return ''
  const firstSlash = firstPath.indexOf('/')
  if (firstSlash === -1) return ''

  const prefix = firstPath.substring(0, firstSlash + 1)
  const allMatch = paths.every((p) => p.startsWith(prefix))

  return allMatch ? prefix : ''
}

/**
 * Classify asset type by file extension
 */
function classifyAsset(path: string): ImportedAsset['type'] {
  const ext = path.split('.').pop()?.toLowerCase() || ''

  if (['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp', 'ico', 'bmp', 'avif'].includes(ext)) {
    return 'image'
  }
  if (['css', 'scss', 'less'].includes(ext)) {
    return 'style'
  }
  if (['js', 'mjs', 'ts'].includes(ext)) {
    return 'script'
  }
  if (['woff', 'woff2', 'ttf', 'otf', 'eot'].includes(ext)) {
    return 'font'
  }
  return 'other'
}

/**
 * Extract page title from HTML <title> tag
 */
function extractPageTitle(html: string): string | null {
  const match = html.match(/<title[^>]*>(.*?)<\/title>/is)
  return match && match[1] ? match[1].trim() : null
}

/**
 * Parse HTML content into block structures.
 * Creates a combination of recognized blocks and raw HTML (ZeroBlock) blocks.
 */
function parseHtmlToBlocks(html: string, assets: ImportedAsset[]): IBlock[] {
  const blocks: IBlock[] = []
  let order = 0

  // Extract body content
  const bodyMatch = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i)
  const bodyContent = bodyMatch?.[1] ?? html

  // Try to find common structural sections
  const parser = new DOMParser()
  const doc = parser.parseFromString(`<div>${bodyContent}</div>`, 'text/html')
  const root = doc.body.firstElementChild

  if (!root || !root.children.length) {
    // Whole page as a single ZeroBlock
    blocks.push(createHtmlBlock(bodyContent, order++))
    return blocks
  }

  // Walk through top-level elements and try to identify block types
  for (const element of Array.from(root.children)) {
    const el = element as HTMLElement
    const tagName = el.tagName.toLowerCase()
    const classNames = (el.className as string) || ''
    const outerHtml = el.outerHTML

    // Try to identify common patterns
    if (tagName === 'nav' || (typeof classNames === 'string' && classNames.match(/\b(nav|menu|header|navbar)\b/i))) {
      blocks.push(createTypedBlock('MenuBlock01', BlockCategory.Menu, {
        html: outerHtml,
      }, order++))
    } else if (tagName === 'footer' || (typeof classNames === 'string' && classNames.match(/\bfooter\b/i))) {
      blocks.push(createTypedBlock('FooterBlock01', BlockCategory.Footer, {
        html: outerHtml,
      }, order++))
    } else if (typeof classNames === 'string' && classNames.match(/\b(hero|cover|banner|jumbotron)\b/i)) {
      blocks.push(createTypedBlock('CoverBlock01', BlockCategory.Cover, {
        html: outerHtml,
        title: extractTextContent(el, 'h1') || 'Cover',
        subtitle: extractTextContent(el, 'p') || '',
      }, order++))
    } else if (tagName === 'section' || tagName === 'div' || tagName === 'article') {
      // Generic section — import as HTML block
      blocks.push(createHtmlBlock(outerHtml, order++))
    } else {
      // Everything else — raw HTML
      blocks.push(createHtmlBlock(outerHtml, order++))
    }
  }

  // If no blocks were created, wrap everything
  if (blocks.length === 0) {
    blocks.push(createHtmlBlock(bodyContent, order++))
  }

  return blocks
}

/**
 * Create a ZeroBlock (raw HTML) block
 */
function createHtmlBlock(html: string, order: number): IBlock {
  return {
    id: uuidv4(),
    type: 'ZeroBlock',
    category: BlockCategory.ZeroBlock,
    content: {
      html,
      elements: [],
    },
    settings: {
      ...DEFAULT_BLOCK_SETTINGS,
      paddingTop: '0px',
      paddingBottom: '0px',
    },
    order,
  }
}

/**
 * Create a typed block with parsed content
 */
function createTypedBlock(
  type: string,
  category: BlockCategory,
  content: Record<string, any>,
  order: number
): IBlock {
  return {
    id: uuidv4(),
    type,
    category,
    content,
    settings: { ...DEFAULT_BLOCK_SETTINGS },
    order,
  }
}

/**
 * Extract text content from first matching child element
 */
function extractTextContent(parent: HTMLElement, selector: string): string | null {
  const el = parent.querySelector(selector)
  return el ? el.textContent?.trim() || null : null
}

/**
 * Validate that the file is a valid ZIP
 */
export function isValidZipFile(file: File): boolean {
  return file.type === 'application/zip' ||
    file.type === 'application/x-zip-compressed' ||
    file.name.endsWith('.zip')
}

/**
 * Get human-readable file size
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`
}
