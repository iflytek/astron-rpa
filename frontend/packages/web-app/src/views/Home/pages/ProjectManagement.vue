<script setup lang="ts">
import { message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'

import { createProject, getDefaultName } from '@/api/project'
import { ARRANGE } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import { newProjectModal } from '@/views/Home/components/modals'

import Banner from '../components/Banner.vue'
import TableContainer from '../components/TableContainer.vue'

const { t } = useTranslation()

function createRobot() {
  newProjectModal.show({
    title: t('newProject'),
    name: t('projectName'),
    defaultName: getDefaultName,
    onConfirm: (name: string) => newProject(name),
  })

  const newProject = async (projectName: string) => {
    const res = await createProject({ name: projectName })
    const projectId = res.data.robotId

    useRoutePush({ name: ARRANGE, query: { projectId, projectName } })
    newProjectModal.hide()
    message.success('新建成功')
  }
}
</script>

<template>
  <div class="h-full flex flex-col z-10 relative">
    <Banner
      :title="$t('designerManage.oneClickAutomation')"
      :sub-title="$t('designerManage.freeFromRepetition')"
      :action-text="$t('designerManage.createRobot')"
      @action="createRobot"
    />
    <TableContainer>
      <router-view />
    </TableContainer>
  </div>
</template>
