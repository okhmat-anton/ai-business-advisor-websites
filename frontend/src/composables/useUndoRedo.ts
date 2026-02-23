// Undo/Redo composable with keyboard shortcuts
import { onMounted, onUnmounted } from 'vue'
import { useEditorStore } from '@/stores/editorStore'

export function useUndoRedo() {
  const editorStore = useEditorStore()

  function handleKeydown(e: KeyboardEvent) {
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0
    const modifier = isMac ? e.metaKey : e.ctrlKey

    if (modifier && e.key === 'z' && !e.shiftKey) {
      e.preventDefault()
      editorStore.undo()
    }
    if (modifier && e.key === 'z' && e.shiftKey) {
      e.preventDefault()
      editorStore.redo()
    }
    if (modifier && e.key === 'y') {
      e.preventDefault()
      editorStore.redo()
    }
    if (modifier && e.key === 's') {
      e.preventDefault()
      editorStore.save()
    }
  }

  function setup() {
    window.addEventListener('keydown', handleKeydown)
  }

  function cleanup() {
    window.removeEventListener('keydown', handleKeydown)
  }

  onMounted(setup)
  onUnmounted(cleanup)

  return {
    cleanup,
    undo: editorStore.undo,
    redo: editorStore.redo,
    canUndo: editorStore.canUndo,
    canRedo: editorStore.canRedo,
  }
}
