<script setup lang="ts">
const model = defineModel({ type: Boolean, default: false })

function handleClick() {
  model.value = !model.value
}
</script>

<template>
  <div class="check-box" :class="{ active: modelValue }" @click="handleClick">
    <div class="checkbox-inner" />
  </div>
</template>

<style lang="scss" scoped>
.check-box {
  display: inline-block;
  position: relative;
  width: 12px;
  height: 12px;

  &::after {
    content: '';
    display: block;
    position: absolute;
    width: 12px;
    height: 12px;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    box-sizing: border-box;
    cursor: pointer;
    transition: all 0.3s;
  }

  &:hover {
    &::after {
      border-color: var(--color-primary);
    }
  }
}

.checkbox-inner {
  position: absolute;
  width: 12px;
  height: 12px;
  border-radius: 4px;
  box-sizing: border-box;
}

.check-box.active {
  &::after {
    border-color: var(--color-primary);
  }

  .checkbox-inner {
    background-color: var(--color-primary);

    &::after {
      content: '';
      display: table;
      box-sizing: border-box;
      position: absolute;
      top: 50%;
      width: 4px;
      height: 8px;
      inset-inline-start: 25.5%;
      border: 2px solid #fff;
      border-top: 0;
      border-inline-start: 0;
      transition:
        all 0.1s cubic-bezier(0.71, -0.46, 0.88, 0.6),
        opacity 0.1s;
      opacity: 1;
      transform: rotate(45deg) scale(1) translate(-50%, -50%);
    }
  }
}
</style>
