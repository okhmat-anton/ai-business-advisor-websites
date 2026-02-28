// Block type definitions for the site builder

export enum BlockCategory {
  Cover = 'cover',
  About = 'about',
  Text = 'text',
  Heading = 'heading',
  Image = 'image',
  Button = 'button',
  Form = 'form',
  Menu = 'menu',
  Footer = 'footer',
  Video = 'video',
  Divider = 'divider',
  Columns = 'columns',
  ZeroBlock = 'zeroblock',
}

export interface IBlockSettings {
  paddingTop: string
  paddingBottom: string
  backgroundColor: string
  backgroundImage?: string
  minHeight?: string       // e.g. '100vh', '600px', 'auto'
  align?: 'left' | 'center' | 'right'
  fullWidth?: boolean
  animation?: string
  customClass?: string
  cssClass?: string
  anchor?: string
  hideOnMobile?: boolean
  hideOnDesktop?: boolean
}

export interface IBlockContent {
  [key: string]: any
}

export interface IBlock {
  id: string
  type: string
  category: BlockCategory
  content: IBlockContent
  settings: IBlockSettings
  order: number
}

export interface IBlockTemplate {
  type: string
  category: BlockCategory
  name: string
  description: string
  thumbnail: string
  defaultContent: IBlockContent
  defaultSettings: IBlockSettings
  htmlTemplate: string
}

export interface IZeroBlockElement {
  id: string
  type: 'text' | 'image' | 'shape' | 'button'
  content: Record<string, any>
  position: {
    desktop: { x: number; y: number; width: number; height: number; zIndex: number }
    tablet_h: { x: number; y: number; width: number; height: number; zIndex: number }
    tablet_v: { x: number; y: number; width: number; height: number; zIndex: number }
    phone_h: { x: number; y: number; width: number; height: number; zIndex: number }
    phone_v: { x: number; y: number; width: number; height: number; zIndex: number }
  }
}

export const DEFAULT_BLOCK_SETTINGS: IBlockSettings = {
  paddingTop: '60px',
  paddingBottom: '60px',
  backgroundColor: '#ffffff',
  align: 'center',
  fullWidth: false,
}
