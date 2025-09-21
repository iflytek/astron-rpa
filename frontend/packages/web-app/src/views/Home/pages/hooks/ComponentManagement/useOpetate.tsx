import { Icon, NiceModal } from '@rpa/components'
import { App, message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { h } from 'vue'

import { checkComponentName, createCopyComponent, createCopyComponentName, deleteComponent, renameComponent } from '@/api/project'
import { ComponentPublishDetail, ComponentPublishModal } from '@/components/ComponentPublish'
import { ARRANGE } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'
import type { AnyObj } from '@/types/common'
import { newProjectModal } from '@/views/Home/components/modals'

export function useOperate(refreshTable: () => void) {
  const { t } = useTranslation()
  const { modal } = App.useApp()

  const handlePublish = (record: AnyObj) => {
    NiceModal.show(ComponentPublishModal, { componentId: record.componentId, onRefresh: refreshTable })
  }

  const handleDetail = (record: AnyObj) => {
    NiceModal.show(ComponentPublishDetail, { componentId: record.componentId })
  }

  const handleEdit = (record: AnyObj) => {
    console.log(record)
    useRoutePush({ name: ARRANGE, query: { projectId: record.componentId, projectName: record.name, type: 'component' } })
  }

  const handleRename = (record: AnyObj) => {
    const componentId = record.componentId

    // 重名校验
    async function checkName(_rule, value: string) {
      const isExist = await checkComponentName({ name: value, componentId })
      if (isExist) {
        return Promise.reject(new Error(t('components.componentNameExists')))
      }
      return Promise.resolve()
    }

    newProjectModal.show({
      title: t('rename'),
      name: t('components.componentName'),
      defaultName: record.name,
      rules: [{ validator: checkName, trigger: 'blur' }],
      onConfirm: (name: string) => handleConfirm(name),
    })

    async function handleConfirm(name: string) {
      await renameComponent({ componentId, newName: name })
      refreshTable()
      newProjectModal.hide()
      message.success(t('common.renameSuccess'))
    }
  }

  const handleDelete = (record: AnyObj) => {
    const onOk = async () => {
      await deleteComponent({ componentId: record.componentId })
      refreshTable()
      message.success(t('common.deleteSuccess'))
    }

    modal.confirm({
      title: t('delete'),
      content: '组件删除后不可恢复，确认删除么？',
      onOk,
    })
  }

  const handleCopy = async (record: AnyObj) => {
    const componentId = record.componentId

    // 重名校验
    async function checkName(_rule, value: string) {
      const isExist = await checkComponentName({ name: value, componentId })
      if (isExist) {
        return Promise.reject(new Error(t('components.componentNameExists')))
      }
      return Promise.resolve()
    }

    newProjectModal.show({
      title: t('components.newCopy'),
      name: t('components.componentName'),
      defaultName: () => createCopyComponentName({ componentId }),
      rules: [{ validator: checkName, trigger: 'blur' }],
      onConfirm: (name: string) => newComponent(name),
    })

    async function newComponent(name: string) {
      await createCopyComponent({ componentId, name })
      refreshTable()
      newProjectModal.hide()
      message.success(t('createCopySuccess'))
    }
  }

  const baseOpts = [
    {
      key: 'edit',
      text: 'edit',
      clickFn: handleEdit,
      icon: h(<Icon name="projedit" size="16px" />),
    },
  ]

  const moreOpts = [
    {
      key: 'detail',
      text: 'components.componentDetail',
      icon: h(<Icon name="bottom-menu-component-attribute-manage" size="16px" />),
      clickFn: handleDetail,
    },
    {
      key: 'createCopy',
      text: 'createCopy',
      icon: h(<Icon name="create-copy" size="16px" />),
      clickFn: handleCopy,
    },
    {
      key: 'release',
      text: 'release',
      icon: h(<Icon name="tools-publish" size="16px" />),
      clickFn: handlePublish,
    },
    // {
    //   key: 'share',
    //   text: 'common.share',
    //   icon: h(<Icon name="share" size="16px" />),
    //   clickFn: () => {},
    // },
    {
      key: 'del',
      text: 'delete',
      icon: h(<Icon name="market-del" size="16px" />),
      clickFn: handleDelete,
    },
  ]

  return { baseOpts, moreOpts, handleEdit, handleRename }
}
