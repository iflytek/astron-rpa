<script setup lang="ts">
import { ArrowDownOutlined, ArrowUpOutlined, CloseOutlined } from '@ant-design/icons-vue'
import { Divider } from 'ant-design-vue'
import { isNil } from 'lodash-es'
import { computed, useTemplateRef } from 'vue'

const props = defineProps<{ total: number, active: number }>()
const inputText = defineModel<string>('value')
const emits = defineEmits(['close', 'previous', 'next'])

const inputRef = useTemplateRef<{ focus: () => void }>("inputRef")

const calculateCount = computed(() => {
  if (!inputText.value)
    return undefined
  return props.total === 0 ? '0/0' : `${props.active}/${props.total}`
})

function close() {
  emits('close')
}

function up() {
  emits('previous')
}

function down() {
  emits('next')
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'ArrowUp') {
    e.preventDefault()
    e.stopPropagation()
    up()
  } else if (e.key === 'ArrowDown') {
    e.preventDefault()
    e.stopPropagation()
    down()
  }
}

function focus() {
  inputRef.value.focus()
}

defineExpose({
  focus,
})
</script>

<template>
  <a-card class="search-widget" :bordered="true">
    <div class="search-widget-container">
      <a-input
        ref="inputRef"
        v-model:value="inputText"
        auto-focus
        :placeholder="$t('search')"
        @press-enter="down"
        @keydown="handleKeydown"
      />
      <span v-if="!isNil(calculateCount)" class="search-widget-total">
        {{ calculateCount }}
      </span>
      <Divider type="vertical" class="search-widget-divider" />
      <div class="search-widget-icon" @click="up">
        <ArrowUpOutlined />
      </div>
      <div class="search-widget-icon" @click="down">
        <ArrowDownOutlined />
      </div>
      <div class="search-widget-icon" @click="close">
        <CloseOutlined />
      </div>
    </div>
  </a-card>
</template>

<style scoped lang="scss">
.search-widget {
  :deep(.ant-card-body) {
    padding: 3px 10px 3px 0;
    width: 310px;
  }

  :deep(.ant-input) {
    border: none;
    box-shadow: none;
    flex: 1;
    font-size: 12px;
    background-color: transparent;
  }

  &-container {
    display: flex;
    align-items: center;
    gap: 5px;
    line-height: 1;
  }

  &-divider {
    position: static;
    height: 16px;
    margin: 0 5px;
  }

  &-icon {
    font-size: 12px;
    display: inline-flex;
    cursor: pointer;
    padding: 5px;

    &:hover {
      color: $color-primary;
    }
  }
}
</style>
