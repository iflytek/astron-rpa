import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

// 获取当前文件路径
const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const distPath = join(__dirname, '../dist')

const lightFile = join(distPath, 'variables.css')
const darkFile = join(distPath, 'variables.dark.css')

try {
  const lightVars = readFileSync(lightFile, 'utf8')
  const darkVars = readFileSync(darkFile, 'utf8')
  const combined = `${lightVars}\n\n/* Dark mode variables */\n${darkVars}`

  writeFileSync(lightFile, combined)
  console.log('CSS variables merged successfully!')
}
catch (err) {
  console.error('Error merging files:', err.message)
}
