import { VxeLoading, VxeTooltip, VxeUI } from 'vxe-pc-ui'
import type { VxeGridProps, VxeTablePropTypes } from 'vxe-table'
import { VxeGrid } from 'vxe-table'

import 'vxe-table/lib/style.css'
import 'vxe-pc-ui/lib/style.css'
import zhCN from 'vxe-table/lib/locale/lang/zh-CN'

VxeUI.setI18n('zh-CN', zhCN)
VxeUI.setLanguage('zh-CN')
VxeUI.component(VxeGrid)
VxeUI.component(VxeTooltip)
VxeUI.component(VxeLoading)

export type { VxeGridProps, VxeTablePropTypes }
export default VxeGrid
