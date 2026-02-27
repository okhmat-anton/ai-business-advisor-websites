// Block registry: maps block type string to Vue component
// Used by BlockRenderer to dynamically render blocks
// Uses static imports (not async) so blocks render immediately when added

import { type Component } from 'vue'

import CoverBlock01 from '@/components/blocks/cover/CoverBlock01.vue'
import CoverBlock02 from '@/components/blocks/cover/CoverBlock02.vue'
import CoverBlock03 from '@/components/blocks/cover/CoverBlock03.vue'
import AboutBlock01 from '@/components/blocks/about/AboutBlock01.vue'
import AboutBlock02 from '@/components/blocks/about/AboutBlock02.vue'
import TextBlock01 from '@/components/blocks/text/TextBlock01.vue'
import TextBlock02 from '@/components/blocks/text/TextBlock02.vue'
import HeadingBlock01 from '@/components/blocks/heading/HeadingBlock01.vue'
import ImageBlock01 from '@/components/blocks/image/ImageBlock01.vue'
import GalleryBlock01 from '@/components/blocks/image/GalleryBlock01.vue'
import ButtonBlock01 from '@/components/blocks/button/ButtonBlock01.vue'
import FormBlock01 from '@/components/blocks/form/FormBlock01.vue'
import FormBlock02 from '@/components/blocks/form/FormBlock02.vue'
import CrmFormBlock from '@/components/blocks/form/CrmFormBlock.vue'
import MenuBlock01 from '@/components/blocks/menu/MenuBlock01.vue'
import MenuBlock02 from '@/components/blocks/menu/MenuBlock02.vue'
import FooterBlock01 from '@/components/blocks/footer/FooterBlock01.vue'
import FooterBlock02 from '@/components/blocks/footer/FooterBlock02.vue'
import VideoBlock01 from '@/components/blocks/video/VideoBlock01.vue'
import DividerBlock01 from '@/components/blocks/divider/DividerBlock01.vue'
import ColumnsBlock01 from '@/components/blocks/columns/ColumnsBlock01.vue'
import ZeroBlock from '@/components/blocks/zeroblock/ZeroBlock.vue'

const blockComponents: Record<string, Component> = {
  CoverBlock01,
  CoverBlock02,
  CoverBlock03,
  AboutBlock01,
  AboutBlock02,
  TextBlock01,
  TextBlock02,
  HeadingBlock01,
  ImageBlock01,
  GalleryBlock01,
  ButtonBlock01,
  FormBlock01,
  FormBlock02,
  CrmFormBlock,
  MenuBlock01,
  MenuBlock02,
  FooterBlock01,
  FooterBlock02,
  VideoBlock01,
  DividerBlock01,
  ColumnsBlock01,
  ZeroBlock,
}

export function getBlockComponent(type: string): Component | null {
  return blockComponents[type] || null
}

export default blockComponents

