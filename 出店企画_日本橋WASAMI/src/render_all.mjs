// usage: node render_all.mjs <outdir> [view...]
import { chromium } from 'playwright-core'
import http from 'http'; import fs from 'fs'; import path from 'path'
const root = path.resolve('.')
const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' }
const srv = http.createServer((q, r) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); if (!fs.existsSync(f)) { r.writeHead(404); return r.end() } r.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r) }).listen(8765)
const [out, ...views] = process.argv.slice(2)
const all = views.length ? views : ['v4_lobby', 'v4_aisle', 'v4_room', 'v5_free', 'v1_lobby', 'v1_mri', 'ax1', 'ax4', 'ax5', 'ext', 'ext_entry']
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] })
for (const v of all) {
  const p = await b.newPage({ viewport: { width: 1600, height: 1000 } })
  p.on('pageerror', e => console.log(v, 'ERR', e.message)); p.on('console', m => { if (m.type() === 'error') console.log(v, m.text()) })
  const t = Date.now()
  await p.goto(`http://localhost:8765/render.html?view=${v}`)
  try { await p.waitForFunction('window.__done === true', null, { timeout: 240000 }) } catch (e) { console.log(v, 'timeout'); continue }
  await (await p.$('canvas')).screenshot({ path: path.join(out, `${v}.png`) })
  console.log(v, 'ok', ((Date.now() - t) / 1000).toFixed(1) + 's')
  await p.close()
}
await b.close(); srv.close()
