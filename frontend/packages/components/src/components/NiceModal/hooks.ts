import type { Component } from 'vue'
import { computed, inject } from 'vue'

import type { ComponentProps, NiceModalHocProps, RemoveReadonly, Simplify } from './contants'
import { hideModalCallbacks, MODAL_REGISTRY, modalCallbacks, NICE_MODAL_ID_KEY } from './contants'
import { useModalContext } from './store'
import { getModalId, hide, register, remove, show } from './utils'

export function useModal<C extends Component>(
  modal?: C | string,
  args?: typeof modal extends string ? Record<string, unknown> : Simplify<RemoveReadonly<Omit<ComponentProps<C>, keyof NiceModalHocProps>>>,
) {
  const { state } = useModalContext()

  const isUseComponent = modal && typeof modal !== 'string'
  const modalId = modal ? getModalId(modal) : inject<string>(NICE_MODAL_ID_KEY)

  if (!modalId) {
    throw new Error('[nice-modal-vue] No modal id found in useModal')
  }

  if (isUseComponent && !MODAL_REGISTRY[modalId]) {
    register(modalId, modal, args)
  }

  const modalInfo = computed(() => state.value[modalId])

  const api = {
    id: modalId,
    args: computed(() => modalInfo.value?.args),
    get visible() {
      return !!modalInfo.value?.visible
    },
    set visible(val: boolean) {
      val ? show(modalId, args) : hide(modalId)
    },
    show: (_args?: typeof args) => show(modalId, _args),
    hide: () => hide(modalId),
    remove: () => remove(modalId),
    resolve: (args?: unknown) => {
      modalCallbacks[modalId]?.resolve(args)
      delete modalCallbacks[modalId]
    },
    reject: (args?: unknown) => {
      modalCallbacks[modalId]?.reject(args)
      delete modalCallbacks[modalId]
    },
    resolveHide: (args?: unknown) => {
      hideModalCallbacks[modalId]?.resolve(args)
      delete hideModalCallbacks[modalId]
    },
  }

  return api
}
