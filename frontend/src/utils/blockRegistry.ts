// Block registry: maps block type string to Vue component
// Used by BlockRenderer to dynamically render blocks

import { defineAsyncComponent, type Component } from 'vue'

const blockComponents: Record<string, Component> = {
  // Covers
  CoverBlock01: defineAsyncComponent(() => import('@/components/blocks/cover/CoverBlock01.vue')),
  CoverBlock02: defineAsyncComponent(() => import('@/components/blocks/cover/CoverBlock02.vue')),
  CoverBlock03: defineAsyncComponent(() => import('@/components/blocks/cover/CoverBlock03.vue')),
  // About
  AboutBlock01: defineAsyncComponent(() => import('@/components/blocks/about/AboutBlock01.vue')),
  AboutBlock02: defineAsyncComponent(() => import('@/components/blocks/about/AboutBlock02.vue')),
  // Text
  TextBlock01: defineAsyncComponent(() => import('@/components/blocks/text/TextBlock01.vue')),
  TextBlock02: defineAsyncComponent(() => import('@/components/blocks/text/TextBlock02.vue')),
  // Heading
  HeadingBlock01: defineAsyncComponent(() => import('@/components/blocks/heading/HeadingBlock01.vue')),
  // Image
  ImageBlock01: defineAsyncComponent(() => import('@/components/blocks/image/ImageBlock01.vue')),
  GalleryBlock01: defineAsyncComponent(() => import('@/components/blocks/image/GalleryBlock01.vue')),
  // Button
  ButtonBlock01: defineAsyncComponent(() => import('@/components/blocks/button/ButtonBlock01.vue')),
  // Form
  FormBlock01: defineAsyncComponent(() => import('@/components/blocks/form/FormBlock01.vue')),
  FormBlock02: defineAsyncComponent(() => import('@/components/blocks/form/FormBlock02.vue')),
  // Menu
  MenuBlock01: defineAsyncComponent(() => import('@/components/blocks/menu/MenuBlock01.vue')),
  MenuBlock02: defineAsyncComponent(() => import('@/components/blocks/menu/MenuBlock02.vue')),
  // Footer
  FooterBlock01: defineAsyncComponent(() => import('@/components/blocks/footer/FooterBlock01.vue')),
  FooterBlock02: defineAsyncComponent(() => import('@/components/blocks/footer/FooterBlock02.vue')),
  // Video
  VideoBlock01: defineAsyncComponent(() => import('@/components/blocks/video/VideoBlock01.vue')),
  // Divider
  DividerBlock01: defineAsyncComponent(() => import('@/components/blocks/divider/DividerBlock01.vue')),
  // Columns
  ColumnsBlock01: defineAsyncComponent(() => import('@/components/blocks/columns/ColumnsBlock01.vue')),
  // Zero Block
  ZeroBlock: defineAsyncComponent(() => import('@/components/blocks/zeroblock/ZeroBlock.vue')),
}

export function getBlockComponent(type: string): Component | null {
  return blockComponents[type] || null
}

export default blockComponents
