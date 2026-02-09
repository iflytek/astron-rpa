import path from 'node:path'
import cac from 'cac'
import debug from 'debug'
import { intro, text, outro, cancel, isCancel } from '@clack/prompts'

import { version } from '../../package.json'
import { globalLogger } from '../logger'
import { resolveComma, toArray, getBuiltinTemplateDir, renderTemplate, exists, ensureDir } from '../utils'
import { createBuildServer } from './vite'

const cli = cac('rpa')

cli.help().version(version)

cli.option('--debug [feat]', 'Show debug logs')

cli
  .command('dev', 'Start the development server')
  .action(async () => {
    await createBuildServer({ dev: true })
  })

cli
  .command('build', 'build the library for production')
  .option('-w, --watch', 'turn on watch mode, watch for changes and rebuild')
  .action(async () => {
    await createBuildServer({ dev: false })
  })

cli
  .command('create', 'create a plugin template')
  .option('-n, --name [name]', 'plugin name')
  .option('-t, --target [dir]', 'target directory to scaffold into')
  .action(async (options: { name?: string, target?: string }) => {
    try {
      intro('create-rpa-plugin')
      
      const cwd = process.cwd()
      const templateDir = getBuiltinTemplateDir()
      if (!templateDir) {
        cancel('builtin plugin template not found')
        return
      }
      
      let name = options.name
      if (!name) {
        const result = await text({
          message: 'Plugin name',
          initialValue: 'my-plugin',
          placeholder: 'my-plugin',
        })
        if (isCancel(result)) {
          cancel('Operation cancelled')
          return
        }
        name = result as string
      }
      
      let targetDir = options.target
      if (!targetDir) {
        const result = await text({
          message: 'Target directory',
          initialValue: path.resolve(cwd, `packages/${name}`),
          placeholder: path.resolve(cwd, `packages/${name}`),
        })
        if (isCancel(result)) {
          cancel('Operation cancelled')
          return
        }
        targetDir = result as string
      }

      const normalizedTarget = targetDir.replace(/\\+/g, '/')
      
      if (exists(normalizedTarget)) {
        cancel('target directory already exists')
        return
      }

      await ensureDir(normalizedTarget)
      await renderTemplate(templateDir, normalizedTarget, {
        name,
      })
      
      outro(`plugin template created at ${normalizedTarget}`)
    }
    catch (error) {
      globalLogger.error(error)
    }
  })

export async function runCli(): Promise<void> {
  cli.parse(process.argv, { run: false })

  if (cli.options.debug) {
    let namespace: string
    if (cli.options.debug === true) {
      namespace = 'rpa:*'
    }
    else {
      // support debugging multiple flags with comma-separated list
      namespace = resolveComma(toArray(cli.options.debug))
        .map(v => `rpa:${v}`)
        .join(',')
    }

    const enabled = debug.disable()
    if (enabled)
      namespace += `,${enabled}`

    debug.enable(namespace)
    debug('rpa:debug')('Debugging enabled', namespace)
  }

  try {
    await cli.runMatchedCommand()
  }
  catch (error) {
    globalLogger.error(error)
    process.exit(1)
  }
}
