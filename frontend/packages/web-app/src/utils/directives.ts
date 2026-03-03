import type { Directive, DirectiveBinding } from 'vue';

/**
 * A Vue custom directive that scrolls the element into the visible area if it's the last item in a list.
 *
 * @example
 * ```html
 * <div v-for="(item, index) in list" :key="item.id" v-scroll-into-view-if-last="index === list.length - 1">
 *   {{ item.text }}
 * </div>
 * ```
 */
const vScrollIntoViewIfLast: Directive<HTMLElement, boolean> = {
  mounted(el: HTMLElement, binding: DirectiveBinding<boolean>) {
    if (binding.value) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  },
  updated(el: HTMLElement, binding: DirectiveBinding<boolean>) {
    // We only scroll if the value has changed from false to true,
    // which means a new last item has been added.
    if (binding.value && !binding.oldValue) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  },
};

export { vScrollIntoViewIfLast };