<script setup lang="ts">
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'

import { checkComponentName, createComponent as createComponentApi, getDefaultComponentName } from '@/api/project'
import { ARRANGE } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import { newProjectModal } from '@/views/Home/components/modals'

import Banner from '../components/Banner.vue'
import TableContainer from '../components/TableContainer.vue'

const { t } = useTranslation()

// 重名校验
async function checkName(_rule, value: string) {
  const isExist = await checkComponentName({ name: value })
  if (isExist) {
    return Promise.reject(new Error(t('components.componentNameExists')))
  }
  return Promise.resolve()
}

function createComponent() {
  newProjectModal.show({
    title: t('components.newComponent'),
    name: t('components.componentName'),
    defaultName: () => getDefaultComponentName(),
    rules: [{ validator: checkName, trigger: 'blur' }],
    onConfirm: (name: string) => newProject(name),
  })

  const newProject = async (componentName: string) => {
    const res = await createComponentApi({ componentName })
    const projectId = res.data.robotId

    useRoutePush({ name: ARRANGE, query: { projectId, projectName: componentName, type: 'component' } })
    newProjectModal.hide()
    message.success(t('components.newComponentSuccess'))
  }
}
</script>

<template>
  <div class="h-full flex flex-col z-10 relative">
    <Banner
      :title="$t('designerManage.customComponents')"
      :sub-title="$t('designerManage.reusableModules')"
      :action-text="$t('components.newComponent')"
      @action="createComponent"
    />
    <TableContainer>
      <router-view />
    </TableContainer>
  </div>
</template>
