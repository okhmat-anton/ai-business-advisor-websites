// Auto-save composable - debounced saving of blocks
import { watch, onUnmounted, ref } from 'vue'
import { useEditorStore } from '@/stores/editorStore'

export function useAutoSave(intervalMs: number = 5000) {
  const editorStore = useEditorStore()
  const lastSaved = ref<Date | null>(null)
  let timer: ReturnType<typeof setInterval> | null = null

  function startAutoSave() {
    timer = setInterval(async () => {
      if (editorStore.isDirty && !editorStore.isSaving) {
        await editorStore.save()
        lastSaved.value = new Date()
      }
    }, intervalMs)
  }

  function stopAutoSave() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  // Start auto-save when composable is used
  startAutoSave()

  onUnmounted(() => {
    stopAutoSave()
  })

  return {
    lastSaved,
    startAutoSave,
    stopAutoSave,
    cleanup: stopAutoSave,
  }
}
