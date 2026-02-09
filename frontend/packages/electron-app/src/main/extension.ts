import fs from 'node:fs'
import path from 'node:path'
import to from 'await-to-js'
import type { IPluginConfig } from '@rpa/shared'

import { extensionPath } from './path'

interface MainManifest {
  id: string
  name: string
  metaData: {
    buildInfo: { buildVersion: string }
    publicPath: string
  }
}

interface IExtension {
  name: string
  resourcePath: string
  config: IPluginConfig
}

export let extensions: IExtension[] = []

/**
 * 遍历 extensionPath 下的 package，读取 mf-manifest.json 中的内容
 */
export async function init() {
  const validExtensions: IExtension[] = []

  const promises = extensionPath.map(async (basePath) => {
    // 检查基础路径是否存在且为目录
    const [errStats, stats] = await to(fs.promises.stat(basePath))
    if (errStats || !stats.isDirectory()) {
      return
    }

    const [errItems, items] = await to(fs.promises.readdir(basePath))
    if (errItems) {
      console.error(`Error reading extension directory ${basePath}:`, errItems)
      return
    }

    const itemPromises = items.map(async (item) => {
      const itemPath = path.join(basePath, item)

      // 检查是否为目录
      const [errItemStats, itemStats] = await to(fs.promises.stat(itemPath))
      if (errItemStats || !itemStats.isDirectory()) return

      const manifestJsonPath = path.join(itemPath, 'mf-manifest.json')

      // 检查 mf-manifest.json 是否存在
      const [errManifestStats, manifestStats] = await to(fs.promises.stat(manifestJsonPath))
      if (errManifestStats || !manifestStats.isFile()) return

      const [errContent, content] = await to(fs.promises.readFile(manifestJsonPath, 'utf-8'))
      if (errContent) return

      try {
        const manifest: MainManifest = JSON.parse(content)
        const resourcePath = itemPath
        const entryUrl = manifest.metaData.publicPath + 'mf-manifest.json'

        validExtensions.push({
          name: manifest.name,
          resourcePath,
          config: {
            name: manifest.name,
            version: manifest.metaData.buildInfo.buildVersion,
            entry: entryUrl,
            enabled: true,
          }
        })
      } catch (err) {
        // JSON 解析失败
        console.error(`Error parsing manifest at ${manifestJsonPath}:`, err)
      }
    })

    await Promise.all(itemPromises)
  })

  await Promise.all(promises)

  extensions = validExtensions
}

init()

export const loadExtensions = () => extensions.map(it => it.config)

export const getExtensionResourcePath = (name: string) => {
  const extension = extensions.find(it => it.name === name)
  return extension?.resourcePath || ''
}
