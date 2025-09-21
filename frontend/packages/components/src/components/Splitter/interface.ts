import type { ExtractPropTypes, PropType } from "vue"
import { stringType, functionType } from "../../utils/type"

export const splitterProps = () => {
  return {
    prefixCls: { type: String },
    layout: stringType<'horizontal' | 'vertical'>("horizontal"),
    lazy: Boolean,
    onResizeStart: functionType<(sizes: number[]) => void>(),
    onResize: functionType<(sizes: number[]) => void>(),
    onResizeEnd: functionType<(sizes: number[]) => void>()
  }
}

export const panelProps = () => {
  return {
    prefixCls: String,
    min: { type: [Number, String] },
    max: { type: [Number, String] },
    size: { type: [Number, String] },
    collapsible: [Boolean, Object] as PropType<boolean | { start?: boolean, end?: boolean }>,
    resizable: Boolean,
    defaultSize: { type: [Number, String] }
  }
}

export type SplitterProps = Partial<ExtractPropTypes<ReturnType<typeof splitterProps>>>;
export type PanelProps = Partial<ExtractPropTypes<ReturnType<typeof panelProps>>>;
