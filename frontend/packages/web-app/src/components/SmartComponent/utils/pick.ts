import { ref, toRaw } from 'vue'

import { isBase64Image, trimBase64Header } from '@/utils/common'

import type { ElementsType } from '@/types/resource'
import { VISUALIZATION } from '@/views/Arrange/config/pick'
import { elementCustomFormat, elementCustomFormatRecover, elementDirectoryFormat, elementDirectoryFormatRecover } from '@/views/Arrange/utils/elementsUtils'

/**
 * 获取当前元素最新数据
 * 处理部分数据格式
 * @param currentElement 当前元素对象
 * @param isSave 是否为保存操作
 * @returns 处理后的元素数据
 */
export function getLatestCurrentElementData(currentElement: ElementsType, isSave: boolean) {
  const detailElementData = ref(JSON.parse(currentElement.elementData))
  const { version, type, path } = detailElementData.value
  const customData = ref(elementCustomFormat(version, type, path))
  const nodeSourceData = ref(elementDirectoryFormat(version, type, path))
  const { checkType, matchTypes } = path || {}
  const formOption = ref({
    matchTypes: matchTypes || [],
    editXPathType: checkType || VISUALIZATION,
  })

  let elementPathData
  let elementData
  if (type === 'web') {
    const customDataMap = toRaw(
      elementCustomFormatRecover(version, type, customData.value),
    ) // url, xpath, cssSelector
    const pathDirs = toRaw(
      elementDirectoryFormatRecover(version, type, nodeSourceData.value),
    ) // pathDirs
    elementPathData = {
      ...detailElementData.value.path,
      ...customDataMap,
      pathDirs,
      checkType: formOption.value.editXPathType,
      matchTypes: formOption.value.matchTypes,
    }
    if (isSave) {
      // 删除掉不需要的数据
      'img' in detailElementData.value && delete detailElementData.value.img
      'similarCount' in elementPathData && delete elementPathData.similarCount
      'rect' in elementPathData && delete elementPathData.rect
    }
    elementData = {
      ...detailElementData.value, // 元素外层数据
      path: elementPathData, // 元素路径数据
    }
  }
  else {
    elementPathData = elementDirectoryFormatRecover(
      version,
      type,
      nodeSourceData.value,
    ) // path 数据
    const selfImg = currentElement.imageUrl
    const parentImg = currentElement.parentImageUrl
    // 保存时若是base64图片，则不保存base64
    const img = isSave
      ? {
          self: isBase64Image(selfImg) ? '' : selfImg,
          parent: isBase64Image(parentImg) ? '' : parentImg,
        }
      : {
          self: isBase64Image(selfImg) ? trimBase64Header(selfImg) : selfImg,
          parent: isBase64Image(parentImg)
            ? trimBase64Header(parentImg)
            : parentImg,
        }
    elementData = {
      ...detailElementData.value, // 元素数据
      img,
      path: elementPathData,
    }
    if (elementData.picker_type === 'SIMILAR') {
      // uia 相似度元素，保存时变更 字段
      elementData.img = {
        self: isBase64Image(selfImg) ? '' : selfImg,
        parent: isBase64Image(parentImg) ? '' : parentImg,
      }
      elementData.similar_count ? delete elementData.similar_count : ''
    }
  }
  return elementData
}
