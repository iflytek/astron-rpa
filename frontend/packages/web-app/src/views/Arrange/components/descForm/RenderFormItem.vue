<script setup lang="ts">
import { computed } from 'vue'

import { ATOM_FORM_TYPE } from '@/constants/atom'
import { PICK_TYPE_CV } from '@/views/Arrange/config/atom'

import { useEditFormType } from './hooks/useEditFormType'
import RenderFormTypeFile from './RenderFormTypeFile.vue'
import RenderFormTypePick from './RenderFormTypePick.vue'
import RenderFormTypeRemote from './RenderFormTypeRemote.vue'
import RenderFormTypeRemoteFiles from './RenderFormTypeRemoteFiles.vue'
import RenderFormTypeSelect from './RenderFormTypeSelect.vue'

const props = defineProps<{
  formItem: RPA.AtomDisplayItem
  desc: string
  id: string
  canEdit: boolean
}>()

const { editItem } = useEditFormType()

const SELECT_TYPES = new Set([
  ATOM_FORM_TYPE.RADIO,
  ATOM_FORM_TYPE.SELECT,
  ATOM_FORM_TYPE.SWITCH,
  ATOM_FORM_TYPE.CHECKBOX,
])

const PICK_TYPES = new Set([ATOM_FORM_TYPE.PICK, ATOM_FORM_TYPE.CVPICK])

// 编辑配置
const editList = computed(() => {
  const { type: formType, params } = props.formItem.formType
  let formTypeArr: string[] = []

  if (formType === ATOM_FORM_TYPE.RESULT) {
    formTypeArr = [ATOM_FORM_TYPE.VARIABLE]
  }
  else if (formType === ATOM_FORM_TYPE.PICK) {
    formTypeArr = params.use === PICK_TYPE_CV
      ? [ATOM_FORM_TYPE.CVPICK]
      : [ATOM_FORM_TYPE.PICK]
  }
  else {
    formTypeArr = formType.split('_')
  }

  return editItem.filter(item => formTypeArr.includes(item.type))
})

const hasEditList = computed(() => editList.value.length > 0)
</script>

<template>
  <span v-if="hasEditList">
    <span
      v-for="item in editList"
      :key="item.type"
      :item-type="item.type"
      :desc="desc"
    >
      <RenderFormTypeSelect
        v-if="SELECT_TYPES.has(item.type)"
        :id="id"
        :item-data="formItem"
        :can-edit="canEdit"
        :desc="desc"
        class="text-primary"
      />
      <RenderFormTypeRemote
        v-else-if="item.type === ATOM_FORM_TYPE.REMOTEPARAMS"
        :id="id"
        :item-data="formItem"
        :can-edit="canEdit"
        class="text-primary"
      />
      <RenderFormTypeRemoteFiles
        v-else-if="item.type === ATOM_FORM_TYPE.REMOTEFOLDERS"
        :id="id"
        :item-data="formItem"
        class="text-primary"
      />
      <RenderFormTypeFile
        v-else-if="item.type === ATOM_FORM_TYPE.FILE"
        :id="id"
        :item-type="item.type"
        :item-data="formItem"
        :can-edit="canEdit"
        :desc="desc"
        class="text-primary"
      />
      <RenderFormTypePick
        v-else-if="PICK_TYPES.has(item.type)"
        :id="id"
        :item-type="item.type"
        :can-edit="canEdit"
        :item-data="formItem"
        :desc="desc"
      />
    </span>
  </span>

  <a-tooltip v-else :title="desc">
    <span class="mx-1 px-1 whitespace-nowrap bg-[#726FFF]/[.1] rounded text-primary">{{ desc }}</span>
  </a-tooltip>
</template>
