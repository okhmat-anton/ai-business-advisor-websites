import { computed } from 'vue'

/**
 * Returns a computed style object for a block's root element.
 * Handles backgroundColor, backgroundImage, parallax, padding, minHeight, textAlign.
 */
export function useBlockStyle(
  settings: Record<string, any>,
  extra?: Record<string, string | undefined>,
) {
  return computed(() => {
    const s: Record<string, string> = {
      containerType: 'inline-size',
      backgroundColor: settings.backgroundColor || '',
      paddingTop: settings.paddingTop || '60px',
      paddingBottom: settings.paddingBottom || '60px',
    }

    // Padding shorthand used by some blocks as padding: `${pt} 0 ${pb}`
    // Keep individual props so `:style` merges cleanly with textAlign etc.

    if (settings.backgroundImage) {
      s.backgroundImage = `url(${settings.backgroundImage})`
      s.backgroundSize = 'cover'
      s.backgroundPosition = 'center'
      if (settings.parallax) {
        s.backgroundAttachment = 'fixed'
      }
    }

    if (settings.minHeight) {
      s.minHeight = settings.minHeight
    }

    if (settings.align) {
      s.textAlign = settings.align
    }

    // Merge any extra style properties (e.g. textAlign from outer block)
    if (extra) {
      for (const [k, v] of Object.entries(extra)) {
        if (v !== undefined) s[k] = v
      }
    }

    return s
  })
}
