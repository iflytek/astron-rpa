import { computed, inject, provide, ref } from 'vue'

import { getBaseURL } from '@/api/http/env'
import { addPyPackageApi, getPyPackageListApi, packageVersion } from '@/api/resource'
import { sseRequest } from '@/api/sse'
import { mirrorList } from '@/components/PythonPackageManagement/config'
import { useProcessStore } from '@/stores/useProcessStore'
import { usePythonPackageStore } from '@/stores/usePythonPackageStore'

// 创建依赖检查上下文
export function usePackageCheckContext() {
  const processStore = useProcessStore()
  const pythonPackageStore = usePythonPackageStore()

  const packages = ref<string[]>([])
  const lackPackages = ref<string[]>([])
  const initialLackPackages = ref<string[]>([])
  const isInstalling = ref(false)
  const isChecking = ref(false)

  async function checkLackPackages() {
    if (!packages.value || packages.value.length === 0) {
      lackPackages.value = []
      initialLackPackages.value = []
      return
    }

    isChecking.value = true
    try {
      const res = await getPyPackageListApi({ robotId: processStore.project.id })
      const installedPackageNames = (res.data || []).map((pkg: any) =>
        pkg.packageName?.toLowerCase(),
      )

      const lack = packages.value.filter((pkg) => {
        const pkgLower = pkg.toLowerCase()
        return !installedPackageNames.includes(pkgLower)
      })
      lackPackages.value = lack

      // 如果是首次检查或 packages 变化，保存初始缺失的依赖列表
      if (initialLackPackages.value.length === 0 && lack.length > 0) {
        initialLackPackages.value = [...lack]
      }
    }
    catch (error) {
      console.error('检查依赖失败:', error)
    }
    finally {
      isChecking.value = false
    }
  }

  function installPackageAsync(packageName: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const controller = sseRequest.post(
        `${getBaseURL()}/scheduler/pip/install`,
        {
          project_id: processStore.project.id,
          package: packageName,
          version: '',
          mirror: mirrorList[0].value,
        },
        (res) => {
          if (!res)
            return

          let newData
          try {
            newData = JSON.parse(res.data).stdout
          }
          catch (e) {
            newData = res.data
            console.log(e)
          }

          if (newData.includes('stderr')) {
            controller.abort()
            reject(new Error(`安装 ${packageName} 失败`))
            return
          }

          if (newData.includes('[DONE]')) {
            controller.abort()
            const params = {
              robotId: processStore.project.id,
              packageName,
              packageVersion: '',
              mirror: '',
            }
            packageVersion({ robotId: processStore.project.id, packageName })
              .then((res) => {
                addPyPackageApi({ ...params, packageVersion: res.data.version })
                  .then(() => {
                    pythonPackageStore.updatePythonList()
                    resolve()
                  })
                  .catch(() => resolve())
              })
              .catch(() => resolve())
          }
        },
        (err) => {
          controller.abort()
          reject(err)
        },
      )
    })
  }

  async function installAllPackages() {
    if (lackPackages.value.length === 0 || isInstalling.value) {
      return
    }

    isInstalling.value = true
    const installResults: { success: string[], failed: string[] } = {
      success: [],
      failed: [],
    }

    try {
      for (const pkgName of lackPackages.value) {
        try {
          await installPackageAsync(pkgName)
          installResults.success.push(pkgName)
        }
        catch (error) {
          console.error(`安装 ${pkgName} 失败:`, error)
          installResults.failed.push(pkgName)
        }
      }

      // 安装完成后不重新检查，保持显示初始的缺失依赖列表
      // 但更新实际缺失的包列表（移除已成功安装的）
      lackPackages.value = lackPackages.value.filter(pkg =>
        !installResults.success.includes(pkg),
      )
    }
    catch (error) {
      console.error('安装依赖失败:', error)
    }
    finally {
      isInstalling.value = false
    }
  }

  async function setPackages(pkgs: string[]) {
    packages.value = pkgs
    initialLackPackages.value = []
    await checkLackPackages()
  }

  function reset() {
    packages.value = []
    lackPackages.value = []
    initialLackPackages.value = []
    isInstalling.value = false
    isChecking.value = false
  }

  const hasLackPackages = computed(() => lackPackages.value.length > 0)
  const hasInitialLackPackages = computed(() => initialLackPackages.value.length > 0)
  const isInstallCompleted = computed(() => initialLackPackages.value.length > 0 && lackPackages.value.length === 0)

  return {
    packages,
    lackPackages,
    initialLackPackages,
    isInstalling,
    isChecking,
    hasLackPackages,
    hasInitialLackPackages,
    isInstallCompleted,

    setPackages,
    checkLackPackages,
    installAllPackages,
    reset,
  }
}

export type PackageCheckContext = ReturnType<typeof usePackageCheckContext>

export function providePackageCheckContext(context: PackageCheckContext) {
  provide('packageCheck', context)
}

// 依赖检查注入
export function usePackageCheck() {
  const context = inject<PackageCheckContext>('packageCheck')
  if (!context) {
    throw new Error('usePackageCheck must be used within SmartComponent Index component')
  }
  return context
}
