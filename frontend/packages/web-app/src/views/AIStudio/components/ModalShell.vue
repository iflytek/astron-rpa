<script setup lang="ts">
import { X } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  title: string
  description?: string
  widthClass?: string
  closeLabel?: string
  overlayClass?: string
  panelClass?: string
  bodyClass?: string
  headerClass?: string
  overlayTestId?: string
  panelTestId?: string
  bodyTestId?: string
  closeOnBackdrop?: boolean
  showCloseButton?: boolean
}>(), {
  overlayClass: '',
  panelClass: '',
  bodyClass: '',
  headerClass: '',
  overlayTestId: undefined,
  panelTestId: undefined,
  bodyTestId: undefined,
  closeOnBackdrop: true,
  showCloseButton: true,
})

const emit = defineEmits<{
  (e: 'close'): void
}>()

function handleBackdropClick() {
  if (!props.closeOnBackdrop)
    return
  emit('close')
}
</script>

<template>
  <div
    :data-testid="props.overlayTestId"
    class="fixed inset-0 z-40 flex items-center justify-center bg-[rgba(15,23,42,0.22)] px-6 py-8 backdrop-blur-[4px]"
    :class="props.overlayClass"
    @click.self="handleBackdropClick"
  >
    <div
      :data-testid="props.panelTestId"
      :class="[props.widthClass || 'w-[520px]', props.panelClass]"
      class="max-h-[calc(100vh-110px)] overflow-hidden rounded-[26px] bg-[rgba(255,255,255,0.98)] shadow-[0_28px_90px_rgba(15,23,42,0.18)] backdrop-blur-[18px]"
    >
      <div
        :class="props.headerClass"
        class="relative flex items-start justify-between gap-4 px-6 py-5"
      >
        <div class="pointer-events-none absolute inset-x-6 bottom-0 h-px bg-[linear-gradient(90deg,rgba(228,234,245,0)_0%,rgba(228,234,245,0.94)_18%,rgba(228,234,245,0.94)_82%,rgba(228,234,245,0)_100%)]" />
        <div class="min-w-0 flex-1">
          <div class="flex items-start gap-2.5">
            <div
              v-if="$slots.icon"
              class="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-[12px] bg-[rgba(247,249,253,0.92)] text-black/54"
            >
              <slot name="icon" />
            </div>
            <div class="min-w-0">
              <div class="truncate text-[16px] font-semibold text-black/88">
                {{ props.title }}
              </div>
              <div
                v-if="props.description"
                class="mt-1 text-[12px] text-black/42"
              >
                {{ props.description }}
              </div>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <slot name="header-actions" />
          <button
            v-if="props.showCloseButton"
            :aria-label="props.closeLabel || '关闭弹层'"
            class="flex h-8 w-8 items-center justify-center rounded-[12px] bg-[rgba(247,249,253,0.92)] text-black/46 transition-colors hover:bg-white hover:text-black/62"
            @click="emit('close')"
          >
            <X class="h-4 w-4" />
          </button>
        </div>
      </div>

      <div
        :data-testid="props.bodyTestId"
        :class="props.bodyClass"
        class="max-h-[calc(100vh-220px)] overflow-y-auto"
      >
        <slot />
      </div>
    </div>
  </div>
</template>
