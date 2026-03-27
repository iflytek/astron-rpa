#!/usr/bin/env node
import { mkdir, rm, writeFile, copyFile, readdir } from "node:fs/promises"
import { createHash } from "node:crypto"
import path from "node:path"
import { spawnSync } from "node:child_process"
import { fileURLToPath } from "node:url"

const repo = process.env.OPENCODE_SIDECAR_REPO ?? "anomalyco/opencode"
const releaseTag = process.env.OPENCODE_SIDECAR_TAG ?? "v1.2.27"
const scriptDir = path.dirname(fileURLToPath(import.meta.url))
const projectRoot = path.resolve(scriptDir, "..")
const destination = path.join(projectRoot, "resources", "opencode-cli.exe")
const manifestPath = path.join(projectRoot, "resources", "opencode-cli.json")
const workDir = path.join(projectRoot, "resources", ".opencode-sidecar-work")
const FETCH_TIMEOUT_MS = 60_000
const EXTRACTION_TIMEOUT_MS = 120_000

function psQuote(value) {
  return `'${String(value).replaceAll("'", "''")}'`
}

function log(message) {
  console.log(`[fetch-opencode-sidecar] ${message}`)
}

function normalizedTag(tag) {
  return String(tag).replace(/^v/i, "")
}

async function fetchJson(url, init = {}) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(new Error(`Timed out after ${FETCH_TIMEOUT_MS}ms`)), FETCH_TIMEOUT_MS)
  try {
    const response = await fetch(url, {
      ...init,
      signal: controller.signal,
    })
    return response
  } finally {
    clearTimeout(timeout)
  }
}

