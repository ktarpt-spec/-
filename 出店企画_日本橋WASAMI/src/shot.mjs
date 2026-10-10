// usage: node shot.mjs <in.svg|html> <out.png|pdf> [widthPx heightPx]
import { chromium } from 'playwright-core'
import path from 'path'
const [inp, out, w = 1600, h = 1131] = process.argv.slice(2)
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] })
const p = await b.newPage({ viewport: { width: +w, height: +h } })
await p.goto('file://' + path.resolve(inp))
await p.waitForTimeout(300)
if (out.endsWith('.pdf')) await p.pdf({ path: out, format: 'A3', landscape: true, printBackground: true, margin: { top: 0, bottom: 0, left: 0, right: 0 } })
else await p.screenshot({ path: out, fullPage: false })
await b.close()
