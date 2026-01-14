export const FILE_TYPE_IMG = {
  doc: new URL('../../assets/img/doc.png', import.meta.url).href,
  docx: new URL('../../assets/img/doc.png', import.meta.url).href,
  txt: new URL('../../assets/img/txt.png', import.meta.url).href,
  pdf: new URL('../../assets/img/pdf.png', import.meta.url).href,
}

export interface FileInfo {
  path: string,
  name: string,
  suffix: string,
  content: string, // 文件内容
  previewContent: string, // 预览内容
}

export const initFileInfo = (): FileInfo => ({
  path: '',
  name: '',
  suffix: '',
  content: '',
  previewContent: '',
})
