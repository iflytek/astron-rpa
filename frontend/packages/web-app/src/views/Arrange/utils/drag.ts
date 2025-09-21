import type { Ref } from 'vue'
import { nextTick } from 'vue'

// 添加或移动节点的过程中添加占位的dom
let listPlaceholder = null
export function draggableAddGhost(e, lastid) {
  console.log('draggableAddGhost', e, lastid)
  listPlaceholder = document.querySelector('.list-placeholder')
  const dom = document.querySelector('#listwrapper .sortable-ghost ') as HTMLElement
  console.log('draggableAddGhost dom', dom)

  // 修改样式、添加占位dom
  if (lastid && lastid === e.related.dataset.id && listPlaceholder && e.willInsertAfter) {
    // 如果拖动到最后一个节点之后，则占位节点hover展示
    listPlaceholder.className += ' active'
  }
  else if (dom) {
    const indent = Number.parseInt(e.related.dataset.indent)
    dom.style.width = `calc(100% - ${indent}px)`
    dom.style.left = `${indent - 1}px`
    // let doms = "";  TODO
    // Array.from({ length: parseInt(e.related.dataset.parentids) }).forEach((i, idx) => {
    //   doms += `<i key="sortable-ghostline${idx}" class="ghost-inner-dom ghostline" style="left:${
    //     indent - idx * PAGE_LEVEL_INDENT - 2
    //   }px"></i>`;
    // });
    // doms += `<i key="sortable-ghostborder" class="ghost-inner-dom ghostborder" style="width:calc(100% - ${indent}px);left:${indent}px"></i>`;
    // dom.innerHTML += doms;
  }
}

// 重置样式、删除占位的dom
export function draggableDelGhost() {
  const dom = document.querySelector('.ghostborder') as HTMLElement
  if (dom) {
    dom.className = dom.className.replace(/ghostborder|ghostline\d+/g, '').replace(/ghostline/g, '').trim()
    dom.removeAttribute('style')
    listPlaceholder = document.querySelector('.list-placeholder')
    if (listPlaceholder) {
      listPlaceholder.className = 'list-placeholder'
    }
    listPlaceholder = null
  }
}

export function clearDraggable(draggableRef: Ref) {
  nextTick(() => {
    if (draggableRef.value) {
      if (draggableRef.value?._sortable?.el) {
        draggableRef.value._sortable.el = null
      }
      draggableRef.value._sortable = null
    }
  })
}
