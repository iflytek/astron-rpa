import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import ejs from 'ejs'

export function resolveComma<T extends string>(arr: T[]): T[] {
  return arr.flatMap(format => format.split(',') as T[])
}

export function toArray<T>(
  val: T | T[] | null | undefined,
  defaultValue?: T,
): T[] {
  if (Array.isArray(val)) {
    return val
  }
  else if (val == null) {
    if (defaultValue)
      return [defaultValue]
    return []
  }
  else {
    return [val]
  }
}

export function exists(p: string): boolean {
  try {
    fs.accessSync(p)
    return true
  }
  catch {
    return false
  }
}

export async function ensureDir(dir: string): Promise<void> {
  await fs.promises.mkdir(dir, { recursive: true })
}

export async function renderTemplate(src: string, dest: string, data: Record<string, string>): Promise<void> {
  await ensureDir(dest)
  const entries = await fs.promises.readdir(src, { withFileTypes: true })
  for (const entry of entries) {
    const name = entry.name
    if (name === 'node_modules' || name === 'dist')
      continue
    
    // Process filename replacement using ejs-style placeholders if needed, 
    // or keep simple replacement for filenames as ejs is mostly for content.
    // Here we use simple replacement for filenames to avoid complexity with filesystem paths.
    let destName = name
    for (const [key, value] of Object.entries(data)) {
      destName = destName.replaceAll(`{{${key}}}`, value)
    }

    const srcPath = path.join(src, name)
    const destPath = path.join(dest, destName)
    
    if (entry.isDirectory()) {
      await renderTemplate(srcPath, destPath, data)
    }
    else {
      // For binary files, copy directly
      if (/\.(png|jpg|jpeg|gif|svg|ico|webp)$/i.test(name)) {
        const content = await fs.promises.readFile(srcPath)
        await fs.promises.writeFile(destPath, content)
      } else {
        // For text files, use ejs to render
        const content = await fs.promises.readFile(srcPath, 'utf-8')
        try {
           const rendered = ejs.render(content, data)
           await fs.promises.writeFile(destPath, rendered, 'utf-8')
        } catch (e) {
           // Fallback or rethrow? If it's not a valid ejs template (e.g. conflict), 
           // we might want to just copy it or warn. 
           // For now, let's assume all text files in template are valid ejs or plain text.
           // EJS is generally safe with plain text unless it contains <% 
           console.warn(`Failed to render ${srcPath}, falling back to plain copy:`, e)
           await fs.promises.writeFile(destPath, content, 'utf-8')
        }
      }
    }
  }
}

export function getBuiltinTemplateDir(): string {
  const dirname = path.dirname(fileURLToPath(import.meta.url))
  return path.resolve(dirname, '../templates/template-vue')
}
