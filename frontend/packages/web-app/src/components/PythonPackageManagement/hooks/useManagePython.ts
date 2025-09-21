import { nextTick } from 'vue'

import { getRootBaseURL } from '@/api/http/env'
import { addPyPackageApi, deletePyPackageApi, packageVersion, updatePyPackageApi } from '@/api/resource'
import { sseRequest } from '@/api/sse'
import { useProcessStore } from '@/stores/useProcessStore'
import { usePythonPackageStore } from '@/stores/usePythonPackageStore'

import { pythonInstallModal } from '../modals'

export function useManagePython() {
  const pythonPackageStore = usePythonPackageStore()
  const processStore = useProcessStore()
  let controller = null

  // 安装依赖包
  function installPackage(pacakgeOption, upgrade = false) {
    const params = { robotId: processStore.project.id, ...pacakgeOption }
    controller = new AbortController()
    pythonPackageStore.setPyLoadingType(upgrade ? 'upgrading' : 'installing')
    sseRequest(`${getRootBaseURL()}/scheduler/pip/install`, {
      project_id: processStore.project.id,
      package: pacakgeOption.packageName,
      version: pacakgeOption.packageVersion,
      mirror: pacakgeOption.mirror,
    }, { single: controller.single }, (res) => {
      if (!res)
        return
      let newData
      try {
        newData = JSON.parse(res.data).stdout
      }
      // eslint-disable-next-line unused-imports/no-unused-vars
      catch (e) {
        newData = res.data
      }

      if (newData.includes('stderr')) {
        pythonPackageStore.setPyLoadingType(upgrade ? 'upgradeFail' : 'installFail')
        controller.abort()
        controller = null
        return
      }
      if (newData.includes('[DONE]')) {
        pythonPackageStore.setPyLoadingType(upgrade ? 'upgradeSuccess' : 'installSuccess')
        pythonInstallModal.hide()
        upgrade ? updatePackage(params) : addPackage(params)
        controller.abort()
        controller = null
        return
      }
      if (newData) {
        pacakgeOption.output += newData
        handleScrollToBottom()
      }
    }, () => {
      pythonPackageStore.setPyLoadingType(upgrade ? 'upgradeFail' : 'installFail')
    })
  }

  function handleScrollToBottom() {
    nextTick(() => {
      const dom = document.querySelector('#form_item_output')
      if (dom) {
        dom.scrollTop = dom.scrollHeight
      }
    })
  }
  // 升级依赖包
  function upgradePackage() {
    const packages = pythonPackageStore.getSelectedPackages()
    packages.forEach((item) => {
      installPackage({ ...item, packageVersion: '', projectId: useProcessStore().project.id }, true)
    })
  }

  // 卸载依赖包
  function uninstallPackage() {
    // 卸载完成后，调用http删除依赖包
    pythonPackageStore.setPyLoadingType('uninstalling')
    delPackage()
  }

  // 获取包版本号, 并调用http接口新增或更新依赖包数据
  function getPackageVersion(packageParams, apiFn = addPyPackageApi) {
    packageVersion(packageParams).then((res) => {
      apiFn({ ...packageParams, packageVersion: res.data.version }).then(() => {
        pythonPackageStore.updatePythonList()
      })
    }).catch(() => {
    })
  }

  // 调用http新增依赖包
  function addPackage(packageParams) {
    getPackageVersion(packageParams, addPyPackageApi)
  }

  // 调用http更新依赖包
  function updatePackage(packageParams) {
    getPackageVersion(packageParams, updatePyPackageApi)
  }

  // 调用http删除依赖包
  function delPackage() {
    const packages = pythonPackageStore.getSelectedPackages()
    deletePyPackageApi({
      robotId: useProcessStore().project.id,
      idList: packages.map(i => i.id),
    }).then(() => {
      pythonPackageStore.setPyLoadingType('uninstallSuccess')
      pythonPackageStore.updatePythonList()
    }).catch(() => {
      pythonPackageStore.setPyLoadingType('uninstallFail')
    })
  }

  // 更新弹窗提示
  const upgradeModal = (ids) => {
    ids && pythonPackageStore.setSelectedPackageIds(ids)
    pythonPackageStore.setPyLoadingType('upgradePythonTip')
  }

  // 卸载弹窗提示
  const uninstallModal = (ids) => {
    ids && pythonPackageStore.setSelectedPackageIds(ids)
    pythonPackageStore.setPyLoadingType('uninstallTip')
  }

  return {
    installPackage,
    upgradePackage,
    uninstallPackage,
    upgradeModal,
    uninstallModal,
  }
}
