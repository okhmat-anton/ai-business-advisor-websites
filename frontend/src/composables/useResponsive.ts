// Responsive preview composable - device mode switching
import { computed } from 'vue'
import { useUiStore } from '@/stores/uiStore'
import { DEVICE_SIZES } from '@/types/editor'
import type { DevicePreviewMode } from '@/types/editor'

export function useResponsive() {
  const uiStore = useUiStore()

  const currentDevice = computed(() => uiStore.devicePreview)
  const currentWidth = computed(() => {
    const size = DEVICE_SIZES[uiStore.devicePreview as DevicePreviewMode]
    return size ? size.width : 1200
  })
  const deviceList = computed(() => Object.values(DEVICE_SIZES))

  function setDevice(mode: DevicePreviewMode) {
    uiStore.setDevicePreview(mode)
  }

  return {
    currentDevice,
    currentWidth,
    deviceList,
    setDevice,
    DEVICE_SIZES,
  }
}
