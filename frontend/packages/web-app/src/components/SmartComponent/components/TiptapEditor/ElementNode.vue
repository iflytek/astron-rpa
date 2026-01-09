<script setup lang="ts">
import { nodeViewProps, NodeViewWrapper } from '@tiptap/vue-3'
import { message } from 'ant-design-vue'
import { throttle } from 'lodash-es'
import { computed } from 'vue'

import { getRootBaseURL } from '@/api/http/env'
import { getLatestCurrentElementData } from '@/components/SmartComponent/utils/pick'
import { useElementsStore } from '@/stores/useElementsStore'
import { useSmartCompPickStore } from '@/stores/useSmartCompPickStore'
import type { ElementsType } from '@/types/resource'

const props = defineProps(nodeViewProps)
const { updateAttributes } = props

// const usePick = usePickStore()
const usePick = useSmartCompPickStore()
const useElements = useElementsStore()

const isValidElement = computed(() => !!props.node.attrs.elementId || !!props.node.attrs.xpath)

function handlePick() {
  // usePick.startPick('WebPick', '', (res) => {
  //   if (!res.success)
  //     return

  //   const data = res.data
  //   // 更新节点属性
  //   updateAttributes({
  //     name: `${data.path.tag}_${data.path.text}`,
  //     imageUrl: data.imageUrl || '',
  //     xpath: data.xpath || '',
  //     outerHtml: data.outerHtml || '',
  //     elementId: data.elementId || '',
  //   })
  // })

  usePick.startPick(async (res) => {
    if (!res.success)
      return

    await useElements.setTempElement(res.data)

    const rawElementData = useElements.currentElement.elementData
    const parsedElementData = JSON.parse(rawElementData)
    const elementData = getLatestCurrentElementData(useElements.currentElement, true)
    const savedElement = await useElements.saveElement(elementData, useElements.currentElement.name)

    // 更新节点属性
    updateAttributes({
      name: savedElement.name,
      imageUrl: `api/resource/file/download?fileId=${savedElement.imageId}`,
      elementId: savedElement.id,
      xpath: parsedElementData.path?.xpath || '',
      outerHtml: parsedElementData.path?.outerHTML || '',
    })
  })
}

function handleRepick() {
  usePick.startPick(async (res) => {
    if (!res.success)
      return

    // 必须先 requestElementDetail 设置 currentElement 否则 setTempElement不生效
    await useElements.requestElementDetail({ id: props.node.attrs.elementId } as ElementsType)
    const groupName = useElementsStore().elements.find(item => item.elements.some(i => i.id === props.node.attrs.elementId)).name
    await useElements.setTempElement(res.data, 'repick', groupName)

    const rawElementData = useElements.currentElement.elementData
    const parsedElementData = JSON.parse(rawElementData)
    const elementData = getLatestCurrentElementData(useElements.currentElement, true)
    const savedElement = await useElements.saveElement(elementData, useElements.currentElement.name)

    // 更新节点属性
    updateAttributes({
      name: savedElement.name,
      imageUrl: `api/resource/file/download?fileId=${savedElement.imageId}`,
      elementId: savedElement.id,
      xpath: parsedElementData.path?.xpath || '',
      outerHtml: parsedElementData.path?.outerHTML || '',
    })
  })
}

const handleCheck = throttle(
  async () => {
    await useElements.requestElementDetail({ id: props.node.attrs.elementId } as ElementsType)
    const elementData = getLatestCurrentElementData(useElements.currentElement, false)
    const element = JSON.stringify(elementData)
    usePick.startCheck(element, (res) => {
      if (res.success)
        message.success('校验成功')
    })
  },
  1500,
  { leading: true, trailing: false },
)

function getImageUrl() {
  return `${getRootBaseURL()}/${props.node.attrs.imageUrl}`
}
</script>

<template>
  <NodeViewWrapper
    class="inline-flex items-center mx-1 px-1 py-[2px] bg-[#D7D7FF]/[.4] dark:bg-[#5D59FF]/[.35] text-[#5D59FF]/[.35] dark:text-[#8482FE]/[.9] border rounded-lg cursor-pointer"
    :class="{ 'border-transparent': !selected }"
    :contenteditable="false"
  >
    <a-popover>
      <template #content>
        <div class="flex flex-col gap-2">
          <div class="border border-[#000000]/[.1] dark:border-[#FFFFFF]/[.16] rounded-none">
            <a-image v-if="isValidElement" :src="getImageUrl()" class="!w-[192px] !h-[108px] object-contain" fallback="data:image/png;base64,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" />
            <div v-else class="w-[192px] h-[108px] flex flex-col justify-center items-center gap-2">
              <span class="text-[12px] text-text-tertiary">暂无元素</span>
              <a-button :loading="usePick.isPicking" @click="handlePick">
                拾取元素
              </a-button>
            </div>
          </div>
          <div v-if="isValidElement" class="flex justify-evenly items-center">
            <rpa-hint-icon
              name="bottom-pick-menu-repick"
              enable-hover-bg
              @click="handleRepick"
            >
              <template #suffix>
                <span class="ml-1">重新拾取</span>
              </template>
            </rpa-hint-icon>
            <a-divider type="vertical" class="h-4 border-s-[#000000]/[.16] dark:border-s-[#FFFFFF]/[.16]" />
            <rpa-hint-icon
              name="get-element-object-web"
              enable-hover-bg
              @click="handleCheck"
            >
              <template #suffix>
                <span class="ml-1">校验元素</span>
              </template>
            </rpa-hint-icon>
          </div>
        </div>
      </template>
      <span>[{{ node.attrs.name }}]</span>
    </a-popover>
  </NodeViewWrapper>
</template>