async function readReleaseMetadata() {
  const apiUrl = `https://api.github.com/repos/${repo}/releases/tags/${releaseTag}`
  log(`Reading release metadata from ${apiUrl}`)
  const authHeader = process.env.GITHUB_TOKEN ? { Authorization: `Bearer ${process.env.GITHUB_TOKEN}` } : {}
  const apiResponse = await fetchJson(apiUrl, {
    headers: {
      "User-Agent": "Codex",
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      ...authHeader,
    },
  })

  if (apiResponse.ok) {
    return await apiResponse.json()
  }

  const pageUrl = `https://github.com/${repo}/releases/tag/${releaseTag}`
  log(`API lookup failed with HTTP ${apiResponse.status}; falling back to ${pageUrl}`)
  const pageResponse = await fetchJson(pageUrl, {
    headers: {
      "User-Agent": "Codex",
      Accept: "text/html",
    },
  })

  if (!pageResponse.ok) {
    throw new Error(`Unable to read release metadata from GitHub (${apiResponse.status} / ${pageResponse.status})`)
  }

  const html = await pageResponse.text()
  const assetMatches = [...html.matchAll(/href="([^"]+\/releases\/download\/[^"]+?\/([^"/?#]+))"/g)]
  const assets = assetMatches.map(([, url, name]) => ({ name, browser_download_url: `https://github.com${url.replace(/&amp;/g, "&")}` }))
  return { tag_name: releaseTag, assets }
}

async function downloadAsset(asset, targetFile) {
  log(`Downloading ${asset.name}`)
  const response = await fetchJson(asset.browser_download_url, {
    redirect: "follow",
    headers: {
      "User-Agent": "Codex",
      Accept: "application/octet-stream",
    },
  })

  if (!response.ok) {
    throw new Error(`Download failed with HTTP ${response.status} ${response.statusText}`)
  }

  const bytes = Buffer.from(await response.arrayBuffer())
  await writeFile(targetFile, bytes)
  return bytes
}

function selectWindowsArchive(assets) {
  const matching = assets.filter((entry) => entry?.name && /windows.*x64.*\.zip$/i.test(entry.name))
  if (matching.length === 0) return null

  matching.sort((left, right) => {
    const leftExact = /^opencode-windows-x64\.zip$/i.test(left.name) ? 0 : 1
    const rightExact = /^opencode-windows-x64\.zip$/i.test(right.name) ? 0 : 1
    const leftBaseline = /baseline/i.test(left.name) ? 1 : 0
    const rightBaseline = /baseline/i.test(right.name) ? 1 : 0

    if (leftExact !== rightExact) return leftExact - rightExact
    if (leftBaseline !== rightBaseline) return leftBaseline - rightBaseline
    return left.name.localeCompare(right.name)
  })

  return matching[0]
}

async function findExecutable(rootDir) {
  const matches = []
  const queue = [rootDir]

  while (queue.length > 0) {
    const current = queue.shift()
    const entries = await readdir(current, { withFileTypes: true })

    for (const entry of entries) {
      const fullPath = path.join(current, entry.name)
      if (entry.isDirectory()) {
        queue.push(fullPath)
        continue
      }

      if (entry.isFile()) {
        const lower = entry.name.toLowerCase()
        if (lower === "opencode.exe" || lower === "opencode-cli.exe") {
          matches.push(fullPath)
        }
      }
    }
  }

  if (matches.length === 0) {
    throw new Error("Could not find opencode.exe inside the extracted archive")
  }

  matches.sort((left, right) => {
    const leftName = path.basename(left).toLowerCase()
    const rightName = path.basename(right).toLowerCase()
    const leftPriority = leftName === "opencode.exe" ? 0 : 1
    const rightPriority = rightName === "opencode.exe" ? 0 : 1
    if (leftPriority !== rightPriority) return leftPriority - rightPriority

    const leftDepth = path.relative(rootDir, left).split(path.sep).length
    const rightDepth = path.relative(rootDir, right).split(path.sep).length
    if (leftDepth !== rightDepth) return leftDepth - rightDepth

    return path.relative(rootDir, left).localeCompare(path.relative(rootDir, right))
  })

  return matches[0]
}

function sha256(buffer) {
  return createHash("sha256").update(buffer).digest("hex")
}

async function main() {
  if (process.platform !== "win32") {
    throw new Error("This fetch script is Windows-focused and expects PowerShell Expand-Archive.")
  }

  await mkdir(path.dirname(destination), { recursive: true })
  await rm(workDir, { recursive: true, force: true })
  await mkdir(workDir, { recursive: true })

  const archivePath = path.join(workDir, "opencode-sidecar.zip")
  const release = await readReleaseMetadata()
  const assets = Array.isArray(release.assets) ? release.assets : []
  const asset = selectWindowsArchive(assets)

  if (!asset) {
    const names = assets.map((entry) => entry?.name).filter(Boolean).join(", ")
    throw new Error(`Could not find a Windows x64 zip asset in release ${releaseTag}. Available assets: ${names || "(none)"}`)
  }

  const bytes = await downloadAsset(asset, archivePath)

  const extractDir = path.join(workDir, "extract")
  await mkdir(extractDir, { recursive: true })

  const expand = spawnSync(
    "powershell.exe",
    [
      "-NoProfile",
      "-ExecutionPolicy",
      "Bypass",
      "-Command",
      `Expand-Archive -LiteralPath ${psQuote(archivePath)} -DestinationPath ${psQuote(extractDir)} -Force`,
    ],
    { stdio: "inherit", timeout: EXTRACTION_TIMEOUT_MS },
  )

  if (expand.error?.code === "ETIMEDOUT") {
    throw new Error(`Expand-Archive timed out after ${EXTRACTION_TIMEOUT_MS}ms`)
  }
  if (expand.status !== 0) {
    throw new Error(`Expand-Archive failed with exit code ${expand.status ?? "unknown"}`)
  }

  const executablePath = await findExecutable(extractDir)
  const executableBytes = await import("node:fs/promises").then(({ readFile }) => readFile(executablePath))

  const manifest = {
    repository: repo,
    releaseTag,
    normalizedVersion: normalizedTag(releaseTag),
    assetName: asset.name,
    assetUrl: asset.browser_download_url,
    archiveSha256: sha256(bytes),
    executableName: path.basename(executablePath),
    executableSha256: sha256(executableBytes),
    createdAt: new Date().toISOString(),
  }

  await copyFile(executablePath, destination)
  await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`)
  log(`Wrote manifest ${manifestPath}`)
  log(`Copied ${executablePath} to ${destination}`)
  await rm(workDir, { recursive: true, force: true })
}

main().catch((error) => {
  console.error(`[fetch-opencode-sidecar] ${error.message}`)
  process.exitCode = 1
})
