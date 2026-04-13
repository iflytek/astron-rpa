import { ref, computed, onMounted } from 'vue'
import { windowManager } from '@/platform'
import { PickShortCuts, PickMode } from '../config'
import { RpaHighlight } from '@/api/highlight'

export function useHighlight() {
  const dpr = window.devicePixelRatio || 1
  const highlightRect = ref({ x: 0, y: 0, width: 0, height: 0 })
  const mousePos = ref({ x: 0, y: 0 })
  const pickMode = ref(PickMode.NORMAL)
  const appName = ref('')
  const tagName = ref('')
  const tooltipVisible = ref(true)

  const tooltipPos = computed(() => {
    const margin = 300
    const mouse = mousePos.value
    if (mouse.x < margin && mouse.y < margin) {
      return 'rightBottom'
    }
    if (mouse.x > (screen.width - margin) * dpr && mouse.y > (screen.height - margin) * dpr) {
      return 'leftTop'
    }
    return 'rightBottom'
  })

  const tagPosition = computed(() => {
    const rect = highlightRect.value
    return rect.y < 60 ? 'bottom' : 'top'
  })

  const shortcuts = computed(() => PickShortCuts[pickMode.value] || [])

  onMounted(() => {
    RpaHighlight.create(() => {
      RpaHighlight.bindMessage((data) => {
        const op = data.Operation
        if (op === 'start') {
          windowManager.showWindow()
          if (data.Type) pickMode.value = data.Type
        } else if (op === 'hide') {
          windowManager.hideWindow()
          highlightRect.value = { x: 0, y: 0, width: 0, height: 0 }
          tagName.value = ''
        } else if (op === 'draw') {
          const boxes = data.Boxes
          if (boxes && boxes.length > 0) {
            const box = boxes[0]
            highlightRect.value = {
              x: box.Left,
              y: box.Top,
              width: (box.Right - box.Left) / dpr,
              height: (box.Bottom - box.Top) / dpr,
            }
            if (box.Msg !== undefined) tagName.value = box.Msg
          }
        }
        windowManager.setWindowAlwaysOnTop(true)
      })
    })
  })

  return {
    dpr,
    highlightRect,
    mousePos,
    pickMode,
    appName,
    tagName,
    tooltipVisible,
    tooltipPos,
    tagPosition,
    shortcuts,
  }
}
