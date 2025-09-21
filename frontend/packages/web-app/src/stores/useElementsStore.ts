import { message } from 'ant-design-vue'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRoute } from 'vue-router'

import { addBase64Header, base64ToFile, isBase64Image } from '@/utils/common'
import BUS from '@/utils/eventBus'

// 元素信息
import {
  addElement,
  addElementGroup,
  createElementCopy,
  delElementGroup,
  getElementDetail,
  getElementsAll,
  moveElement,
  postDeleteElement,
  renameElementGroup,
  updateElement,
  uploadFile,
} from '@/api/resource'
import type { ElementsTree, ElementsType, PickElementType, PickStepType } from '@/types/resource.d'
import { useGlobalDataUpdate } from '@/views/Arrange/hook/useGlobalDataUpdate'

export const useElementsStore = defineStore('elements', () => {
  const route = useRoute()
  const elements = ref<ElementsTree[]>([])
  const { elementDeleteAndUpdateFlow, elementRenameAndUpdateFlow } = useGlobalDataUpdate()
  const selectedElement = ref<ElementsType>({
    id: '',
    name: '',
    elementData: '',
  }) // 选中元素

  const currentElement = ref<ElementsType>({
    id: '',
    name: '',
    elementData: '',
  }) // 当前元素

  // 设置当前元素
  const setCurrentElement = (data: ElementsType) => {
    currentElement.value = data
  }

  // 设置所有元素
  const setElements = (data: ElementsTree[]) => {
    // 重组数据
    elements.value = data.map((item) => {
      const elements = (item.elements ?? []).map(eleItem => ({
        ...eleItem,
        groupName: item.name, // 分组名称
        groupId: item.id, // 分组id
      }))
      return { ...item, groupName: item.name, elements }
    })
  }
  // 设置选中元素
  const setSelectedElement = (data: ElementsType) => {
    selectedElement.value = data
  }
  // 重置选中元素
  const resetSelectedElement = () => {
    Object.keys(selectedElement.value).forEach((key) => {
      selectedElement.value[key] = ''
    })
    setSelectedElement(selectedElement.value)
  }
  // 重置当前元素
  const resetCurrentElement = () => {
    Object.keys(currentElement.value).forEach((key) => {
      currentElement.value[key] = ''
    })
    setCurrentElement(currentElement.value)
  }
  // 请求所有元素
  const requestAllElements = async () => {
    resetSelectedElement()
    const robotId = route.query?.projectId as string
    const { data } = await getElementsAll({ robotId, elementType: 'common' })
    if (data) {
      setElements(data)
    }
    return data || []
  }
  // 请求到当前元素
  const requestElementDetail = async (params: ElementsType) => {
    const robotId = route.query?.projectId as string
    const elementId = params.id
    const { data } = await getElementDetail({ robotId, elementId })
    setCurrentElement(data)
    return data
  }
  // 请求到当前元素
  const renameElement = async (params: ElementsType) => {
    console.log('params: ', params)
    const _name = params.name.trim()
    if (_name === '') {
      message.error('请输入元素名称')
      return
    }

    const robotId = route.query?.projectId as string
    await getElementDetail({ robotId, elementId: params.id })
    const res = await updateElement({
      robotId,
      element: {
        id: params.id,
        name: _name,
      },
    })
    if (res) {
      message.success('修改成功')
      await requestAllElements()
      elementRenameAndUpdateFlow({ ...params, name: _name })
    }
  }

  /**
   * 新增元素(不需要经过编辑，将拾取到的数据直接上传)
   * TODO：部分功能和下面的 saveElement 重复，需要优化
   * @param data 元素数据
   */
  const addNewElement = async (data: PickElementType) => {
    const groupName = data.app
    const robotId = route.query?.projectId as string
    const elementData = JSON.stringify(data)
    const name = generateName(data)
    const imageUrl = data.img.self ? addBase64Header(data.img.self) : ''
    const parentImageUrl = data.img.parent ? addBase64Header(data.img.parent) : ''

    const [imageId, parentImageId] = await Promise.all([
      isBase64Image(imageUrl) ? uploadFile({ file: base64ToFile(imageUrl, 'image.png') }) : '',
      isBase64Image(parentImageUrl) ? uploadFile({ file: base64ToFile(parentImageUrl, 'parent_image.png') }) : '',
    ])

    const res = await addElement({
      type: 'common',
      robotId,
      groupName,
      element: {
        commonSubType: 'single',
        name,
        icon: '',
        imageId,
        parentImageId,
        elementData,
      },
    })

    return { ...res.data, name }
  }

  // 保存当前元素
  const saveElement = async (data: PickElementType, name: string, emit = true) => {
    const robotId = route.query?.projectId as string
    const { groupName, id, imageUrl, parentImageUrl } = currentElement.value
    const elementData = JSON.stringify(data)
    const icon = '' // Array.isArray(data.elementData.path) ? "" : data.elementData.path.favIconUrl
    const isNew = isNewElement(id)
    const fileName = `${id}.png`

    const [imageId, parentImageId] = await Promise.all([
      isBase64Image(imageUrl) ? uploadFile({ file: base64ToFile(imageUrl, fileName) }) : '',
      isBase64Image(parentImageUrl) ? uploadFile({ file: base64ToFile(parentImageUrl, `parent_${fileName}`) }) : '',
    ])

    // 判断是否是新元素, 则新增
    if (isNew) {
      const { data } = await addElement({
        type: 'common',
        robotId,
        groupName,
        element: {
          commonSubType: 'single',
          name,
          icon,
          imageId,
          parentImageId,
          elementData,
        },
      })
      emit && BUS.$emit('pick-done', { data: data.elementId, value: name }) // 通知其他组件拾取已完成
    }
    else {
      // 更新当前元素
      const oldName = currentElement.value.name
      const elementId = currentElement.value.id
      const newElement: ElementsType = {
        ...currentElement.value,
        name,
        elementData,
      }
      if (imageId) {
        newElement.imageId = imageId
      }
      if (parentImageId) {
        newElement.parentImageId = parentImageId
      }
      await updateElement({
        robotId,
        element: newElement,
      })
      if (oldName !== name) {
        // 名称有变化
        elementRenameAndUpdateFlow({ elementId, name })
      }
    }
    resetCurrentElement()
    await requestAllElements()
  }
  // 删除当前元素
  const deleteElement = async (data: ElementsType) => {
    const _data = { ...data }
    const robotId = route.query?.projectId as string
    await postDeleteElement({
      robotId,
      elementId: _data.id,
    })
    await requestAllElements()
    elementDeleteAndUpdateFlow({ elementIds: [_data.id] })
  }
  // 将树形结构转换为扁平结构
  function convertTreeToFlat(tree: ElementsTree[]) {
    const flat: ElementsType[] = []
    for (const item of tree) {
      item.elements.forEach((child) => {
        flat.push(child)
      })
    }
    return flat
  }

  // 校验重名
  function checkName(name: string, elementId?: string) {
    const flat = convertTreeToFlat(elements.value)
    const ele = flat.find(item => item.id === elementId)
    if (ele) {
      // 编辑元素时，排除自身
      return flat.some(item => item.name === name && item.id !== elementId)
    }
    return flat.some(item => item.name === name)
  }

  // 生成唯一名称
  function generateName(data: PickElementType) {
    const { type, path } = data

    const genName = (name: string) => {
      if (checkName(name)) {
        const index = name.match(/\d+$/) ? Number.parseInt(name.match(/\d+$/)[0]) + 1 : 1
        const newName = `${name.replace(/\d+$/, '')}${index}`
        return genName(newName)
      }
      return name
    }

    // 去掉字符串中控制字符，空格， 特殊字符
    function removeControlChars(str: string) {
      const specialChars = /[!@#$%^&*(),.?":{}|<>]/g
      return str.replace(specialChars, '').replace(/[\x00-\x1F\x7F-\x9F\s]+/g, '').replace(' ', '')
    }

    let tag = ''
    let text = ''

    if (type === 'web' && 'tag' in path) {
      tag = path.tag || '未知标签'
      text = path.text || '未知名称'
    }
    else if (path && Array.isArray(path)) {
      tag = path[path.length - 1].tag_name || '未知标签'
      text = path[path.length - 1].name || path[path.length - 1].value || '未知名称'
    }

    text = removeControlChars(text.substring(0, 10)) || '未知名称'
    return genName(`${tag}_${text}_1`)
  }

  // 校验是否是新元素
  function isNewElement(elementId: string) {
    const flat = convertTreeToFlat(elements.value)
    return flat.every(item => item.id !== elementId)
  }

  /**
   * 设置当前缓存元素
   * @param data 元素数据
   * @param pickStep 拾取步骤 'new' | 'repick' | 'similar
   * @returns Promise
   */
  const setTempElement = (data: PickElementType, pickStep: PickStepType = 'new', group?: string) => {
    return new Promise((resolve) => {
      const { app, type, img } = data
      const elementData = JSON.stringify({
        ...data,
        // 元素图片, 存储后则为图片地址
        img: { self: '', parent: '' },
      })
      let element: ElementsType
      const groupName = group || app
      const icon = ''
      let imageUrl = ''
      let parentImageUrl = ''

      if (pickStep === 'new') {
        const name = generateName(data)
        imageUrl = img.self ? addBase64Header(img.self) : ''
        parentImageUrl = img.parent ? addBase64Header(img.parent) : ''
        element = { name, imageUrl, parentImageUrl, groupName, icon, elementData }
      }
      else if (pickStep === 'repick') {
        imageUrl = img.self ? addBase64Header(img.self) : ''
        parentImageUrl = img.parent ? addBase64Header(img.parent) : ''
        // 重新拾取元素，图片， elementData 需要替换
        element = { ...currentElement.value, imageUrl, parentImageUrl, elementData }
      }
      else if (pickStep === 'similar') {
        if (type === 'web') {
          // 相似元素仅替换 currentElement.value.elementData
          element = { ...currentElement.value, elementData }
        }
        else {
          // 相似元素仅替换 currentElement.value.elementData
          element = { ...currentElement.value, elementData }
        }
      }
      setCurrentElement(element)
      resolve(true)
    })
  }

  // 获取元素的父组
  const getParentGroup = (groupName: string) => {
    return elements.value.find(item => item.groupName === groupName)
  }

  // 新增分组
  const addGroup = (groupName: string) => {
    return new Promise((resolve, reject) => {
      addElementGroup({ robotId: route.query?.projectId as string, groupName, elementType: 'common' }).then(() => {
        message.success('新增成功')
        requestAllElements()
        resolve(true)
      }).catch((err) => {
        reject(err)
      })
    })
  }

  // 分组重命名
  const renameGroup = (groupId: string, groupName: string) => {
    return new Promise((resolve, reject) => {
      renameElementGroup({ robotId: route.query?.projectId as string, groupId, groupName, elementType: 'common' }).then(() => {
        message.success('重命名成功')
        requestAllElements()
        resolve(true)
      }).catch((err) => {
        reject(err)
      })
    })
  }

  // 删除分组
  const deleteGroup = (groupId: string) => {
    const delElments = elements.value.find(i => i.id === groupId).elements
    delElementGroup({ robotId: route.query?.projectId as string, groupId }).then(() => {
      message.success('删除成功')
      requestAllElements()
      // 更新流程数据-删除该分组下的图像
      elementDeleteAndUpdateFlow({ elementIds: delElments.map(i => i.id) })
    })
  }
  // 移动分组
  const moveGroup = (originId: string, targetId: string) => {
    moveElement({ robotId: route.query?.projectId as string, elementId: originId, groupId: targetId }).then(() => {
      message.success('移动成功')
      requestAllElements()
    })
  }

  // 创建元素副本
  const elementCopy = (elementId: string) => {
    createElementCopy({ robotId: route.query?.projectId as string, elementId }).then(() => {
      message.success('复制成功')
      requestAllElements()
    })
  }

  const getElementById = (id: string) => {
    const allFlatElements = convertTreeToFlat(elements.value)
    return allFlatElements.find(item => item.id === id)
  }

  const reset = () => {
    elements.value = []
    resetSelectedElement()
    resetCurrentElement()
  }

  const elementsListener = () => {
    BUS.$on('get-elements', () => {
      console.log('on get-elements')
      requestAllElements()
    })
  }

  elementsListener()

  return {
    elements,
    currentElement,
    selectedElement,
    setElements,
    checkName,
    saveElement,
    deleteElement,
    convertTreeToFlat,
    getParentGroup,
    setTempElement,
    requestAllElements,
    requestElementDetail,
    setSelectedElement,
    reset,
    resetCurrentElement,
    renameElement,
    addGroup,
    renameGroup,
    deleteGroup,
    moveGroup,
    elementCopy,
    getElementById,
    addNewElement,
  }
})
