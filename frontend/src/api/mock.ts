// Mock data for sites API
import { v4 as uuidv4 } from 'uuid'
import type { ISite, IPage } from '@/types/site'
import type { IBlock, IBlockTemplate, BlockCategory } from '@/types/block'

// Simulated delay for realistic behavior
const delay = (ms: number = 300) => new Promise((resolve) => setTimeout(resolve, ms))

// ========== BLOCK TEMPLATES (library) ==========
export const BLOCK_TEMPLATES: IBlockTemplate[] = [
  // Cover blocks
  {
    type: 'CoverBlock01',
    category: 'cover' as BlockCategory,
    name: 'Cover with centered text',
    description: 'Full-width cover with centered heading, subheading, and CTA button',
    thumbnail: '',
    defaultContent: {
      title: 'Welcome to Our Website',
      subtitle: 'We create amazing digital experiences',
      buttonText: 'Learn More',
      buttonUrl: '#',
      backgroundImage: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920',
      overlayOpacity: 0.5,
    },
    defaultSettings: {
      paddingTop: '0px',
      paddingBottom: '0px',
      backgroundColor: '#1a1a2e',
      align: 'center',
      fullWidth: true,
    },
    htmlTemplate: '',
  },
  {
    type: 'CoverBlock02',
    category: 'cover' as BlockCategory,
    name: 'Cover with left-aligned text',
    description: 'Cover with text on the left side and image background',
    thumbnail: '',
    defaultContent: {
      title: 'Build Something Great',
      subtitle: 'Start your journey with us today',
      buttonText: 'Get Started',
      buttonUrl: '#',
      backgroundImage: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1920',
      overlayOpacity: 0.6,
    },
    defaultSettings: {
      paddingTop: '0px',
      paddingBottom: '0px',
      backgroundColor: '#0f3460',
      align: 'left',
      fullWidth: true,
    },
    htmlTemplate: '',
  },
  {
    type: 'CoverBlock03',
    category: 'cover' as BlockCategory,
    name: 'Cover with video background',
    description: 'Full-screen cover with video background placeholder',
    thumbnail: '',
    defaultContent: {
      title: 'Innovation Starts Here',
      subtitle: 'Transforming ideas into reality',
      buttonText: 'Watch Video',
      buttonUrl: '#',
      backgroundImage: 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1920',
      overlayOpacity: 0.4,
    },
    defaultSettings: {
      paddingTop: '0px',
      paddingBottom: '0px',
      backgroundColor: '#16213e',
      align: 'center',
      fullWidth: true,
    },
    htmlTemplate: '',
  },

  // About blocks
  {
    type: 'AboutBlock01',
    category: 'about' as BlockCategory,
    name: 'About with image on the right',
    description: 'Text on left, image on right',
    thumbnail: '',
    defaultContent: {
      title: 'About Our Company',
      text: 'We are a team of dedicated professionals committed to delivering exceptional results. With years of experience in the industry, we understand what it takes to succeed.',
      image: 'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=800',
    },
    defaultSettings: {
      paddingTop: '80px',
      paddingBottom: '80px',
      backgroundColor: '#ffffff',
      align: 'left',
    },
    htmlTemplate: '',
  },
  {
    type: 'AboutBlock02',
    category: 'about' as BlockCategory,
    name: 'About with counters',
    description: 'Description text with stat counters',
    thumbnail: '',
    defaultContent: {
      title: 'What We Do',
      text: 'Our mission is to help businesses grow through innovative technology solutions.',
      counters: [
        { value: '150+', label: 'Projects Done' },
        { value: '50+', label: 'Happy Clients' },
        { value: '10+', label: 'Years Experience' },
        { value: '25', label: 'Team Members' },
      ],
    },
    defaultSettings: {
      paddingTop: '80px',
      paddingBottom: '80px',
      backgroundColor: '#f8f9fa',
      align: 'center',
    },
    htmlTemplate: '',
  },

  // Text blocks
  {
    type: 'TextBlock01',
    category: 'text' as BlockCategory,
    name: 'Simple text block',
    description: 'Basic text block with title and paragraph',
    thumbnail: '',
    defaultContent: {
      title: 'Section Title',
      text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.',
    },
    defaultSettings: {
      paddingTop: '60px',
      paddingBottom: '60px',
      backgroundColor: '#ffffff',
      align: 'center',
    },
    htmlTemplate: '',
  },
  {
    type: 'TextBlock02',
    category: 'text' as BlockCategory,
    name: 'Two-column text',
    description: 'Text split into two columns',
    thumbnail: '',
    defaultContent: {
      title: 'Our Approach',
      leftText: 'We believe in a methodical approach to solving complex problems. Our team takes the time to understand your unique challenges.',
      rightText: 'With cutting-edge tools and proven methodologies, we deliver solutions that are both innovative and practical.',
    },
    defaultSettings: {
      paddingTop: '60px',
      paddingBottom: '60px',
      backgroundColor: '#ffffff',
      align: 'left',
    },
    htmlTemplate: '',
  },

  // Heading block
  {
    type: 'HeadingBlock01',
    category: 'heading' as BlockCategory,
    name: 'Section heading',
    description: 'Large heading with optional subtitle',
    thumbnail: '',
    defaultContent: {
      title: 'Section Heading',
      subtitle: 'Optional subtitle text goes here',
      level: 'h2',
    },
    defaultSettings: {
      paddingTop: '40px',
      paddingBottom: '20px',
      backgroundColor: '#ffffff',
      align: 'center',
    },
    htmlTemplate: '',
  },

  // Image blocks
  {
    type: 'ImageBlock01',
    category: 'image' as BlockCategory,
    name: 'Single image',
    description: 'Full-width image with optional caption',
    thumbnail: '',
    defaultContent: {
      image: 'https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=1200',
      alt: 'Image description',
      caption: '',
    },
    defaultSettings: {
      paddingTop: '40px',
      paddingBottom: '40px',
      backgroundColor: '#ffffff',
      align: 'center',
    },
    htmlTemplate: '',
  },
  {
    type: 'GalleryBlock01',
    category: 'image' as BlockCategory,
    name: 'Image gallery',
    description: 'Grid of images with lightbox',
    thumbnail: '',
    defaultContent: {
      images: [
        { src: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600', alt: 'Image 1' },
        { src: 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=600', alt: 'Image 2' },
        { src: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=600', alt: 'Image 3' },
        { src: 'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=600', alt: 'Image 4' },
      ],
      columns: 2,
    },
    defaultSettings: {
      paddingTop: '40px',
      paddingBottom: '40px',
      backgroundColor: '#ffffff',
      align: 'center',
    },
    htmlTemplate: '',
  },

  // Button block
  {
    type: 'ButtonBlock01',
    category: 'button' as BlockCategory,
    name: 'Button group',
    description: 'One or two call-to-action buttons',
    thumbnail: '',
    defaultContent: {
      buttons: [
        { text: 'Primary Action', url: '#', style: 'primary' },
        { text: 'Secondary Action', url: '#', style: 'outlined' },
      ],
    },
    defaultSettings: {
      paddingTop: '40px',
      paddingBottom: '40px',
      backgroundColor: '#ffffff',
      align: 'center',
    },
    htmlTemplate: '',
  },

  // Form blocks
  {
    type: 'CrmFormBlock',
    category: 'form' as BlockCategory,
    name: 'CRM Form',
    description: 'Embed a form from AKM Advisor CRM directly on your page',
    thumbnail: '',
    defaultContent: {
      title: '',
      subtitle: '',
      formId: '',
      formName: '',
      formSlug: '',
      embedCode: '',
    },
    defaultSettings: {
      paddingTop: '60px',
      paddingBottom: '60px',
      backgroundColor: '#ffffff',
      align: 'center',
    },
    htmlTemplate: '',
  },
  {
    type: 'FormBlock01',
    category: 'form' as BlockCategory,
    name: 'Contact form',
    description: 'Simple contact form with name, email, and message fields',
    thumbnail: '',
    defaultContent: {
      title: 'Contact Us',
      subtitle: 'Fill out the form and we\'ll get back to you',
      fields: [
        { type: 'text', label: 'Name', placeholder: 'Your name', required: true },
        { type: 'email', label: 'Email', placeholder: 'your@email.com', required: true },
        { type: 'textarea', label: 'Message', placeholder: 'Your message...', required: true },
      ],
      submitText: 'Send Message',
      successMessage: 'Thank you! We will contact you soon.',
    },
    defaultSettings: {
      paddingTop: '80px',
      paddingBottom: '80px',
      backgroundColor: '#f8f9fa',
      align: 'center',
    },
    htmlTemplate: '',
  },
  {
    type: 'FormBlock02',
    category: 'form' as BlockCategory,
    name: 'Subscription form',
    description: 'Email subscription form with inline input',
    thumbnail: '',
    defaultContent: {
      title: 'Stay Updated',
      subtitle: 'Subscribe to our newsletter',
      placeholder: 'Enter your email',
      submitText: 'Subscribe',
      successMessage: 'You have been subscribed!',
    },
    defaultSettings: {
      paddingTop: '60px',
      paddingBottom: '60px',
      backgroundColor: '#1a1a2e',
      align: 'center',
    },
    htmlTemplate: '',
  },

  // Menu blocks
  {
    type: 'MenuBlock01',
    category: 'menu' as BlockCategory,
    name: 'Navigation bar',
    description: 'Horizontal navigation with logo and links',
    thumbnail: '',
    defaultContent: {
      logo: 'My Site',
      links: [
        { text: 'Home', url: '#' },
        { text: 'About', url: '#about' },
        { text: 'Services', url: '#services' },
        { text: 'Contact', url: '#contact' },
      ],
      ctaButton: { text: 'Get Started', url: '#' },
    },
    defaultSettings: {
      paddingTop: '0px',
      paddingBottom: '0px',
      backgroundColor: '#ffffff',
      align: 'center',
      fullWidth: true,
    },
    htmlTemplate: '',
  },
  {
    type: 'MenuBlock02',
    category: 'menu' as BlockCategory,
    name: 'Transparent navigation',
    description: 'Transparent overlay navigation bar',
    thumbnail: '',
    defaultContent: {
      logo: 'Brand',
      links: [
        { text: 'Home', url: '#' },
        { text: 'Portfolio', url: '#portfolio' },
        { text: 'Blog', url: '#blog' },
        { text: 'Contact', url: '#contact' },
      ],
    },
    defaultSettings: {
      paddingTop: '0px',
      paddingBottom: '0px',
      backgroundColor: 'transparent',
      align: 'center',
      fullWidth: true,
    },
    htmlTemplate: '',
  },

  // Footer blocks
  {
    type: 'FooterBlock01',
    category: 'footer' as BlockCategory,
    name: 'Simple footer',
    description: 'Footer with copyright and social links',
    thumbnail: '',
    defaultContent: {
      copyright: '© 2026 My Company. All rights reserved.',
      socialLinks: [
        { icon: 'mdi-facebook', url: '#' },
        { icon: 'mdi-twitter', url: '#' },
        { icon: 'mdi-instagram', url: '#' },
      ],
    },
    defaultSettings: {
      paddingTop: '40px',
      paddingBottom: '40px',
      backgroundColor: '#1a1a2e',
      align: 'center',
    },
    htmlTemplate: '',
  },
  {
    type: 'FooterBlock02',
    category: 'footer' as BlockCategory,
    name: 'Multi-column footer',
    description: 'Footer with multiple link columns and contact info',
    thumbnail: '',
    defaultContent: {
      logo: 'My Site',
      description: 'Building the future of web design.',
      columns: [
        {
          title: 'Company',
          links: [
            { text: 'About', url: '#' },
            { text: 'Careers', url: '#' },
            { text: 'Blog', url: '#' },
          ],
        },
        {
          title: 'Support',
          links: [
            { text: 'Help Center', url: '#' },
            { text: 'Contact', url: '#' },
            { text: 'Privacy', url: '#' },
          ],
        },
      ],
      copyright: '© 2026 My Company',
    },
    defaultSettings: {
      paddingTop: '60px',
      paddingBottom: '40px',
      backgroundColor: '#0f0f23',
      align: 'left',
    },
    htmlTemplate: '',
  },

  // Video block
  {
    type: 'VideoBlock01',
    category: 'video' as BlockCategory,
    name: 'Video embed',
    description: 'Embedded YouTube or Vimeo video',
    thumbnail: '',
    defaultContent: {
      videoUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
      title: 'Watch Our Story',
      aspectRatio: '16/9',
    },
    defaultSettings: {
      paddingTop: '60px',
      paddingBottom: '60px',
      backgroundColor: '#000000',
      align: 'center',
    },
    htmlTemplate: '',
  },

  // Divider block
  {
    type: 'DividerBlock01',
    category: 'divider' as BlockCategory,
    name: 'Horizontal divider',
    description: 'Simple line divider with optional spacing',
    thumbnail: '',
    defaultContent: {
      style: 'solid',
      width: '100px',
      color: '#dee2e6',
    },
    defaultSettings: {
      paddingTop: '30px',
      paddingBottom: '30px',
      backgroundColor: '#ffffff',
      align: 'center',
    },
    htmlTemplate: '',
  },

  // Columns block
  {
    type: 'ColumnsBlock01',
    category: 'columns' as BlockCategory,
    name: 'Three-column cards',
    description: 'Three cards with icon, title, and description',
    thumbnail: '',
    defaultContent: {
      title: 'Our Services',
      cards: [
        { icon: 'mdi-palette', title: 'Design', text: 'Beautiful, modern designs that capture your brand essence.' },
        { icon: 'mdi-code-braces', title: 'Development', text: 'Robust, scalable solutions built with cutting-edge technology.' },
        { icon: 'mdi-rocket-launch', title: 'Marketing', text: 'Strategic campaigns that drive growth and engagement.' },
      ],
    },
    defaultSettings: {
      paddingTop: '80px',
      paddingBottom: '80px',
      backgroundColor: '#ffffff',
      align: 'center',
    },
    htmlTemplate: '',
  },
]

// ========== LOCAL STORAGE PERSISTENCE ==========
const STORAGE_KEY_SITES = 'mock_sites'
const STORAGE_KEY_BLOCKS = 'mock_blocks'

function loadFromStorage<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    if (raw) return JSON.parse(raw)
  } catch { /* ignore parse errors */ }
  return fallback
}

function saveToStorage(key: string, data: unknown): void {
  try {
    localStorage.setItem(key, JSON.stringify(data))
  } catch { /* ignore quota errors */ }
}

function persistSites() { saveToStorage(STORAGE_KEY_SITES, mockSites) }
function persistBlocks() { saveToStorage(STORAGE_KEY_BLOCKS, mockBlocks) }

// ========== MOCK DATABASE (persisted in localStorage) ==========
const DEFAULT_SITES: ISite[] = [
  {
    id: 'site-1',
    userId: 'user-1',
    name: 'My First Website',
    description: 'A portfolio website',
    globalSettings: {
      fonts: { heading: 'Inter', body: 'Inter' },
      colors: { primary: '#1976D2', secondary: '#424242', accent: '#FF5252', background: '#ffffff', text: '#212121' },
    },
    domains: [],
    pages: [
      {
        id: 'page-1',
        siteId: 'site-1',
        title: 'Home',
        slug: '/',
        blocks: ['block-1', 'block-2', 'block-3', 'block-4'],
        seo: { title: 'Home - My First Website', description: 'Welcome to my website', keywords: 'portfolio, web' },
        status: 'draft',
        isMain: true,
        createdAt: '2026-01-01T00:00:00Z',
        updatedAt: '2026-01-15T00:00:00Z',
      },
      {
        id: 'page-2',
        siteId: 'site-1',
        title: 'About',
        slug: '/about',
        blocks: [],
        seo: { title: 'About - My First Website', description: 'Learn more about us', keywords: 'about' },
        status: 'draft',
        isMain: false,
        createdAt: '2026-01-02T00:00:00Z',
        updatedAt: '2026-01-10T00:00:00Z',
      },
    ],
    status: 'draft',
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: '2026-02-20T00:00:00Z',
  },
]

const DEFAULT_BLOCKS: Record<string, IBlock[]> = {
  'page-1': [
    {
      id: 'block-1',
      type: 'MenuBlock01',
      category: 'menu' as BlockCategory,
      content: { logo: 'MyBrand', links: [{ text: 'Home', url: '#' }, { text: 'About', url: '#about' }, { text: 'Contact', url: '#contact' }], ctaButton: { text: 'Get Started', url: '#' } },
      settings: { paddingTop: '0px', paddingBottom: '0px', backgroundColor: '#ffffff', align: 'center', fullWidth: true },
      order: 0,
    },
    {
      id: 'block-2',
      type: 'CoverBlock01',
      category: 'cover' as BlockCategory,
      content: { title: 'Welcome to My Portfolio', subtitle: 'Designer & Developer', buttonText: 'View Work', buttonUrl: '#work', backgroundImage: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920', overlayOpacity: 0.5 },
      settings: { paddingTop: '0px', paddingBottom: '0px', backgroundColor: '#1a1a2e', align: 'center', fullWidth: true },
      order: 1,
    },
    {
      id: 'block-3',
      type: 'ColumnsBlock01',
      category: 'columns' as BlockCategory,
      content: { title: 'What I Do', cards: [{ icon: 'mdi-palette', title: 'UI/UX Design', text: 'Creating intuitive user interfaces.' }, { icon: 'mdi-code-braces', title: 'Web Development', text: 'Building fast, modern websites.' }, { icon: 'mdi-cellphone', title: 'Mobile Apps', text: 'Cross-platform mobile solutions.' }] },
      settings: { paddingTop: '80px', paddingBottom: '80px', backgroundColor: '#ffffff', align: 'center' },
      order: 2,
    },
    {
      id: 'block-4',
      type: 'FooterBlock01',
      category: 'footer' as BlockCategory,
      content: { copyright: '© 2026 MyBrand. All rights reserved.', socialLinks: [{ icon: 'mdi-github', url: '#' }, { icon: 'mdi-linkedin', url: '#' }] },
      settings: { paddingTop: '40px', paddingBottom: '40px', backgroundColor: '#1a1a2e', align: 'center' },
      order: 3,
    },
  ],
}

let mockSites: ISite[] = loadFromStorage(STORAGE_KEY_SITES, DEFAULT_SITES)
let mockBlocks: Record<string, IBlock[]> = loadFromStorage(STORAGE_KEY_BLOCKS, DEFAULT_BLOCKS)

// ========== MOCK API FUNCTIONS ==========

// Sites
export async function fetchSites(): Promise<ISite[]> {
  await delay()
  return JSON.parse(JSON.stringify(mockSites))
}

export async function fetchSite(siteId: string): Promise<ISite | null> {
  await delay()
  const site = mockSites.find((s) => s.id === siteId)
  return site ? JSON.parse(JSON.stringify(site)) : null
}

export async function createSite(name: string, description?: string, isImported?: boolean): Promise<ISite> {
  await delay()
  const site: ISite = {
    id: uuidv4(),
    userId: 'user-1',
    name,
    description,
    isImported: isImported || false,
    globalSettings: {
      fonts: { heading: 'Inter', body: 'Inter' },
      colors: { primary: '#1976D2', secondary: '#424242', accent: '#FF5252', background: '#ffffff', text: '#212121' },
    },
    domains: [],
    pages: [
      {
        id: uuidv4(),
        siteId: '',
        title: 'Home',
        slug: '/',
        blocks: [],
        seo: { title: `${name} - Home`, description: '', keywords: '' },
        status: 'draft',
        isMain: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ],
    status: 'draft',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }
  if (site.pages[0]) {
    site.pages[0].siteId = site.id
  }
  mockSites.push(site)
  persistSites()
  return JSON.parse(JSON.stringify(site))
}

export async function updateSite(siteId: string, data: Partial<ISite>): Promise<ISite | null> {
  await delay()
  const index = mockSites.findIndex((s) => s.id === siteId)
  if (index === -1) return null
  const existing = mockSites[index]!
  mockSites[index] = { ...existing, ...data, updatedAt: new Date().toISOString() } as ISite
  persistSites()
  return JSON.parse(JSON.stringify(mockSites[index]))
}

export async function deleteSite(siteId: string): Promise<boolean> {
  await delay()
  const index = mockSites.findIndex((s) => s.id === siteId)
  if (index === -1) return false
  mockSites.splice(index, 1)
  delete mockBlocks[siteId]
  persistSites()
  persistBlocks()
  return true
}

// Pages
export async function createPage(siteId: string, title: string, slug: string): Promise<IPage | null> {
  await delay()
  const site = mockSites.find((s) => s.id === siteId)
  if (!site) return null
  const page: IPage = {
    id: uuidv4(),
    siteId,
    title,
    slug,
    blocks: [],
    seo: { title, description: '', keywords: '' },
    status: 'draft',
    isMain: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }
  site.pages.push(page)
  persistSites()
  return JSON.parse(JSON.stringify(page))
}

export async function deletePage(siteId: string, pageId: string): Promise<boolean> {
  await delay()
  const site = mockSites.find((s) => s.id === siteId)
  if (!site) return false
  const index = site.pages.findIndex((p) => p.id === pageId)
  if (index === -1) return false
  site.pages.splice(index, 1)
  delete mockBlocks[pageId]
  persistSites()
  persistBlocks()
  return true
}

export async function updatePage(siteId: string, pageId: string, data: Partial<IPage>): Promise<IPage | null> {
  await delay()
  const site = mockSites.find((s) => s.id === siteId)
  if (!site) return null
  const page = site.pages.find((p) => p.id === pageId)
  if (!page) return null
  Object.assign(page, data, { updatedAt: new Date().toISOString() })
  persistSites()
  return JSON.parse(JSON.stringify(page))
}

// Blocks
export async function fetchPageBlocks(pageId: string): Promise<IBlock[]> {
  await delay()
  return JSON.parse(JSON.stringify(mockBlocks[pageId] || []))
}

export async function savePageBlocks(pageId: string, blocks: IBlock[]): Promise<boolean> {
  await delay()
  mockBlocks[pageId] = JSON.parse(JSON.stringify(blocks))
  persistBlocks()
  return true
}

// Block templates (library)
export async function fetchBlockTemplates(): Promise<IBlockTemplate[]> {
  await delay(100)
  return JSON.parse(JSON.stringify(BLOCK_TEMPLATES))
}

// Publish
export async function publishPage(siteId: string, pageId: string): Promise<boolean> {
  await delay(500)
  const site = mockSites.find((s) => s.id === siteId)
  if (!site) return false
  const page = site.pages.find((p) => p.id === pageId)
  if (!page) return false
  page.status = 'published'
  persistSites()
  return true
}

export async function publishSite(siteId: string): Promise<boolean> {
  await delay(800)
  const site = mockSites.find((s) => s.id === siteId)
  if (!site) return false
  site.status = 'published'
  site.pages.forEach((p) => (p.status = 'published'))
  persistSites()
  return true
}

// ========== Domains (mock stubs) ==========

export async function addDomain(siteId: string, domainName: string): Promise<import('@/types/site').IDomain> {
  await delay(300)
  const site = mockSites.find((s) => s.id === siteId)
  if (!site) throw new Error('Site not found')
  const domain: import('@/types/site').IDomain = {
    id: uuidv4(),
    siteId,
    domainName,
    sslStatus: 'none',
    isPrimary: false,
    isVerified: false,
    createdAt: new Date().toISOString(),
  }
  site.domains.push(domain)
  persistSites()
  return domain
}

export async function removeDomain(siteId: string, domainId: string): Promise<boolean> {
  await delay(300)
  const site = mockSites.find((s) => s.id === siteId)
  if (!site) return false
  site.domains = site.domains.filter((d) => d.id !== domainId)
  persistSites()
  return true
}

export async function verifyDomain(siteId: string, domainId: string): Promise<import('./real').DomainVerifyResult> {
  await delay(1000)
  return {
    isVerified: false,
    domainName: 'example.com',
    resolvedIps: [],
    expectedIp: '127.0.0.1',
    message: 'Mock: DNS verification not available in mock mode',
  }
}

export async function enableSsl(siteId: string, domainId: string): Promise<{ status: string; message: string }> {
  await delay(1000)
  return { status: 'error', message: 'Mock: SSL not available in mock mode' }
}

export async function fetchServerInfo(): Promise<{ serverIp: string }> {
  await delay(100)
  return { serverIp: '127.0.0.1' }
}

// Mock file upload — sends to real backend local disk storage so the URL persists
// across page reloads and works in published static HTML.
export async function uploadFile(file: File): Promise<{ url: string; filename: string }> {
  const formData = new FormData()
  formData.append('file', file)
  try {
    const { default: apiClient } = await import('./index')
    const { data } = await apiClient.post('/uploads', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    const url: string = data.url || ''
    const filename: string = data.filename || file.name
    return { url, filename }
  } catch {
    // Fallback to blob URL if backend is not available (local dev without backend)
    const url = URL.createObjectURL(file)
    return { url, filename: file.name }
  }
}
