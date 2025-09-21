import { defineStore } from 'pinia'
import { ref } from 'vue'

const cursorStore = defineStore('cursorStore', () => {
  const cursorEle = ref<Range | null>(null)
  const selection = ref<Selection | null>(null)
  function handleBlur() {
    const sel = window.getSelection && window.getSelection()
    if (sel && sel.rangeCount) {
      const range = sel.getRangeAt(0)
      selection.value = sel
      cursorEle.value = range
    }
  }
  function setCursorPos(dom: HTMLElement, editableDiv: Element) {
    if (!cursorEle.value) {
      editableDiv.appendChild(dom)
      return
    }
    const { id, parentNode } = cursorEle.value.endContainer as Element
    if (id === editableDiv.id || (parentNode as Element).id === editableDiv.id) {
      cursorEle.value.insertNode(dom)
      cursorEle.value.setStartAfter(dom)
      cursorEle.value.collapse(true)
      selection.value.removeAllRanges()
      selection.value.addRange(cursorEle.value)
    }
    else {
      editableDiv.appendChild(dom)
    }
  }
  return {
    cursorEle,
    handleBlur,
    setCursorPos,
  }
})

export default cursorStore
