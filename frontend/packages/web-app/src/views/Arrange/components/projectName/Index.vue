<script lang="ts" setup>
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { nextTick, reactive, ref } from 'vue'

import { checkComponentName, rename, renameCheck, renameComponent } from '@/api/project'
import { useProcessStore } from '@/stores/useProcessStore'

interface FormState {
  robotId: string | number
  newName: string
}

const processStore = useProcessStore()
const { t } = useTranslation()
const inputRef = ref()
const isEdit = ref(false)
const formState = reactive<FormState>({
  robotId: processStore.project.id,
  newName: processStore.project.name,
})

function toggleEdit(value?: boolean) {
  isEdit.value = value ?? !isEdit.value
  nextTick(() => {
    inputRef.value?.focus()
  })
}

async function editProjectName() {
  try {
    if (processStore.isComponent) {
      await checkComponentName({
        name: formState.newName,
        componentId: formState.robotId as string,
      })

      await renameComponent({
        newName: formState.newName,
        componentId: formState.robotId as string,
      })
    }
    else {
      await renameCheck(formState)
      await rename(formState)
    }

    message.success(t('common.renameSuccess'))
    processStore.setProject({ ...processStore.project, name: formState.newName })
    setTimeout(() => toggleEdit(false), 100) // blur事件会先于click触发导致状态错乱，延迟修改以确保状态正常更新
  }
  catch (e) {
    console.log(e)
  }
}
</script>

<template>
  <div data-tauri-drag-region class="project-name">
    <slot name="prefix" />
    <rpa-hint-icon name="robot" size="20" class="mx-2 bg-primary rounded-sm text-white" />
    <a-input
      v-if="isEdit"
      ref="inputRef"
      v-model:value="formState.newName"
      size="small"
      @press-enter="toggleEdit(false)"
      @blur="editProjectName"
    />
    <a-tooltip v-else :title="processStore.project.name">
      <span class="project-name-text">{{ processStore.project.name }}</span>
    </a-tooltip>
    <rpa-hint-icon name="projedit" :title="$t('rename')" class="ml-2" enable-hover-bg @click="!isEdit && toggleEdit(true)" />
  </div>
</template>

<style lang="scss" scoped>
.project-name {
  display: flex;
  align-items: center;
  position: relative;
  padding-left: 14px;
  width: 192px;

  .project-name-text {
    font-size: 14px;
    font-weight: 500;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
  }
}
</style>
