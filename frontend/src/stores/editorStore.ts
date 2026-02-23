// Editor store - manages blocks, active block, undo/redo
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import type { IBlock, IBlockTemplate } from '@/types/block'
import { BlockCategory } from '@/types/block'
import type { IHistoryEntry } from '@/types/editor'
import { fetchPageBlocks, savePageBlocks, fetchBlockTemplates } from '@/api/mock'

const MAX_HISTORY = 50

export const useEditorStore = defineStore('editor', () => {
  // State
  const blocks = ref<IBlock[]>([])
  const activeBlockId = ref<string | null>(null)
  const isDirty = ref(false)
  const isLoading = ref(false)
  const isSaving = ref(false)
  const currentSiteId = ref<string | null>(null)
  const currentPageId = ref<string | null>(null)
  const templates = ref<IBlockTemplate[]>([])

  // Undo/Redo
  const history = ref<IHistoryEntry[]>([])
  const historyIndex = ref(-1)

  // Getters
  const activeBlock = computed(() =>
    blocks.value.find((b: IBlock) => b.id === activeBlockId.value) || null
  )

  const sortedBlocks = computed(() =>
    [...blocks.value].sort((a: IBlock, b: IBlock) => a.order - b.order)
  )

  const canUndo = computed(() => historyIndex.value > 0)
  const canRedo = computed(() => historyIndex.value < history.value.length - 1)

  const templatesByCategory = computed(() => {
    const map: Record<string, IBlockTemplate[]> = {}
    templates.value.forEach((t: IBlockTemplate) => {
      if (!map[t.category]) map[t.category] = []
      map[t.category]!.push(t)
    })
    return map
  })

  // Private helpers
  function pushHistory(description: string) {
    // Remove any forward history if we are not at the end
    if (historyIndex.value < history.value.length - 1) {
      history.value = history.value.slice(0, historyIndex.value + 1)
    }
    history.value.push({
      blocks: JSON.parse(JSON.stringify(blocks.value)),
      timestamp: Date.now(),
      description,
    })
    if (history.value.length > MAX_HISTORY) {
      history.value.shift()
    }
    historyIndex.value = history.value.length - 1
    isDirty.value = true
  }

  // Actions

  /** Load blocks for a page */
  async function loadBlocks(siteId: string, pageId: string) {
    isLoading.value = true
    currentSiteId.value = siteId
    currentPageId.value = pageId
    try {
      blocks.value = await fetchPageBlocks(pageId)
      // Initialize history with current state
      history.value = [{
        blocks: JSON.parse(JSON.stringify(blocks.value)),
        timestamp: Date.now(),
        description: 'Initial load',
      }]
      historyIndex.value = 0
      isDirty.value = false
    } finally {
      isLoading.value = false
    }
  }

  /** Load block template library */
  async function loadTemplates() {
    if (templates.value.length > 0) return
    templates.value = await fetchBlockTemplates()
  }

  /** Save current blocks to server */
  async function save() {
    if (!currentPageId.value) return
    isSaving.value = true
    try {
      await savePageBlocks(currentPageId.value, blocks.value)
      isDirty.value = false
    } finally {
      isSaving.value = false
    }
  }

  /** Add a new block from type and category */
  function addBlock(type: string, category: string, afterBlockId?: string) {
    // Find matching template for defaults
    const template = templates.value.find((t: IBlockTemplate) => t.type === type)
    const defaultContent = template ? JSON.parse(JSON.stringify(template.defaultContent)) : {}
    const defaultSettings = template ? JSON.parse(JSON.stringify(template.defaultSettings)) : {
      paddingTop: '60px', paddingBottom: '60px', backgroundColor: '#ffffff',
    }

    const newBlock: IBlock = {
      id: uuidv4(),
      type,
      category: category as BlockCategory,
      content: defaultContent,
      settings: defaultSettings,
      order: 0,
    }

    if (afterBlockId) {
      const afterIndex = blocks.value.findIndex((b: IBlock) => b.id === afterBlockId)
      if (afterIndex !== -1) {
        blocks.value.splice(afterIndex + 1, 0, newBlock)
      } else {
        blocks.value.push(newBlock)
      }
    } else {
      blocks.value.push(newBlock)
    }

    // Recalculate order
    blocks.value.forEach((b: IBlock, i: number) => (b.order = i))
    activeBlockId.value = newBlock.id
    pushHistory(`Added block: ${type}`)
  }

  /** Remove a block */
  function removeBlock(blockId: string) {
    const index = blocks.value.findIndex((b: IBlock) => b.id === blockId)
    if (index === -1) return
    blocks.value.splice(index, 1)
    blocks.value.forEach((b: IBlock, i: number) => (b.order = i))
    if (activeBlockId.value === blockId) {
      activeBlockId.value = null
    }
    pushHistory('Removed block')
  }

  /** Duplicate a block */
  function duplicateBlock(blockId: string) {
    const original = blocks.value.find((b: IBlock) => b.id === blockId)
    if (!original) return
    const clone: IBlock = {
      ...JSON.parse(JSON.stringify(original)),
      id: uuidv4(),
    }
    const index = blocks.value.findIndex((b: IBlock) => b.id === blockId)
    blocks.value.splice(index + 1, 0, clone)
    blocks.value.forEach((b: IBlock, i: number) => (b.order = i))
    activeBlockId.value = clone.id
    pushHistory('Duplicated block')
  }

  /** Move block up in order */
  function moveBlockUp(blockId: string) {
    const index = blocks.value.findIndex((b: IBlock) => b.id === blockId)
    if (index <= 0) return
    const arr = blocks.value
    ;[arr[index], arr[index - 1]] = [arr[index - 1]!, arr[index]!]
    blocks.value.forEach((b: IBlock, i: number) => (b.order = i))
    pushHistory('Moved block up')
  }

  /** Move block down in order */
  function moveBlockDown(blockId: string) {
    const index = blocks.value.findIndex((b: IBlock) => b.id === blockId)
    if (index === -1 || index >= blocks.value.length - 1) return
    const arr = blocks.value
    ;[arr[index], arr[index + 1]] = [arr[index + 1]!, arr[index]!]
    blocks.value.forEach((b: IBlock, i: number) => (b.order = i))
    pushHistory('Moved block down')
  }

  /** Update block content */
  function updateBlockContent(blockId: string, content: Record<string, any>) {
    const block = blocks.value.find((b: IBlock) => b.id === blockId)
    if (!block) return
    block.content = { ...block.content, ...content }
    pushHistory('Updated block content')
  }

  /** Update block settings */
  function updateBlockSettings(blockId: string, settings: Record<string, any>) {
    const block = blocks.value.find((b: IBlock) => b.id === blockId)
    if (!block) return
    block.settings = { ...block.settings, ...settings }
    pushHistory('Updated block settings')
  }

  /** Set active block */
  function setActiveBlock(blockId: string | null) {
    activeBlockId.value = blockId
  }

  /** Reorder blocks after drag-and-drop */
  function reorderBlocks(newBlocks: IBlock[]) {
    blocks.value = newBlocks.map((b: IBlock, i: number) => ({ ...b, order: i }))
    pushHistory('Reordered blocks')
  }

  /** Undo last action */
  function undo() {
    if (!canUndo.value) return
    historyIndex.value--
    const entry = history.value[historyIndex.value]
    if (entry) {
      blocks.value = JSON.parse(JSON.stringify(entry.blocks))
      isDirty.value = true
    }
  }

  /** Redo last undone action */
  function redo() {
    if (!canRedo.value) return
    historyIndex.value++
    const entry = history.value[historyIndex.value]
    if (entry) {
      blocks.value = JSON.parse(JSON.stringify(entry.blocks))
      isDirty.value = true
    }
  }

  return {
    // State
    blocks,
    activeBlockId,
    isDirty,
    isLoading,
    isSaving,
    currentSiteId,
    currentPageId,
    templates,
    // Getters
    activeBlock,
    sortedBlocks,
    canUndo,
    canRedo,
    templatesByCategory,
    // Actions
    loadBlocks,
    loadTemplates,
    save,
    addBlock,
    removeBlock,
    duplicateBlock,
    moveBlockUp,
    moveBlockDown,
    updateBlockContent,
    updateBlockSettings,
    setActiveBlock,
    reorderBlocks,
    undo,
    redo,
  }
})
