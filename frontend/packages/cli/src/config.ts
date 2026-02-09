import { federation } from '@module-federation/vite'
import path from 'node:path'
import fs from 'node:fs'
import { loadConfigFromFile, ConfigEnv } from 'vite'

export type RpaConfig = Parameters<typeof federation>[0]

type UserConfigFnObject = (env: ConfigEnv) => RpaConfig;
type UserConfigFnPromise = (env: ConfigEnv) => Promise<RpaConfig>;
type UserConfigFn = (env: ConfigEnv) => RpaConfig | Promise<RpaConfig>;
type UserConfigExport = RpaConfig | Promise<RpaConfig> | UserConfigFnObject | UserConfigFnPromise | UserConfigFn;

export function defineConfig(config: RpaConfig): RpaConfig;
export function defineConfig(config: Promise<RpaConfig>): Promise<RpaConfig>;
export function defineConfig(config: UserConfigFnObject): UserConfigFnObject;
export function defineConfig(config: UserConfigFnPromise): UserConfigFnPromise;
export function defineConfig(config: UserConfigFn): UserConfigFn;
export function defineConfig(config: UserConfigExport): UserConfigExport {
  return config
}

export async function loadRpaConfig(root: string, command: 'build' | 'serve', mode: string): Promise<RpaConfig | null> {
  const configNames = [
    'rpa.config.ts',
    'rpa.config.js',
    'rpa.config.mjs',
    'rpa.config.cjs',
    'rpa.config.mts',
    'rpa.config.cts',
  ]

  let resolvedPath: string | undefined
  for (const name of configNames) {
    const p = path.resolve(root, name)
    if (fs.existsSync(p)) {
      resolvedPath = p
      break
    }
  }

  if (!resolvedPath)
    return null

  const result = await loadConfigFromFile(
    { command, mode },
    resolvedPath,
    root,
  )

  if (result && result.config) {
    return result.config as unknown as RpaConfig
  }

  return null
}
