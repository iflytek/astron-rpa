export function highLight(rect: DOMRectT) {
  let highlight: HTMLElement | null = null
  if (highlight)
    return
  clearHighlight()
  highlight = document.createElement('div') // 遮罩 div
  highlight.className = 'rpa-highlight'
  document.querySelector('html').appendChild(highlight)
  const { width, height, left, top } = rect
  // 当前document 在浏览器中的位置
  highlight.style.top = `${Math.round(top)}px`
  highlight.style.left = `${Math.round(left)}px`
  highlight.style.width = `${Math.round(width)}px`
  highlight.style.height = `${Math.round(height)}px`
  highlight.style.display = 'block'
  setTimeout(() => {
    document.querySelector('html').removeChild(highlight)
  }, 3000)
}

export function highLightRects(rects: DOMRectT[]) {
  rects.forEach((rect) => {
    const highlight = document.createElement('div') // 遮罩 div
    highlight.className = 'rpa-highlight'
    document.querySelector('html').appendChild(highlight)

    const { width, height, left, top } = rect
    // 当前document 在浏览器中的位置
    highlight.style.top = `${Math.round(top)}px`
    highlight.style.left = `${Math.round(left)}px`
    highlight.style.width = `${Math.round(width)}px`
    highlight.style.height = `${Math.round(height)}px`
    highlight.style.display = 'block'

    setTimeout(() => {
      document.querySelector('html').removeChild(highlight)
    }, 3000)
  })
}

function clearHighlight() {
  const highlightDoms = document.querySelectorAll('.rpa-highlight')
  highlightDoms.forEach((dom) => {
    dom && document.querySelector('html').removeChild(dom)
  })
}
