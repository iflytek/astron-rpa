import type { InjectionKey, Ref } from 'vue'
import { inject } from 'vue'

export const ChainOfThoughtContextKey: InjectionKey<Ref<boolean>> = Symbol(
  'ChainOfThoughtContext',
)

export function useChainOfThought() {
  const isOpen = inject(ChainOfThoughtContextKey)

  if (!isOpen) {
    throw new Error(
      'useChainOfThought must be used within a <ChainOfThought> component',
    )
  }

  const setIsOpen = (open: boolean) => {
    isOpen.value = open
  }

  return { isOpen, setIsOpen }
}
