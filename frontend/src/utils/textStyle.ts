/**
 * Builds an inline style object for a text element inside a block.
 *
 * - fontFamily: inherited from CSS custom properties --font-heading / --font-body
 *   that are injected at the page/canvas root level from globalSettings.
 * - fontSize / fontWeight: read from content[`${key}FontSize`] / content[`${key}FontWeight`]
 *   as set by the editor ContentPanel per-field controls.
 *
 * @param content  Block content object
 * @param key      Content field name, e.g. 'title', 'subtitle', 'text'
 * @param isHeading  true → heading font-family, false → body font-family
 */
export function textStyle(
  content: Record<string, any>,
  key: string,
  isHeading = true,
): Record<string, string> {
  const style: Record<string, string> = {
    fontFamily: isHeading
      ? 'var(--font-heading, inherit)'
      : 'var(--font-body, inherit)',
  }
  const fs = content?.[`${key}FontSize`]
  const fw = content?.[`${key}FontWeight`]
  if (fs !== undefined && fs !== '') {
    style.fontSize = typeof fs === 'number' ? `${fs}px` : String(fs)
  }
  if (fw !== undefined && fw !== '') {
    style.fontWeight = String(fw)
  }
  return style
}
