// ZIP import utility — extracts HTML pages and inlines assets (CSS, images) into them
import JSZip from 'jszip'

export interface ZipImportResult {
  siteName: string
  pages: ImportedPage[]
}

export interface ImportedPage {
  fileName: string
  title: string
  slug: string
  htmlContent: string // full HTML with inlined assets
  isMain: boolean
}

/**
 * Parse a ZIP file and extract site pages with inlined assets
 */
export async function parseZipFile(file: File): Promise<ZipImportResult> {
  const arrayBuffer = await file.arrayBuffer()
  const zip = await JSZip.loadAsync(arrayBuffer)
  const siteName = file.name.replace(/\.zip$/i, '')

  // Detect root directory (some ZIPs have a wrapper folder)
  const rootPrefix = detectRootPrefix(zip)

  // Collect HTML files
  const htmlFiles: string[] = []
  const assetEntries: Array<{ path: string; relativePath: string }> = []

  zip.forEach((relativePath, entry) => {
    if (entry.dir) return
    const cleanPath = relativePath.replace(rootPrefix, '')
    if (!cleanPath) return

    if (cleanPath.match(/\.html?$/i)) {
      htmlFiles.push(relativePath)
    } else {
      assetEntries.push({ path: cleanPath, relativePath })
    }
  })

  // Build asset map — read all non-HTML files as base64 data URLs for inlining
  const assetMap = new Map<string, string>()

  await Promise.all(
    assetEntries.map(async ({ path, relativePath }) => {
      const entry = zip.file(relativePath)
      if (!entry) return
      const blob = await entry.async('blob')
      const dataUrl = await blobToDataUrl(blob, getMimeType(path))
      assetMap.set(path, dataUrl)
    })
  )

  // Process HTML files
  const pages: ImportedPage[] = []

  for (const htmlPath of htmlFiles) {
    const entry = zip.file(htmlPath)
    if (!entry) continue

    const cleanPath = htmlPath.replace(rootPrefix, '')
    let htmlContent = await entry.async('string')
    const title = extractPageTitle(htmlContent) || cleanPath.replace(/\.html?$/i, '')
    const slug = cleanPath
      .replace(/\.html?$/i, '')
      .replace(/[^a-z0-9-/]/gi, '-')
      .toLowerCase()

    const isMain = cleanPath.match(/^index\.html?$/i) !== null

    // Inline all referenced assets (CSS, JS, images) into HTML
    htmlContent = inlineAssets(htmlContent, cleanPath, assetMap)

    pages.push({
      fileName: cleanPath,
      title,
      slug: slug === 'index' ? '' : slug,
      htmlContent,
      isMain,
    })
  }

  // Sort: main page first
  pages.sort((a, b) => (a.isMain ? -1 : b.isMain ? 1 : 0))

  return { siteName, pages }
}

/**
 * Inline CSS, JS, and image assets into HTML by replacing relative paths with data URLs
 */
function inlineAssets(
  html: string,
  htmlPath: string,
  assetMap: Map<string, string>
): string {
  const htmlDir = htmlPath.includes('/')
    ? htmlPath.substring(0, htmlPath.lastIndexOf('/') + 1).replace(/^[^/]*\//, '')
    : ''

  // Replace src="" and href="" attributes with data URLs
  html = html.replace(
    /(src|href)=["']([^"']+)["']/gi,
    (match, attr, path) => {
      if (isExternalUrl(path)) return match
      const resolvedPath = resolvePath(htmlDir, path)
      const dataUrl = assetMap.get(resolvedPath)
      if (dataUrl) {
        return `${attr}="${dataUrl}"`
      }
      return match
    }
  )

  // Replace url() in inline styles and <style> tags
  html = html.replace(
    /url\(["']?([^"')]+)["']?\)/gi,
    (match, path) => {
      if (isExternalUrl(path)) return match
      const resolvedPath = resolvePath(htmlDir, path)
      const dataUrl = assetMap.get(resolvedPath)
      if (dataUrl) {
        return `url("${dataUrl}")`
      }
      return match
    }
  )

  return html
}

function isExternalUrl(path: string): boolean {
  return (
    path.startsWith('http://') ||
    path.startsWith('https://') ||
    path.startsWith('//') ||
    path.startsWith('data:') ||
    path.startsWith('#') ||
    path.startsWith('mailto:') ||
    path.startsWith('tel:')
  )
}

/**
 * Resolve a relative path against a directory
 */
function resolvePath(dir: string, relativePath: string): string {
  const cleanPath = relativePath.split('?')[0]!.split('#')[0]!

  if (cleanPath.startsWith('/')) {
    return cleanPath.substring(1)
  }

  const parts = (dir + cleanPath).split('/')
  const resolved: string[] = []
  for (const part of parts) {
    if (part === '..') {
      resolved.pop()
    } else if (part !== '.' && part !== '') {
      resolved.push(part)
    }
  }
  return resolved.join('/')
}

/**
 * Detect if all files share a common root directory
 */
function detectRootPrefix(zip: JSZip): string {
  const paths: string[] = []
  zip.forEach((path) => paths.push(path))

  if (paths.length === 0) return ''

  const firstPath = paths[0]
  if (!firstPath) return ''
  const firstSlash = firstPath.indexOf('/')
  if (firstSlash === -1) return ''

  const prefix = firstPath.substring(0, firstSlash + 1)
  const allMatch = paths.every((p) => p.startsWith(prefix))

  return allMatch ? prefix : ''
}

/**
 * Extract page title from HTML <title> tag
 */
function extractPageTitle(html: string): string | null {
  const match = html.match(/<title[^>]*>(.*?)<\/title>/is)
  return match && match[1] ? match[1].trim() : null
}

/**
 * Get MIME type from file extension
 */
function getMimeType(path: string): string {
  const ext = path.split('.').pop()?.toLowerCase() || ''
  const mimeMap: Record<string, string> = {
    jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', gif: 'image/gif',
    svg: 'image/svg+xml', webp: 'image/webp', ico: 'image/x-icon', bmp: 'image/bmp',
    avif: 'image/avif',
    css: 'text/css',
    js: 'application/javascript', mjs: 'application/javascript',
    woff: 'font/woff', woff2: 'font/woff2', ttf: 'font/ttf', otf: 'font/otf',
    eot: 'application/vnd.ms-fontobject',
    json: 'application/json', xml: 'application/xml',
  }
  return mimeMap[ext] || 'application/octet-stream'
}

/**
 * Convert Blob to data URL
 */
function blobToDataUrl(blob: Blob, mimeType: string): Promise<string> {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onloadend = () => {
      const result = reader.result as string
      if (result.startsWith('data:application/octet-stream') && mimeType !== 'application/octet-stream') {
        resolve(result.replace('data:application/octet-stream', `data:${mimeType}`))
      } else {
        resolve(result)
      }
    }
    reader.readAsDataURL(new Blob([blob], { type: mimeType }))
  })
}

/**
 * Validate that the file is a valid ZIP
 */
export function isValidZipFile(file: File): boolean {
  return (
    file.type === 'application/zip' ||
    file.type === 'application/x-zip-compressed' ||
    file.name.endsWith('.zip')
  )
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
