import { defineAsyncComponent } from 'vue'

export const CodeEditor = defineAsyncComponent(() => import('./CodeEditor.vue'))
