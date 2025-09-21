import { computed, defineComponent, h, onMounted, onUnmounted, provide } from 'vue'
import type { Component } from 'vue'

import type { ComponentProps, ComponentWithModalId, NiceModalHocProps, RemoveReadonly, Simplify } from './contants'
import { ALREADY_MOUNTED, hideModalCallbacks, MODAL_REGISTRY, modalCallbacks, NICE_MODAL_ID_KEY } from './contants'
import { useModal } from './hooks'
import { useModalContext } from './store'

let uidSeed = 0

// Generate unique modal ID
const getUid = () => `_nice_modal_${uidSeed++}`

// Get modal ID helper
export function getModalId(modal: string | ComponentWithModalId): string {
  if (typeof modal === 'string')
    return modal

  if (!modal[NICE_MODAL_ID_KEY]) {
    modal[NICE_MODAL_ID_KEY] = getUid()
  }

  return modal[NICE_MODAL_ID_KEY]
}

// Register modal component
export function register<T extends Component>(id: string, comp: T, props: Partial<NiceModalHocProps> = {}) {
  if (!MODAL_REGISTRY[id]) {
    MODAL_REGISTRY[id] = { comp, props }
  }
  else {
    MODAL_REGISTRY[id].props = props
  }
}

// Unregister modal component
export function unregister(id: string) {
  delete MODAL_REGISTRY[id]
}

export function show<T = unknown, C extends Component = Component>(
  modal: string | C,
  args?: C extends string ? Record<string, unknown> : Simplify<RemoveReadonly<Omit<ComponentProps<C>, keyof NiceModalHocProps>>>,
): Promise<T> {
  const modalId = getModalId(modal)

  if (typeof modal !== 'string' && !MODAL_REGISTRY[modalId]) {
    register(modalId, modal)
  }

  const { dispatch } = useModalContext()

  dispatch({ type: 'nice-modal/show', payload: { modalId, args } })

  if (!modalCallbacks[modalId]) {
    modalCallbacks[modalId] = Promise.withResolvers()
  }

  return modalCallbacks[modalId].promise as Promise<T>
}

// Create modal component with HOC
export function create<T, C extends Component<T>>(Comp: C) {
  return defineComponent((_props: Simplify<RemoveReadonly<ComponentProps<C>>> & NiceModalHocProps, ctx) => {
    const { id, ...restProps } = ctx.attrs as T & NiceModalHocProps

    const { state } = useModalContext()
    const { show, args } = useModal(id)
    const modalInfo = computed(() => state.value[id])

    onMounted(() => {
      ALREADY_MOUNTED[id] = true
      if (modalInfo.value?.delayVisible) {
        show(args.value)
      }
    })

    onUnmounted(() => {
      delete ALREADY_MOUNTED[id]
    })

    provide(NICE_MODAL_ID_KEY, id)

    return () => {
      if (!modalInfo.value)
        return null

      return h(Comp, { ...restProps as T, ...modalInfo.value?.args })
    }
  })
}

export function hide<T = unknown>(modal: Component | string): Promise<T> {
  const modalId = getModalId(modal)

  const { dispatch } = useModalContext()

  dispatch({ type: 'nice-modal/hide', payload: { modalId } })
  delete modalCallbacks[modalId]

  if (!hideModalCallbacks[modalId]) {
    hideModalCallbacks[modalId] = Promise.withResolvers()
  }
  return hideModalCallbacks[modalId].promise as Promise<T>
}

export function remove(modal: Component | string) {
  const modalId = getModalId(modal)

  const { dispatch } = useModalContext()

  dispatch({ type: 'nice-modal/remove', payload: { modalId } })
  delete modalCallbacks[modalId]
  delete hideModalCallbacks[modalId]
}

export function antdModal(modal: ReturnType<typeof useModal>) {
  return {
    open: modal.visible,
    onCancel: () => modal.hide(),
    afterClose: () => {
      // Need to resolve before remove
      modal.resolveHide()
      modal.remove()
    },
  }
}

export function antdDrawer(modal: ReturnType<typeof useModal>) {
  return {
    open: modal.visible,
    onClose: () => modal.hide(),
    onAfterOpenChange: (v: boolean) => {
      if (!v) {
        modal.resolveHide()
        modal.remove()
      }
    },
  }
}
