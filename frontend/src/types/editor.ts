// Editor state type definitions

import type { IBlock } from './block'

export interface IHistoryEntry {
  blocks: IBlock[]
  timestamp: number
  description: string
}

export interface IEditorState {
  blocks: IBlock[]
  activeBlockId: string | null
  isDirty: boolean
  history: IHistoryEntry[]
  historyIndex: number
}

export type DevicePreviewMode = 'desktop' | 'tablet_h' | 'tablet_v' | 'phone_h' | 'phone_v'

export interface IDeviceSize {
  name: string
  label: string
  width: number
  icon: string
}

export const DEVICE_SIZES: Record<DevicePreviewMode, IDeviceSize> = {
  desktop: { name: 'desktop', label: 'Desktop', width: 1200, icon: 'mdi-monitor' },
  tablet_h: { name: 'tablet_h', label: 'Tablet Horizontal', width: 1024, icon: 'mdi-tablet' },
  tablet_v: { name: 'tablet_v', label: 'Tablet Vertical', width: 768, icon: 'mdi-tablet' },
  phone_h: { name: 'phone_h', label: 'Phone Horizontal', width: 640, icon: 'mdi-cellphone' },
  phone_v: { name: 'phone_v', label: 'Phone Vertical', width: 375, icon: 'mdi-cellphone' },
}
