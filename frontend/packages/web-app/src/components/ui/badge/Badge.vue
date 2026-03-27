<script setup lang="ts">
import { cva } from 'class-variance-authority'
import { Primitive } from 'reka-ui'

import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold tracking-[-0.01em] transition-colors',
  {
    variants: {
      variant: {
        default: 'border-[var(--color-primary)]/14 bg-[linear-gradient(135deg,#F2F0FF,#E9E6FF)] text-[var(--color-primary)]',
        neutral: 'border-black/[0.05] bg-[#F4F5F8] text-black/48',
        success: 'border-[#2FCB64]/16 bg-[#2FCB64]/10 text-[#1A9D46]',
        subtle: 'border-transparent bg-transparent text-black/35',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

type BadgeVariant = 'default' | 'neutral' | 'success' | 'subtle'

type BadgeProps = {
  as?: string
  asChild?: boolean
  class?: string
  variant?: BadgeVariant
}

const props = withDefaults(defineProps<BadgeProps>(), {
  as: 'div',
})
</script>

<template>
  <Primitive
    data-slot="badge"
    :as="props.as"
    :as-child="props.asChild"
    :class="cn(badgeVariants({ variant: props.variant }), props.class)"
  >
    <slot />
  </Primitive>
</template>
