import type { Attachment } from '@/components/AttachmentUpload/index.vue'
import { DEFAULT_COLOR } from '@/constants/avatar'

export interface FormState {
  version: string | number // 版本
  updateLog: string // 更新日志
  name: string // 名称
  icon: string // 图标
  color: string // 图标颜色
  introduction: string // 简介
  useDescription: string // 使用说明
  video: Attachment[] // 视频地址id
  appendix: Attachment[] // 附件地址id
  enableLastVersion: boolean // 是否同步启用该版本
}

/**
 * 将后端保存的表单转为前端需要的格式
 */
export function toFrontData(data: Record<string, any> = {}): FormState {
  const { videoId, videoName, appendixId, appendixName, enableLastVersion } = data

  return {
    version: data.version,
    updateLog: '',
    name: data.name,
    icon: fromIcon(data.icon).icon,
    color: fromIcon(data.icon).color || DEFAULT_COLOR,
    introduction: data.introduction,
    useDescription: data.useDescription,
    video: videoId ? [{ uid: videoId, name: videoName, status: 'success' }] : [],
    appendix: appendixId ? [{ uid: appendixId, name: appendixName, status: 'success' }] : [],
    enableLastVersion: enableLastVersion === '1',
  }
}

/**
 * 将前端需要的格式转为后端保存的格式
 */
export function toBackData(data: FormState) {
  return {
    version: data.version,
    updateLog: data.updateLog,
    name: data.name,
    icon: toIcon(data.icon, data.color),
    introduction: data.introduction,
    useDescription: data.useDescription,
    videoId: data.video[0]?.uid,
    videoName: data.video[0]?.name,
    appendixId: data.appendix[0]?.uid,
    appendixName: data.appendix[0]?.name,
    enableLastVersion: data.enableLastVersion ? '1' : '0',
  }
}

export function toIcon(icon: string, color: string) {
  return `${icon || ''}&color=${color || ''}`
}

export function fromIcon(iconAndColor: string) {
  const [icon, color] = iconAndColor?.split('&color=') || []
  return { icon, color }
}
