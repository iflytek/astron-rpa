<script setup lang="ts">
import { cva } from 'class-variance-authority'
import { Primitive } from 'reka-ui'

import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-medium tracking-[-0.01em] transition-all duration-200 outline-none disabled:pointer-events-none disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]/20',
  {
    variants: {
      variant: {
        default: 'bg-[linear-gradient(135deg,#726FFF,#5D59FF)] text-white shadow-[0_14px_28px_rgba(114,111,255,0.22)] hover:translate-y-[-1px] hover:shadow-[0_18px_34px_rgba(114,111,255,0.28)]',
        secondary: 'border border-black/[0.06] bg-white text-black/72 shadow-[0_8px_18px_rgba(15,23,42,0.04)] hover:border-black/[0.08] hover:bg-[#fcfcff] hover:translate-y-[-1px]',
        outline: 'border border-[var(--color-primary)]/28 bg-white text-[var(--color-primary)] shadow-[0_8px_18px_rgba(114,111,255,0.08)] hover:bg-[#faf9ff] hover:translate-y-[-1px]',
        ghost: 'text-black/55 hover:bg-[#f6f7fb]',
        soft: 'bg-[linear-gradient(135deg,#F3F1FF,#ECE9FF)] text-[var(--color-primary)] hover:bg-[#ecebff]',
        dashed: 'border border-dashed border-[var(--color-primary)]/45 bg-white text-[var(--color-primary)] hover:bg-[#faf9ff]',
      },
      size: {
        sm: 'h-9 px-3.5',
        default: 'h-10 px-4',
        lg: 'h-11 px-5',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

type ButtonVariant = 'default' | 'secondary' | 'outline' | 'ghost' | 'soft' | 'dashed'
type ButtonSize = 'sm' | 'default' | 'lg' | 'icon'

type ButtonProps = {
  as?: string
  asChild?: boolean
  class?: string
  size?: ButtonSize
  variant?: ButtonVariant
}

const props = withDefaults(defineProps<ButtonProps>(), {
  as: 'button',
})
</script>

<template>
  <Primitive
    data-slot="button"
    :as="props.as"
    :as-child="props.asChild"
    :class="cn(buttonVariants({ variant: props.variant, size: props.size }), props.class)"
  >
    <slot />
  </Primitive>
</template>
