// ZIP import utility — extracts HTML pages and inlines assets (CSS, images, JS) into them
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
 * Parse a ZIP file and extract site pages with inlined assets.
 *
 * CSS is inlined as <style> tags, JS as <script> tags (not data URLs),
 * images/fonts as base64 data URLs. URL-encoded paths are decoded
 * before matching against ZIP entries.
 */
export async function parseZipFile(file: File): Promise<ZipImportResult> {
  const arrayBuffer = await file.arrayBuffer()
  const zip = await JSZip.loadAsync(arrayBuffer)
  const siteName = file.name.replace(/\.zip$/i, '')

  // Detect root directory (some ZIPs have a wrapper folder)
  const rootPrefix = detectRootPrefix(zip)

  // Collect HTML files and asset entries
  const htmlFiles: string[] = []
  const assetEntries: Array<{ path: string; relativePath: string }> = []

  zip.forEach((relativePath, entry) => {
    if (entry.dir) return
    // Skip macOS resource forks and hidden metadata files
    if (relativePath.startsWith('__MACOSX/') || relativePath.includes('/__MACOSX/')) return
    const basename = relativePath.split('/').pop() || ''
    if (basename.startsWith('._')) return
    if (basename === '.DS_Store') return

    const cleanPath = relativePath.replace(rootPrefix, '')
    if (!cleanPath) return

    if (cleanPath.match(/\.html?$/i)) {
      htmlFiles.push(relativePath)
    } else {
      assetEntries.push({ path: cleanPath, relativePath })
    }
  })

  // Build two asset maps:
  // 1) textAssetMap — raw text content for CSS & JS (to inline as <style>/<script>)
  // 2) dataUrlAssetMap — base64 data URLs for images (to inline in src/href/url())
  const textAssetMap = new Map<string, string>()
  const dataUrlAssetMap = new Map<string, string>()

  await Promise.all(
    assetEntries.map(async ({ path, relativePath }) => {
      const entry = zip.file(relativePath)
      if (!entry) return
      const ext = path.split('.').pop()?.toLowerCase() || ''

      if (ext === 'css' || ext === 'js' || ext === 'mjs') {
        // Read as text for inline embedding
        const text = await entry.async('string')
        textAssetMap.set(path, text)
      }
      // Always build a data URL for all files (images, fonts, and also CSS/JS as fallback)
      const blob = await entry.async('blob')
      const dataUrl = await blobToDataUrl(blob, getMimeType(path))
      dataUrlAssetMap.set(path, dataUrl)
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

    // Inline all referenced assets into HTML
    htmlContent = inlineAssets(htmlContent, cleanPath, textAssetMap, dataUrlAssetMap)

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
 * Inline CSS, JS, and image assets into HTML.
 * - <link rel="stylesheet" href="..."> → <style>...contents...</style>
 * - <script src="..."></script> → <script>...contents...</script>
 * - <img src="..."> and other src/href → data URLs
 * - url() in CSS → data URLs
 */
function inlineAssets(
  html: string,
  htmlPath: string,
  textAssetMap: Map<string, string>,
  dataUrlAssetMap: Map<string, string>
): string {
  const htmlDir = getHtmlDir(htmlPath)

  // 1. Inline CSS: replace <link rel="stylesheet" href="..."> with <style> tags
  html = html.replace(
    /<link\b[^>]*\bhref=["']([^"']+)["'][^>]*>/gi,
    (match, href) => {
      // Only process stylesheet links
      if (!/rel=["']stylesheet["']/i.test(match) && !/\.css(\?[^"']*)?$/i.test(href)) {
        return match
      }
      if (isExternalUrl(href)) return match

      const resolvedPath = resolveAssetPath(htmlDir, href)
      const cssText = textAssetMap.get(resolvedPath)
      if (cssText) {
        // Resolve url() references inside the CSS before inlining
        const cssDir = resolvedPath.includes('/')
          ? resolvedPath.substring(0, resolvedPath.lastIndexOf('/') + 1)
          : ''
        const processedCss = resolveCssUrls(cssText, cssDir, dataUrlAssetMap)
        return `<style>/* ${resolvedPath} */\n${processedCss}\n</style>`
      }
      return match
    }
  )

  // 2. Inline JS: replace <script src="...">...</script> with inline <script> tags
  html = html.replace(
    /<script\b([^>]*)\bsrc=["']([^"']+)["']([^>]*)>[\s\S]*?<\/script>/gi,
    (match, before, src, after) => {
      if (isExternalUrl(src)) return match

      const resolvedPath = resolveAssetPath(htmlDir, src)
      const jsText = textAssetMap.get(resolvedPath)
      if (jsText) {
        // Clone the <script> tag attributes but remove src, keep type etc.
        const attrs = (before + after)
          .replace(/\bsrc=["'][^"']*["']/gi, '')
          .replace(/\bonerror=["'][^"']*["']/gi, '') // remove onerror since we're inlining
          .trim()
        const attrsStr = attrs ? ` ${attrs}` : ''
        return `<script${attrsStr}>/* ${resolvedPath} */\n${jsText}\n</script>`
      }
      return match
    }
  )

  // 3. Replace src, href, and data-* attributes with asset paths (images, favicons, etc.)
  //    Covers: src, href, data-original, data-src, data-bg-src, data-srcset, poster, etc.
  html = html.replace(
    /(src|href|data-original|data-src|data-bg-src|data-lazy-src|poster|data-srcset)=["']([^"']+)["']/gi,
    (match, attr, path) => {
      if (isExternalUrl(path)) return match
      if (path.startsWith('data:')) return match

      const resolvedPath = resolveAssetPath(htmlDir, path)
      const dataUrl = dataUrlAssetMap.get(resolvedPath)
      if (dataUrl) {
        return `${attr}="${dataUrl}"`
      }
      return match
    }
  )

  // 4. Replace url() in inline styles and remaining <style> tags
  html = html.replace(
    /url\(["']?([^"')]+)["']?\)/gi,
    (match, path) => {
      if (isExternalUrl(path)) return match
      if (path.startsWith('data:')) return match
      const resolvedPath = resolveAssetPath(htmlDir, path)
      const dataUrl = dataUrlAssetMap.get(resolvedPath)
      if (dataUrl) {
        return `url("${dataUrl}")`
      }
      return match
    }
  )

  return html
}

/**
 * Resolve url() references inside CSS content, replacing them with data URLs
 */
function resolveCssUrls(
  cssText: string,
  cssDir: string,
  dataUrlAssetMap: Map<string, string>
): string {
  return cssText.replace(
    /url\(["']?([^"')]+)["']?\)/gi,
    (match, path) => {
      if (isExternalUrl(path)) return match
      if (path.startsWith('data:')) return match
      const resolvedPath = resolveAssetPath(cssDir, path)
      const dataUrl = dataUrlAssetMap.get(resolvedPath)
      if (dataUrl) {
        return `url("${dataUrl}")`
      }
      return match
    }
  )
}

/**
 * Get the directory portion of the HTML path (relative to root, without root prefix)
 */
function getHtmlDir(htmlPath: string): string {
  const lastSlash = htmlPath.lastIndexOf('/')
  if (lastSlash === -1) return ''
  return htmlPath.substring(0, lastSlash + 1)
}

function isExternalUrl(path: string): boolean {
  return (
    path.startsWith('http://') ||
    path.startsWith('https://') ||
    path.startsWith('//') ||
    path.startsWith('data:') ||
    path.startsWith('#') ||
    path.startsWith('mailto:') ||
    path.startsWith('tel:') ||
    path.startsWith('javascript:')
  )
}

/**
 * Resolve a relative asset path against a directory.
 * Decodes URL-encoded characters (e.g. %20 → space) so paths match ZIP entries.
 */
function resolveAssetPath(dir: string, relativePath: string): string {
  // Strip query string and fragment
  let cleanPath = relativePath.split('?')[0]!.split('#')[0]!

  // Decode URL-encoded characters (%20 → space, etc.)
  try {
    cleanPath = decodeURIComponent(cleanPath)
  } catch {
    // If decoding fails, use the original path
  }

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
  zip.forEach((relativePath) => {
    // Skip macOS resource forks and hidden metadata (same as main loop)
    if (relativePath.startsWith('__MACOSX/') || relativePath.includes('/__MACOSX/')) return
    const basename = relativePath.split('/').pop() || ''
    if (basename.startsWith('._') || basename === '.DS_Store') return
    paths.push(relativePath)
  })

  if (paths.length === 0) return ''

  // Find the first non-directory entry (usually an HTML or asset file)
  const firstFile = paths.find((p) => !p.endsWith('/'))
  const firstPath = firstFile || paths[0]
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
