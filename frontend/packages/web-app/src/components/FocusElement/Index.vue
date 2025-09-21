<script lang="ts" setup>
/**
 * This component is used to reset the focus of the input element.
 * 这个组件用于重置输入元素的焦点。
 * 缘由：聚焦的元素会被浏览器缓存，属于Chromium 的bug，若是很多节点的聚焦，可能会造成内存泄漏，所以需要手动重置焦点。
 * 改组件暴露出一个方法提供外部调用，方法名是resetFocus
 */

// const focusInput = ref(null)

// function resetFocus() {
//   if (focusInput.value) {
//     focusInput.value.focus()
//     focusInput.value.blur()
//   }
// }
</script>

<template>
  <div style="position: fixed; top: -100px;">
    <input ref="focusInput" type="text" style="visibility: hidden; width: 0px; height: 0px; ">
  </div>
</template>
