#!/usr/bin/env node
// Regenerate docs/star-history.svg from this repository's real stargazer history.
//
// Usage:
//   GH_TOKEN=<token> node .github/scripts/gen-star-history.mjs [--repo owner/name] [--color '#2f7ed8'] [--out docs/star-history.svg]
//
// The repo defaults to $GITHUB_REPOSITORY (set by GitHub Actions). The token
// defaults to $GH_TOKEN or $GITHUB_TOKEN. Because GitHub restricted the
// stargazer-timestamp API to a repository's admins/collaborators (2026-06-30),
// the token must be able to read this repo's stars. The script FAILS (exit 1)
// without overwriting the existing SVG if it cannot read real dated stars, so a
// permission problem never silently commits a broken chart.

import { writeFileSync } from 'node:fs';

const args = process.argv.slice(2);
function arg(name, def) {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : def;
}

const REPO = arg('--repo', process.env.GITHUB_REPOSITORY);
const COLOR = arg('--color', '#2f7ed8');
const OUT = arg('--out', 'docs/star-history.svg');
const TOKEN = process.env.GH_TOKEN || process.env.GITHUB_TOKEN;

if (!REPO) { console.error('No repo: pass --repo owner/name or set GITHUB_REPOSITORY'); process.exit(1); }
if (!TOKEN) { console.error('No token: set GH_TOKEN or GITHUB_TOKEN'); process.exit(1); }

const API = 'https://api.github.com';
const HEADERS = {
  'User-Agent': 'star-history-selfhost',
  Authorization: 'Bearer ' + TOKEN,
  Accept: 'application/vnd.github.star+json',
  'X-GitHub-Api-Version': '2022-11-28',
};

async function getJson(path, tries = 6) {
  let lastErr;
  for (let i = 0; i < tries; i++) {
    try {
      const res = await fetch(API + path, { headers: HEADERS });
      if (res.ok) return res.json();
      lastErr = new Error(res.status + ' ' + (await res.text()).slice(0, 160));
    } catch (e) { lastErr = e; }
    await new Promise(r => setTimeout(r, 800 * (i + 1)));
  }
  throw lastErr;
}

function niceMax(v) { const p = 10 ** Math.floor(Math.log10(v)); const n = v / p; return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10) * p; }
function fmtDate(t) { const d = new Date(t); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0'); }

function renderSVG(pts, total, repo, color) {
  const W = 840, H = 500, m = { top: 60, right: 150, bottom: 60, left: 74 };
  const plotW = W - m.left - m.right, plotH = H - m.top - m.bottom;
  let tMin = Infinity, tMax = -Infinity, yMax = 0;
  for (const [t, y] of pts) { if (t < tMin) tMin = t; if (t > tMax) tMax = t; if (y > yMax) yMax = y; }
  const yTop = niceMax(yMax);
  const xOf = t => m.left + ((t - tMin) / (tMax - tMin)) * plotW;
  const yOf = y => m.top + plotH - (y / yTop) * plotH;
  const P = [];
  P.push(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif">`);
  P.push(`<rect width="${W}" height="${H}" fill="#ffffff"/>`);
  P.push(`<text x="${W / 2}" y="34" text-anchor="middle" font-size="20" font-weight="600" fill="#24292f">Star History — ${repo}</text>`);
  for (let i = 0; i <= 5; i++) { const val = yTop * i / 5, y = yOf(val); P.push(`<line x1="${m.left}" y1="${y.toFixed(1)}" x2="${m.left + plotW}" y2="${y.toFixed(1)}" stroke="#eaeef2"/>`); P.push(`<text x="${m.left - 10}" y="${(y + 4).toFixed(1)}" text-anchor="end" font-size="12" fill="#57606a">${Math.round(val).toLocaleString()}</text>`); }
  for (let i = 0; i <= 6; i++) { const t = tMin + (tMax - tMin) * i / 6, x = xOf(t); P.push(`<line x1="${x.toFixed(1)}" y1="${m.top + plotH}" x2="${x.toFixed(1)}" y2="${(m.top + plotH + 5).toFixed(1)}" stroke="#8c959f"/>`); P.push(`<text x="${x.toFixed(1)}" y="${m.top + plotH + 22}" text-anchor="middle" font-size="12" fill="#57606a">${fmtDate(t)}</text>`); }
  P.push(`<line x1="${m.left}" y1="${m.top}" x2="${m.left}" y2="${m.top + plotH}" stroke="#d0d7de" stroke-width="1.5"/>`);
  P.push(`<line x1="${m.left}" y1="${m.top + plotH}" x2="${m.left + plotW}" y2="${m.top + plotH}" stroke="#d0d7de" stroke-width="1.5"/>`);
  P.push(`<text transform="translate(22,${m.top + plotH / 2}) rotate(-90)" text-anchor="middle" font-size="13" fill="#57606a">GitHub Stars</text>`);
  const d = pts.map(([t, y], i) => `${i ? 'L' : 'M'}${xOf(t).toFixed(1)},${yOf(y).toFixed(1)}`).join(' ');
  P.push(`<path d="${d}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>`);
  const last = pts[pts.length - 1];
  P.push(`<circle cx="${xOf(last[0]).toFixed(1)}" cy="${yOf(last[1]).toFixed(1)}" r="4" fill="${color}"/>`);
  P.push(`<rect x="${m.left + plotW + 16}" y="${m.top + 6}" width="12" height="12" rx="2" fill="${color}"/>`);
  P.push(`<text x="${m.left + plotW + 32}" y="${m.top + 17}" font-size="12" fill="#24292f">${repo.split('/')[1]}</text>`);
  P.push(`<text x="${m.left + plotW + 32}" y="${m.top + 33}" font-size="12" font-weight="600" fill="${color}">${total.toLocaleString()} ★</text>`);
  P.push('</svg>');
  return P.join('\n');
}

const meta = await getJson(`/repos/${REPO}`);
const total = meta.stargazers_count;
if (!total || total < 2) { console.error('Repo has too few stars to chart'); process.exit(1); }

const step = Math.max(1, Math.ceil(total / 70));
const ks = [];
for (let k = 1; k <= total; k += step) ks.push(k);
if (ks[ks.length - 1] !== total) ks.push(total);

const pts = [];
for (const k of ks) {
  const arrK = await getJson(`/repos/${REPO}/stargazers?per_page=1&page=${k}`);
  const at = arrK && arrK[0] && arrK[0].starred_at;
  if (at) pts.push([Date.parse(at), k]);
}

// Validate: the token must have returned real dated stars. Refuse to overwrite
// the committed chart with garbage if access is restricted.
if (pts.length < Math.min(ks.length, 5) || pts.length < ks.length * 0.8) {
  console.error(`Only ${pts.length}/${ks.length} sampled stars had a starred_at timestamp. ` +
    `The token likely lacks stargazer access for ${REPO} (GitHub restricts this to ` +
    `admins/collaborators). Not overwriting ${OUT}.`);
  process.exit(1);
}

writeFileSync(OUT, renderSVG(pts, total, REPO, COLOR));
console.log(`Wrote ${OUT} — ${total.toLocaleString()} stars, ${pts.length} points.`);
