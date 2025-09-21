<script setup lang="ts">
import { ATOM_FORM_TYPE } from '@/constants/atom'
import { PICK_TYPE_CV } from '@/views/Arrange/config/atom'

import { useEditFormType } from './hooks/useEditFormType'
import RenderFormTypeFile from './RenderFormTypeFile.vue'
import RenderFormTypePick from './RenderFormTypePick.vue'
import RenderFormTypeRemote from './RenderFormTypeRemote.vue'
import RenderFormTypeRemoteFiles from './RenderFormTypeRemoteFiles.vue'
import RenderFormTypeSelect from './RenderFormTypeSelect.vue'

const { formItem, desc, id, canEdit } = defineProps<{
  formItem: RPA.AtomDisplayItem
  desc: string
  id: string
  canEdit: boolean
}>()

const { editItem } = useEditFormType()

// 编辑配置
function renderEdit() {
  const formType = formItem.formType.type
  let formTypeArr: string[] = []
  if (Object.is(formType, ATOM_FORM_TYPE.RESULT)) {
    formTypeArr = [ATOM_FORM_TYPE.VARIABLE]
  }
  else if (Object.is(formType, ATOM_FORM_TYPE.PICK)) {
    switch (formItem.formType.params.use) {
      case PICK_TYPE_CV:
        formTypeArr = [ATOM_FORM_TYPE.CVPICK]
        break
      default:
        formTypeArr = [ATOM_FORM_TYPE.PICK]
        break
    }
  }
  else {
    formTypeArr = formType.split('_')
  }

  return editItem.filter(item => formTypeArr.includes(item.type))
}
</script>

<template>
  <span v-if="renderEdit().length !== 0">
    <span
      v-for="item in renderEdit()"
      :key="item.type"
      :item-type="item.type"
      :desc="desc"
    >
      <RenderFormTypeSelect
        v-if="[ATOM_FORM_TYPE.RADIO, ATOM_FORM_TYPE.SELECT, ATOM_FORM_TYPE.SWITCH, ATOM_FORM_TYPE.CHECKBOX].includes(item.type)"
        :id="id"
        :item-data="formItem"
        :can-edit="canEdit"
        :desc="desc"
        class="text-primary"
      />
      <RenderFormTypeRemote
        v-if="[ATOM_FORM_TYPE.REMOTEPARAMS].includes(item.type)"
        :id="id"
        :item-data="formItem"
        :can-edit="canEdit"
        class="text-primary"
      />
      <RenderFormTypeRemoteFiles
        v-if="[ATOM_FORM_TYPE.REMOTEFOLDERS].includes(item.type)"
        :id="id"
        :item-data="formItem"
        class="text-primary"
      />
      <RenderFormTypeFile
        v-if="item.type === ATOM_FORM_TYPE.FILE"
        :id="id"
        :item-type="item.type"
        :item-data="formItem"
        :can-edit="canEdit"
        :desc="desc"
        class="text-primary"
      />
      <RenderFormTypePick
        v-if="[ATOM_FORM_TYPE.PICK, ATOM_FORM_TYPE.CVPICK].includes(item.type)"
        :id="id"
        :item-type="item.type"
        :can-edit="canEdit"
        :item-data="formItem"
        :desc="desc"
      />
    </span>
  </span>

  <a-tooltip v-if="renderEdit().length === 0" :title="desc">
    <span class="mx-1 px-1 whitespace-nowrap bg-[#726FFF]/[.1] rounded text-primary">{{ desc }}</span>
  </a-tooltip>
</template>
