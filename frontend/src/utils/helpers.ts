// Utility helpers: uuid, debounce, deepClone
import { v4 as uuidv4 } from 'uuid'

export function generateId(): string {
  return uuidv4()
}

export function debounce<T extends (...args: any[]) => any>(fn: T, delayMs: number): T {
  let timer: ReturnType<typeof setTimeout> | null = null
  return ((...args: any[]) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delayMs)
  }) as unknown as T
}

export function deepClone<T>(obj: T): T {
  return JSON.parse(JSON.stringify(obj))
}

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/--+/g, '-')
    .trim()
}

/** Capitalize the first letter of each word */
export function categoryLabel(category: string): string {
  const labels: Record<string, string> = {
    cover: 'Covers',
    about: 'About',
    text: 'Text',
    heading: 'Headings',
    image: 'Images & Gallery',
    button: 'Buttons',
    form: 'Forms',
    menu: 'Navigation',
    footer: 'Footer',
    video: 'Video',
    divider: 'Dividers',
    columns: 'Columns & Cards',
    zeroblock: 'Zero Block',
  }
  return labels[category] || category
}
