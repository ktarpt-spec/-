// 内装・外装イメージパース生成（three.js）。?view=<id>&w=&h=
import * as THREE from 'three'
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js'
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js'
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js'
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js'
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js'
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js'

const Q = new URLSearchParams(location.search)
const VIEW = Q.get('view') || 'v4_lobby'
const WPX = +(Q.get('w') || 1600), HPX = +(Q.get('h') || 1000)
const DATA = await (await fetch('./build/floors.json')).json()

// ------------------------------------------------------------ textures
function canvasTex(w, h, draw, repeat = [1, 1]) {
  const c = document.createElement('canvas'); c.width = w; c.height = h
  draw(c.getContext('2d'), w, h)
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...repeat); t.anisotropy = 8
  return t
}
let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647
const carpetTex = canvasTex(1024, 1024, (g, w, h) => {
  g.fillStyle = '#cdb893'; g.fillRect(0, 0, w, h)
  const img = g.getImageData(0, 0, w, h)
  for (let i = 0; i < img.data.length; i += 4) {
    const n = (rnd() - 0.5) * 34
    img.data[i] += n; img.data[i + 1] += n * 0.95; img.data[i + 2] += n * 0.85
  }
  g.putImageData(img, 0, 0)
  g.globalAlpha = 0.16; g.strokeStyle = '#fff6e6'; g.lineWidth = 3
  for (let k = 0; k < 70; k++) { // 葉脈状の柔らかな柄
    const x = rnd() * w, y = rnd() * h, r = 40 + rnd() * 110, a = rnd() * 6.28
    g.beginPath(); g.ellipse(x, y, r, r * 0.35, a, 0, Math.PI * 2); g.stroke()
    g.beginPath(); g.moveTo(x - Math.cos(a) * r, y - Math.sin(a) * r); g.lineTo(x + Math.cos(a) * r, y + Math.sin(a) * r); g.stroke()
  }
}, [3, 3])
function woodTex(base = '#b9946b', dark = '#9c7650', rep = [1, 1], vertical = true) {
  return canvasTex(512, 512, (g, w, h) => {
    g.fillStyle = base; g.fillRect(0, 0, w, h)
    for (let i = 0; i < 260; i++) {
      const x = rnd() * w; g.strokeStyle = dark; g.globalAlpha = 0.05 + rnd() * 0.12; g.lineWidth = 1 + rnd() * 3
      g.beginPath()
      if (vertical) { g.moveTo(x, 0); g.bezierCurveTo(x + rnd() * 8 - 4, h * 0.3, x + rnd() * 8 - 4, h * 0.6, x + rnd() * 6 - 3, h) }
      else { g.moveTo(0, x); g.bezierCurveTo(w * 0.3, x + rnd() * 8 - 4, w * 0.6, x + rnd() * 8 - 4, w, x + rnd() * 6 - 3) }
      g.stroke()
    }
  }, rep)
}
const plasterTex = canvasTex(512, 512, (g, w, h) => {
  g.fillStyle = '#e6e0d6'; g.fillRect(0, 0, w, h)
  const img = g.getImageData(0, 0, w, h)
  for (let i = 0; i < img.data.length; i += 4) { const n = (rnd() - 0.5) * 10; img.data[i] += n; img.data[i + 1] += n; img.data[i + 2] += n }
  g.putImageData(img, 0, 0)
}, [2, 2])
function logoTex(bg = '#f4f1ec', fg = '#24418f', w = 1024, h = 512, size = 230, sub = '') {
  const t = canvasTex(w, h, (g) => {
    g.fillStyle = bg; g.fillRect(0, 0, w, h)
    if (bg === '#f4f1ec') { // 銀座院同様の白い塗り壁テクスチャ
      g.globalAlpha = 0.07; g.strokeStyle = '#8a7b66'
      for (let i = 0; i < 400; i++) { g.lineWidth = 1 + rnd() * 2; g.beginPath(); const x = rnd() * w, y = rnd() * h; g.moveTo(x, y); g.quadraticCurveTo(x + 30, y - 20 + rnd() * 40, x + 60 * rnd(), y + 40 * rnd()); g.stroke() }
      g.globalAlpha = 1
    }
    g.fillStyle = fg; g.font = `500 ${size}px Inter, DejaVu Sans, sans-serif`; g.textAlign = 'center'; g.textBaseline = 'middle'
    g.fillText('fukka', w / 2, h / 2)
    if (sub) { g.font = `400 ${size * 0.22}px Inter, sans-serif`; g.fillText(sub, w / 2, h / 2 + size * 0.62) }
  })
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping
  return t
}

// ------------------------------------------------------------ materials
const M = {
  carpet: new THREE.MeshStandardMaterial({ map: carpetTex, roughness: 1 }),
  wall: new THREE.MeshStandardMaterial({ map: plasterTex, color: 0xffffff, roughness: 0.92 }),
  ceil: new THREE.MeshStandardMaterial({ color: 0xf1efea, roughness: 0.95 }),
  wood: new THREE.MeshStandardMaterial({ map: woodTex(), roughness: 0.6 }),
  woodH: new THREE.MeshStandardMaterial({ map: woodTex('#b9946b', '#9c7650', [2, 1], false), roughness: 0.6 }),
  woodDark: new THREE.MeshStandardMaterial({ map: woodTex('#6e5038', '#4f3726'), roughness: 0.55 }),
  door: new THREE.MeshStandardMaterial({ map: woodTex('#a98a66', '#8c6d4c', [1, 1]), roughness: 0.55 }),
  white: new THREE.MeshStandardMaterial({ color: 0xf6f4f0, roughness: 0.4 }),
  top: new THREE.MeshStandardMaterial({ color: 0xfbfaf8, roughness: 0.25 }),
  fabric: new THREE.MeshStandardMaterial({ color: 0xd8cebf, roughness: 0.98 }),
  fabric2: new THREE.MeshStandardMaterial({ color: 0xc9bba6, roughness: 0.98 }),
  leg: new THREE.MeshStandardMaterial({ map: woodTex('#d0a877', '#b88d5c'), roughness: 0.5 }),
  metal: new THREE.MeshStandardMaterial({ color: 0x9a9da1, metalness: 0.8, roughness: 0.35 }),
  dark: new THREE.MeshStandardMaterial({ color: 0x2c2f33, roughness: 0.6 }),
  glass: new THREE.MeshPhysicalMaterial({ color: 0xdfe9ef, transparent: true, opacity: 0.22, roughness: 0.05, metalness: 0, depthWrite: false }),
  sky: new THREE.MeshBasicMaterial({ color: 0xe9f1f7 }),
  light: new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xfff4e2, emissiveIntensity: 2.2 }),
  bed: new THREE.MeshStandardMaterial({ color: 0xf3ede4, roughness: 0.85 }),
  towel: new THREE.MeshStandardMaterial({ color: 0xe8dccb, roughness: 1 }),
  mri: new THREE.MeshStandardMaterial({ color: 0xf4f6f7, roughness: 0.3 }),
  mriBlue: new THREE.MeshStandardMaterial({ color: 0x8fa9c4, roughness: 0.4 }),
  plant: new THREE.MeshStandardMaterial({ color: 0x5f7a4f, roughness: 0.9 }),
  pot: new THREE.MeshStandardMaterial({ color: 0xd9d2c8, roughness: 0.8 }),
}

const scene = new THREE.Scene()
scene.background = new THREE.Color(0xf3f1ed)
const mm = (v) => v / 1000
function box(w, h, d, mat, x, y, z, parent = scene, cast = true) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)
  m.position.set(x, y, z); m.castShadow = cast; m.receiveShadow = true; parent.add(m); return m
}
// 平面座標(mm) → 3D: X=x, Z=-y
const P = (x, y) => [mm(x), -mm(y)]

// ------------------------------------------------------------ walls
function wallSeg(x0, y0, x1, y1, h, mat, openings = [], t = 100, base = 0) {
  // openings: [{a,b,top,bottom}] 区間は始点からの距離(mm)
  const L = Math.hypot(x1 - x0, y1 - y0), ux = (x1 - x0) / L, uy = (y1 - y0) / L
  const ang = Math.atan2(-(y1 - y0), x1 - x0)
  const piece = (s0, s1, z0, z1) => {
    if (s1 - s0 < 1 || z1 - z0 < 1) return
    const cx = x0 + ux * (s0 + s1) / 2, cy = y0 + uy * (s0 + s1) / 2
    const m = new THREE.Mesh(new THREE.BoxGeometry(mm(s1 - s0), mm(z1 - z0), mm(t)), mat)
    const [X, Z] = P(cx, cy); m.position.set(X, mm(base + (z0 + z1) / 2), Z); m.rotation.y = ang
    m.castShadow = true; m.receiveShadow = true; scene.add(m)
  }
  const ops = [...openings].sort((p, q) => p.a - q.a)
  let s = 0
  for (const o of ops) {
    piece(s, o.a, 0, h)
    piece(o.a, o.b, o.top, h)
    if (o.bottom) piece(o.a, o.b, 0, o.bottom)
    s = o.b
  }
  piece(s, L, 0, h)
}

function roomWalls(f) {
  const H = f.partition_h
  for (const r of f.rooms) {
    if (['open', 'existing'].includes(r.kind)) continue
    const edges = { S: [r.x0, r.y0, r.x1, r.y0], N: [r.x0, r.y1, r.x1, r.y1], W: [r.x0, r.y0, r.x0, r.y1], E: [r.x1, r.y0, r.x1, r.y1] }
    let keys = Object.keys(edges)
    if (r.kind === 'corridor') keys = f.floor === '1F' ? ['N', 'S'] : ['N', 'W', 'E']
    for (const k of keys) {
      const [a, b, c, d] = edges[k]
      if (k === 'S' && r.y0 <= 0) continue
      if (k === 'N' && r.y1 >= f.D) continue
      if (k === 'W' && r.x0 <= 0) continue
      if (k === 'E' && r.x1 >= f.W) continue
      if (r.kind === 'corridor' && f.floor === '1F') continue
      const ops = []
      for (const dd of r.doors) if (dd.side === k) {
        const s0 = (k === 'S' || k === 'N') ? dd.at - a : dd.at - b
        ops.push({ a: s0 - dd.w / 2, b: s0 + dd.w / 2, top: 2100 })
        doorLeaf(k, r, dd)
      }
      // 隣室側の扉もこの壁を共有する場合
      for (const o of f.rooms) if (o !== r) for (const dd of o.doors) {
        if ((dd.side === 'S' && k === 'N' && Math.abs(o.y0 - r.y1) < 1 && dd.at > a && dd.at < c) ||
            (dd.side === 'N' && k === 'S' && Math.abs(o.y1 - r.y0) < 1 && dd.at > a && dd.at < c))
          ops.push({ a: dd.at - a - dd.w / 2, b: dd.at - a + dd.w / 2, top: 2100 })
        if ((dd.side === 'W' && k === 'E' && Math.abs(o.x0 - r.x1) < 1) || (dd.side === 'E' && k === 'W' && Math.abs(o.x1 - r.x0) < 1)) {
          const yy = dd.at; if (yy > b && yy < d) ops.push({ a: yy - b - dd.w / 2, b: yy - b + dd.w / 2, top: 2100 })
        }
      }
      wallSeg(a, b, c, d, r.kind === 'mri' ? f.ch_render : H, M.wall, ops)
      if (r.kind !== 'mri' && H < f.ch_render) { // 欄間上部開放：小口見切り
        const L = Math.hypot(c - a, d - b)
        const m = box(mm(L), 0.02, 0.11, M.white, 0, 0, 0)
        const [X, Z] = P((a + c) / 2, (b + d) / 2); m.position.set(X, mm(H) + 0.01, Z); m.rotation.y = Math.atan2(-(d - b), c - a)
      }
    }
  }
}

function doorLeaf(side, r, dd) {
  const w = dd.w, th = 35
  if (dd.type === 'swing') return
  let x, y, rot = 0
  if (side === 'S') { x = dd.at; y = r.y0 - 60 } else if (side === 'N') { x = dd.at; y = r.y1 + 60 }
  else if (side === 'W') { x = r.x0 - 60; y = dd.at; rot = Math.PI / 2 } else { x = r.x1 + 60; y = dd.at; rot = Math.PI / 2 }
  const [X, Z] = P(x, y)
  const m = box(mm(w + 80), 2.08, mm(th), M.door, X, 1.04, Z); m.rotation.y = rot
  const hd = box(0.02, 0.5, 0.03, M.metal, 0, 1.0, 0, m); hd.position.set(mm(w / 2) - 0.08, 0, mm(th) / 2 + 0.01)
  const hd2 = hd.clone(); hd2.position.z = -hd.position.z; m.add(hd2)
  // 室名サイン
  const pl = box(0.16, 0.08, 0.006, M.white, 0, 0.4, 0, m); pl.position.set(-mm(w / 2) + 0.15, 0.4, (side === 'S' || side === 'E' ? -1 : 1) * 0.025)
}

// ------------------------------------------------------------ furniture
function chair(x, y, rot, mat = M.fabric) {
  const g = new THREE.Group(); const [X, Z] = P(x, y); g.position.set(X, 0, Z); g.rotation.y = THREE.MathUtils.degToRad(rot - 90)
  box(0.6, 0.12, 0.56, mat, 0, 0.44, 0.02, g)
  box(0.6, 0.38, 0.1, mat, 0, 0.68, -0.25, g)
  box(0.08, 0.2, 0.56, mat, -0.26, 0.58, 0.02, g); box(0.08, 0.2, 0.56, mat, 0.26, 0.58, 0.02, g)
  box(0.6, 0.16, 0.6, mat, 0, 0.34, 0, g)
  for (const [lx, lz] of [[-0.25, -0.25], [0.25, -0.25], [-0.25, 0.25], [0.25, 0.25]]) {
    const l = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.014, 0.27, 10), M.leg); l.position.set(lx, 0.135, lz); l.castShadow = true; g.add(l)
  }
  scene.add(g); return g
}
function bed(x, y, rot = 0) {
  const g = new THREE.Group(); const [X, Z] = P(x, y); g.position.set(X, 0, Z); g.rotation.y = rot
  box(0.62, 0.5, 1.8, M.wood, 0, 0.25, 0, g)
  const top = new THREE.Mesh(new RoundedBoxGeometry(0.72, 0.12, 1.92, 3, 0.04), M.bed); top.position.set(0, 0.58, 0); top.castShadow = true; g.add(top)
  const pil = new THREE.Mesh(new RoundedBoxGeometry(0.5, 0.08, 0.32, 3, 0.03), M.white); pil.position.set(0, 0.67, -0.72); g.add(pil)
  const tw = box(0.74, 0.015, 0.55, M.towel, 0, 0.645, 0.45, g)
  scene.add(g); return g
}
function stool(x, y) {
  const [X, Z] = P(x, y)
  const s = new THREE.Mesh(new THREE.CylinderGeometry(0.19, 0.19, 0.06, 24), M.fabric2); s.position.set(X, 0.5, Z); s.castShadow = true; scene.add(s)
  const l = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.47, 10), M.metal); l.position.set(X, 0.24, Z); scene.add(l)
  const b = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.02, 24), M.metal); b.position.set(X, 0.01, Z); scene.add(b)
}
function plant(x, y, h = 1.2) {
  const [X, Z] = P(x, y)
  const p = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.14, 0.38, 20), M.pot); p.position.set(X, 0.19, Z); scene.add(p)
  for (let i = 0; i < 9; i++) {
    const l = new THREE.Mesh(new THREE.SphereGeometry(0.16 + rnd() * 0.1, 10, 8), M.plant)
    l.position.set(X + (rnd() - 0.5) * 0.35, 0.45 + h * (0.35 + rnd() * 0.6), Z + (rnd() - 0.5) * 0.35); l.scale.set(1, 1.4, 0.5); l.rotation.y = rnd() * 3; l.castShadow = true; scene.add(l)
  }
}

function treatRoom(r) {
  const cx = (r.x0 + r.x1) / 2
  if (r.y1 - r.y0 > r.x1 - r.x0 - 100) {
    bed(r.x0 + 650, r.y1 - 1175)
    stool(r.x1 - 520, r.y1 - 1500)
    box(0.42, 0.75, 0.42, M.wood, ...[mm(r.x1 - 425), 0.375, -mm(r.y1 - 425)])
    box(0.42, 0.02, 0.42, M.top, mm(r.x1 - 425), 0.76, -mm(r.y1 - 425))
    const bk = box(0.4, 0.25, 0.35, M.woodH, mm(r.x1 - 450), 0.125, -mm(r.y0 + 425))
    // 壁付フック・ミラー
    box(0.5, 0.025, 0.22, M.wood, mm(r.x1 - 160), 1.55, -mm(r.y0 + 1100)).rotation.y = Math.PI / 2
    box(0.3, 0.06, 0.18, M.towel, mm(r.x1 - 160), 1.6, -mm(r.y0 + 1100)).rotation.y = Math.PI / 2
  } else {
    bed((r.x0 + r.x1) / 2 - 200, r.y1 - 650, Math.PI / 2)
  }
}

function reception(rc, f) {
  const [X, Z] = P(rc.cx, rc.cy)
  const a0 = THREE.MathUtils.degToRad(rc.a0), a1 = THREE.MathUtils.degToRad(rc.a1)
  const shape = new THREE.Shape()
  const R1 = mm(rc.r), R2 = mm(rc.r - 550)
  shape.absarc(0, 0, R1, a0, a1, false); shape.absarc(0, 0, R2, a1, a0, true)
  const front = new THREE.Mesh(new THREE.ExtrudeGeometry(shape, { depth: 1.0, bevelEnabled: false, curveSegments: 64 }), M.woodH)
  front.rotation.x = -Math.PI / 2; front.position.set(X, 0, Z); front.castShadow = front.receiveShadow = true; scene.add(front)
  const shape2 = new THREE.Shape(); shape2.absarc(0, 0, R1 + 0.03, a0 - 0.01, a1 + 0.01, false); shape2.absarc(0, 0, R2 - 0.03, a1 + 0.01, a0 - 0.01, true)
  const top = new THREE.Mesh(new THREE.ExtrudeGeometry(shape2, { depth: 0.035, bevelEnabled: false, curveSegments: 64 }), M.top)
  top.rotation.x = -Math.PI / 2; top.position.set(X, 1.0, Z); top.castShadow = true; scene.add(top)
  // 受付背面：棚＋ロゴ壁（銀座院同様）
  const [bx0, by0, bx1, by1] = rc.back
  const horiz = (bx1 - bx0) > (by1 - by0)
  const len = horiz ? bx1 - bx0 : by1 - by0, dep = horiz ? by1 - by0 : bx1 - bx0
  const g = new THREE.Group(); const [GX, GZ] = P((bx0 + bx1) / 2, (by0 + by1) / 2); g.position.set(GX, 0, GZ)
  // ロゴ壁の向き：受付カウンター側（rc中心側）
  const toward = horiz ? (rc.cy < by0 ? 0 : Math.PI) : (rc.cx < bx0 ? -Math.PI / 2 : Math.PI / 2)
  g.rotation.y = toward
  const Lm = mm(len), Dm = mm(dep), Hh = 2.45
  box(Lm, Hh, Dm, M.woodH, 0, Hh / 2, 0, g)
  // 左：オープン棚（升目）
  const sw = Lm * 0.36
  box(sw, Hh - 0.1, 0.02, M.woodDark, -Lm / 2 + sw / 2 + 0.05, Hh / 2, Dm / 2 + 0.005, g, false)
  for (let i = 0; i < 6; i++) box(sw, 0.025, 0.3, M.wood, -Lm / 2 + sw / 2 + 0.05, 0.12 + i * 0.44, Dm / 2 + 0.15, g)
  for (let j = 0; j < 3; j++) box(0.025, Hh - 0.1, 0.3, M.wood, -Lm / 2 + 0.05 + j * sw / 2, Hh / 2, Dm / 2 + 0.15, g)
  // 右：白い塗り壁＋ロゴ
  const lw = Lm * 0.44
  const lp = new THREE.Mesh(new THREE.PlaneGeometry(lw, Hh - 0.05), new THREE.MeshStandardMaterial({ map: logoTex('#f4f1ec', '#24418f', 1024, 1024 * (Hh - 0.05) / lw, 260), roughness: 0.9 }))
  lp.position.set(Lm / 2 - lw / 2 - 0.02, Hh / 2, Dm / 2 + 0.006); g.add(lp)
  // 中央：斜めの木パネル
  const mid = box(Lm * 0.2, Hh, 0.06, M.wood, Lm / 2 - lw - Lm * 0.1 - 0.02, Hh / 2, Dm / 2 + 0.03, g); mid.rotation.y = 0.12
  scene.add(g)
  // 天井：木の円形ボーダー（間接照明）
  const ring = new THREE.Mesh(new THREE.CylinderGeometry(R1 + 0.55, R1 + 0.55, 0.32, 96, 1, true), M.woodDark)
  ring.position.set(X, mm(f.ch_render) - 0.16, Z); scene.add(ring)
  const disk = new THREE.Mesh(new THREE.CircleGeometry(R1 + 0.55, 96), M.ceil); disk.rotation.x = Math.PI / 2; disk.position.set(X, mm(f.ch_render) - 0.32, Z); scene.add(disk)
  const glow = new THREE.Mesh(new THREE.TorusGeometry(R1 + 0.53, 0.012, 6, 96), M.light); glow.rotation.x = Math.PI / 2; glow.position.set(X, mm(f.ch_render) - 0.325, Z); scene.add(glow)
  for (let i = 0; i < 6; i++) {
    const a = a0 + (a1 - a0) * (i + 0.5) / 6
    const d = new THREE.Mesh(new THREE.CircleGeometry(0.05, 20), M.light); d.rotation.x = Math.PI / 2
    d.position.set(X + Math.cos(a) * R1 * 0.85, mm(f.ch_render) - 0.33, Z - Math.sin(a) * R1 * 0.85); scene.add(d)
    const sp = new THREE.SpotLight(0xffe7c4, 3.2, 5, 0.55, 0.6, 1.5); sp.position.copy(d.position); sp.target.position.set(d.position.x, 0, d.position.z); scene.add(sp, sp.target)
  }
  // PC・レジ
  const m = Math.atan2(Math.sin(a0) + Math.sin(a1), Math.cos(a0) + Math.cos(a1))
  for (const k of [-0.5, 0.5]) {
    const a = m + k
    const mon = box(0.4, 0.26, 0.03, M.dark, X + Math.cos(a) * (R2 + 0.2), 1.26, Z - Math.sin(a) * (R2 + 0.2)); mon.rotation.y = a + Math.PI / 2
  }
  for (const k of [-0.65, 0.65]) stool(rc.cx + Math.cos(m + k) * (rc.r - 900), rc.cy + Math.sin(m + k) * (rc.r - 900))
}

// ------------------------------------------------------------ shell (floors 4/5)
const COLS = [1708, 4408, 7108, 9808, 12508, 15208, 17908, 20608]
function upperShell(f) {
  const W = f.W, D = f.D, CH = f.ch_render
  // 道路側（Y1面）窓
  const wOps = []; for (let s = 400; s < D - 300; s += 2900) wOps.push({ a: s, b: Math.min(s + 2500, D + 100), top: 2550, bottom: 700 })
  wallSeg(-150, -100, -150, D + 250, CH, M.wall, wOps, 300)
  const skyW = new THREE.Mesh(new THREE.PlaneGeometry(mm(D + 400), mm(CH)), M.sky); skyW.rotation.y = Math.PI / 2; skyW.position.set(-0.6, mm(CH) / 2, -mm(D / 2)); scene.add(skyW)
  // X1側窓（柱間）
  const xs = [-300, ...COLS, W + 300], nOps = []
  for (let i = 0; i < xs.length - 1; i++) { const a = xs[i] + 700, b = xs[i + 1] - 700; if (b - a > 500) nOps.push({ a: a + 300, b: b + 300, top: 2550, bottom: 700 }) }
  wallSeg(-300, D + 150, W + 300, D + 150, CH, M.wall, nOps, 300)
  const skyN = new THREE.Mesh(new THREE.PlaneGeometry(mm(W + 2000), mm(CH)), M.sky); skyN.position.set(mm(W / 2), mm(CH) / 2, -mm(D + 700)); scene.add(skyN)
  for (const c of COLS) box(0.8, mm(CH), 0.45, M.wall, mm(c), mm(CH) / 2, -mm(D - 175))
  wallSeg(W + 150, D + 250, W + 150, -100, CH, M.wall, [], 300)
  // コア側壁（EVホール開口）
  wallSeg(-300, -50, 9750, -50, CH, M.wall, [], 100)
  wallSeg(12350, -50, W + 300, -50, CH, M.wall, [], 100)
  wallSeg(9750, -2600, 12350, -2600, CH, M.wall, [], 100)
  box(1.0, 2.1, 0.04, M.metal, mm(10500), 1.05, mm(2550))
  box(1.0, 2.1, 0.04, M.metal, mm(11600), 1.05, mm(2550))
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(mm(W + 600), mm(D + 3000)), M.ceil); ceil.rotation.x = Math.PI / 2
  ceil.position.set(mm(W / 2), mm(CH), -mm(D / 2 - 1300)); ceil.receiveShadow = true; scene.add(ceil)
  const fl = new THREE.Mesh(new THREE.PlaneGeometry(mm(W + 600), mm(D + 6000)), M.carpet); fl.rotation.x = -Math.PI / 2
  fl.position.set(mm(W / 2), 0, -mm(D / 2 - 2700)); fl.receiveShadow = true; scene.add(fl)
}

function windowsN(f) { // 窓枠・ロールスクリーン
  const W = f.W, D = f.D
  const xs = [-300, ...COLS, W + 300]
  const scr = new THREE.MeshStandardMaterial({ color: 0xf6f1e8, roughness: 1 })
  for (let i = 0; i < xs.length - 1; i++) {
    const a = Math.max(0, xs[i] + 400), b = Math.min(W, xs[i + 1] - 400); if (b - a < 400) continue
    box(mm(b - a), 0.05, 0.08, M.metal, mm((a + b) / 2), 0.7, -mm(D + 100))
    box(0.04, 1.85, 0.06, M.metal, mm((a + b) / 2), 1.625, -mm(D + 100))
    box(mm(b - a), 0.5, 0.01, scr, mm((a + b) / 2), 2.3, -mm(D + 20))
  }
}

function ceilingLights(f, rects) {
  const CH = mm(f.ch_render)
  for (const [x0, y0, x1, y1] of rects) {
    const [X, Z] = P((x0 + x1) / 2, (y0 + y1) / 2)
    const horiz = (x1 - x0) > (y1 - y0)
    const l = new THREE.Mesh(new THREE.BoxGeometry(horiz ? mm(x1 - x0) : 0.08, 0.01, horiz ? 0.08 : mm(y1 - y0)), M.light)
    l.position.set(X, CH - 0.006, Z); scene.add(l)
  }
}

function addPointLights(f, pts, intensity = 2.2, dist = 6) {
  for (const [x, y] of pts) {
    const [X, Z] = P(x, y)
    const pl = new THREE.PointLight(0xfff1dc, intensity, dist, 1.4); pl.position.set(X, mm(f.ch_render) - 0.35, Z); scene.add(pl)
  }
}

// ------------------------------------------------------------ build floors
function buildUpper(key) {
  const f = DATA[key]; f.ch_render = f.ch
  upperShell(f); windowsN(f); roomWalls(f)
  for (const r of f.rooms) if (r.kind === 'treat') treatRoom(r)
  // 避難経路のガラス自動ドア
  for (const e of f.entrances || []) if (e.side === 'CORE') {
    const [X, Z] = P(e.at, 1400)
    box(mm(e.w), 2.4, 0.02, M.glass, X, 1.2, Z, scene, false)
    box(mm(e.w) + 0.1, 0.12, 0.12, M.metal, X, 2.44, Z)
    // 自動ドア上のロゴ
  }
  if (f.reception) reception(f.reception, f)
  for (const [x, y, rot] of f.chairs) chair(x, y, rot)
  // ラウンジ（5F）
  if (f.lounge) {
    const L = f.lounge
    box(0.6, 0.42, mm(L.y1 - L.y0), M.fabric, ...[mm(L.x0 + 300), 0.21, -mm((L.y0 + L.y1) / 2)])
    box(mm(3800), 0.42, 0.6, M.fabric, mm(L.x0 + 1900), 0.21, -mm(L.y1 - 300))
    box(0.12, 0.45, mm(L.y1 - L.y0), M.fabric2, mm(L.x0 + 60), 0.62, -mm((L.y0 + L.y1) / 2))
    box(mm(3800), 0.45, 0.12, M.fabric2, mm(L.x0 + 1900), 0.62, -mm(L.y1 - 60))
    for (const [tx, ty] of [[1800, 1700], [3500, 900]]) {
      const t = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.45, 0.03, 40), M.top); t.position.set(mm(L.x0 + tx), 0.7, -mm(L.y0 + ty)); t.castShadow = true; scene.add(t)
      const l = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.7, 10), M.leg); l.position.set(mm(L.x0 + tx), 0.35, -mm(L.y0 + ty)); scene.add(l)
    }
    for (const [tx, ty, r] of [[5200, 1900, 270], [6400, 1900, 270], [5200, 700, 90], [6400, 700, 90]]) chair(L.x0 + tx, L.y0 + ty, r, M.fabric)
    box(0.6, 0.45, 0.5, M.wood, mm(L.x0 + 5800), 0.225, -mm(L.y0 + 1300))
    // ウォーターサーバー
    box(0.32, 1.2, 0.35, M.white, mm(L.x1 + 250), 0.6, -mm(L.y0 + 300))
    plant(L.x0 + 7000, L.y1 - 300, 1.4)
    // 壁面ロゴ（フリースペース）
  }
  // 照明計画：施術室ごとにライン照明、通路・待合に線状照明
  const rects = []
  for (const r of f.rooms) {
    if (r.kind === 'treat') rects.push([r.x0 + 500, (r.y0 + r.y1) / 2, r.x1 - 500, (r.y0 + r.y1) / 2 + 1])
    if (r.kind === 'room' || r.kind === 'service') rects.push([r.x0 + 400, (r.y0 + r.y1) / 2, r.x1 - 400, (r.y0 + r.y1) / 2 + 1])
  }
  rects.push([300, 5500, 9500, 5501], [13200, 5500, 22700, 5501])
  rects.push([13000, 2600, 17200, 2601], [7400, 2600, 9800, 2601], [5000, 700, 9600, 701])
  if (f.lounge) rects.push([8000, 3000, 15000, 3001])
  ceilingLights(f, rects)
  const pts = []
  for (let x = 1500; x < f.W; x += 3000) { pts.push([x, 5500]); pts.push([x, 2600]) }
  for (const r of f.rooms) if (r.kind === 'treat') pts.push([(r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2])
  addPointLights(f, pts, 1.6, 5)
  plant(17300, 4500, 1.3); plant(7600, 1700, 1.0)
}

function build1F() {
  const f = DATA['1F']; f.ch_render = 3000
  const W = f.W, D = f.D, CH = f.ch_render
  const fl = new THREE.Mesh(new THREE.PlaneGeometry(mm(W + 2000), mm(D + 2000)), M.carpet); fl.rotation.x = -Math.PI / 2; fl.position.set(mm(W / 2), 0, -mm(D / 2)); fl.receiveShadow = true; scene.add(fl)
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(mm(W + 2000), mm(D + 2000)), M.ceil); ceil.rotation.x = Math.PI / 2; ceil.position.set(mm(W / 2), mm(CH), -mm(D / 2)); scene.add(ceil)
  // 外周壁
  wallSeg(-150, -100, -150, 4950, CH, M.wall, [{ a: 1650, b: 3350, top: 2900, bottom: 150 }], 300)   // 道路側 SSW-2
  wallSeg(-300, -150, W + 300, -150, CH, M.wall, [{ a: 3150, b: 3950, top: 2100 }], 300)            // 館内側
  wallSeg(-300, D + 150, W + 300, D + 150, CH, M.wall, [], 300)
  wallSeg(W + 150, -100, W + 150, D + 100, CH, M.wall, [], 300)
  for (const c of f.columns) box(0.8, mm(CH), 0.4, M.wall, mm(c[0]), mm(CH) / 2, -mm(D - 200))
  // 道路側窓の外：明るい外光＋木調ルーバー（600mm後退）
  const sky = new THREE.Mesh(new THREE.PlaneGeometry(1.8, 2.8), M.sky); sky.rotation.y = Math.PI / 2; sky.position.set(-0.32, 1.5, -mm(2500)); scene.add(sky)
  for (let i = 0; i < 12; i++) box(0.04, 2.4, 0.06, M.wood, mm(650), 1.3, -mm(1600 + i * 155))
  box(0.36, 0.12, 0.02, new THREE.MeshStandardMaterial({ map: logoTex('#f4efe6', '#24418f', 512, 170, 120) }), mm(700), 1.75, -mm(2450)).rotation.y = -Math.PI / 2
  // エントランス（既設アプローチ）とのガラス間仕切
  wallSeg(1900, 4950, 1900, D, CH, M.glass, [{ a: 200, b: 1400, top: 2400 }], 30)
  wallSeg(0, 4950, 1900, 4950, CH, M.wall, [], 100)
  // MRI室は天井まで（シールド）
  roomWalls(f)
  // 受付
  reception(f.reception, f)
  for (const [x, y, rot] of f.chairs) chair(x, y, rot)
  // MRI
  const mriR = f.rooms.find(r => r.id === 'mri'); const mx = mm((mriR.x0 + mriR.x1) / 2 + 300)
  const gan = new THREE.Mesh(new RoundedBoxGeometry(2.2, 2.0, 1.8, 6, 0.35), M.mri); gan.position.set(mx, 1.0, -mm(mriR.y0 + 3400)); gan.castShadow = true; scene.add(gan)
  const hole = new THREE.Mesh(new THREE.CylinderGeometry(0.33, 0.33, 1.82, 48), M.dark); hole.rotation.x = Math.PI / 2; hole.position.set(mx, 1.0, -mm(mriR.y0 + 3400)); scene.add(hole)
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.42, 0.06, 16, 64), M.mriBlue); ring.position.set(mx, 1.0, -mm(mriR.y0 + 2490)); scene.add(ring)
  box(0.6, 0.75, 2.0, M.mri, mx, 0.375, -mm(mriR.y0 + 1400)); box(0.55, 0.06, 2.0, M.bed, mx, 0.78, -mm(mriR.y0 + 1400))
  // 診察・処置
  const ex = f.rooms.find(r => r.id === 'ex'); box(1.4, 0.72, 0.6, M.wood, mm(ex.x0 + 900), 0.36, -mm(ex.y0 + 600)); bed(ex.x1 - 550, ex.y1 - 1150)
  const tr = f.rooms.find(r => r.id === 'tr'); bed(tr.x0 + 1400, tr.y0 + 1250, Math.PI / 2)
  ceilingLights(f, [[600, 1500, 3400, 1501], [600, 3300, 3400, 3301], [5300, 3500, 9700, 3501], [5400, 5300, 7700, 5301], [5400, 1450, 7700, 1451], [10500, 3300, 13400, 3301]])
  addPointLights(f, [[1500, 1500], [1500, 4000], [3500, 2500], [7500, 3500], [12000, 3300]], 2.2, 6)
  plant(300, 4600, 1.2); plant(3300, 300, 0.9)
}

// ------------------------------------------------------------ exterior
function buildExterior() {
  scene.background = new THREE.Color(0xc9d6e0)
  const H1 = 4.95, HT = 3.9, BW = 14.3, N = 13
  const facade = new THREE.Group(); scene.add(facade)
  const ecp = new THREE.MeshStandardMaterial({ color: 0xb9b2a8, roughness: 0.85 })
  const panelA = new THREE.MeshStandardMaterial({ color: 0xa9a49d, roughness: 0.55, metalness: 0.2 })
  const alum = new THREE.MeshStandardMaterial({ color: 0x8d9298, roughness: 0.4, metalness: 0.6 })
  const glassEx = new THREE.MeshStandardMaterial({ color: 0x55636f, roughness: 0.12, metalness: 0.35 })
  const warm = new THREE.MeshStandardMaterial({ color: 0xfff1d8, emissive: 0xffe6bf, emissiveIntensity: 0.6 })
  // 立面：u(左=X1)→ X、高さ → Y、建物面 Z=0
  const parts = [[0, 2.3, 'entry'], [2.3, 3.9, 'panel'], [3.9, 5.6, 'window'], [5.6, 7.3, 'panel'], [7.3, 10.3, 'ecp'], [10.3, BW, 'bldg']]
  const h1 = H1 - 0.9
  for (const [a, b, k] of parts) {
    const w = b - a, cx = a + w / 2
    if (k === 'panel') { box(w, h1, 0.2, panelA, cx, h1 / 2, 0); for (let j = 1; j < 4; j++) box(w, 0.01, 0.205, ecp, cx, h1 * j / 4, 0) }
    if (k === 'ecp') { box(w, h1, 0.2, ecp, cx, h1 / 2, 0); for (let j = 1; j < 8; j++) box(w, 0.008, 0.205, panelA, cx, h1 * j / 8, 0) }
    if (k === 'window') {
      box(w, h1, 0.05, glassEx, cx, h1 / 2, -0.05)
      box(w, 0.08, 0.12, alum, cx, h1, 0); box(0.06, h1, 0.12, alum, a + 0.03, h1 / 2, 0); box(0.06, h1, 0.12, alum, b - 0.03, h1 / 2, 0)
      // 室内：600mm後退の木調ルーバー（透けて見える）
      box(w, 3.0, 0.02, warm, cx, 1.6, -1.2)
      for (let i = 0; i < 12; i++) box(0.04, 2.5, 0.06, M.wood, a + 0.12 + i * (w - 0.24) / 11, 1.35, -0.75)
      box(0.36, 0.12, 0.01, new THREE.MeshStandardMaterial({ map: logoTex('#f4efe6', '#24418f', 512, 170, 120) }), cx, 1.75, -0.71)
    }
    if (k === 'entry') {
      // 既設アプローチ（奥行き約1.9m）：奥壁木調＋ロゴ、間接照明
      box(w, 0.3, 2.0, ecp, cx, h1 - 0.15, -1.0)
      box(0.1, h1, 2.0, ecp, a + 0.05, h1 / 2, -1.0)
      const back = box(w - 0.1, h1 - 0.3, 0.05, M.woodH, cx + 0.05, (h1 - 0.3) / 2, -1.95)
      for (let i = 1; i < 10; i++) box(0.012, h1 - 0.3, 0.06, M.woodDark, a + 0.1 + i * (w - 0.1) / 10, (h1 - 0.3) / 2, -1.94)
      const lg = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 0.3), new THREE.MeshBasicMaterial({ map: logoTex('#b9946b', '#f6eedf', 768, 256, 170), transparent: false }))
      lg.position.set(cx + 0.05, 1.9, -1.915); scene.add(lg)
      box(w - 0.2, 0.02, 0.05, M.light, cx + 0.05, h1 - 0.32, -1.85)
      const sl = new THREE.SpotLight(0xffe2b8, 6, 6, 0.9, 0.8, 1.2); sl.position.set(cx, h1 - 0.4, -1.5); sl.target.position.set(cx, 0.5, -1.95); scene.add(sl, sl.target)
      // 扉（ガラス）
      box(0.05, h1 - 0.3, 1.2, M.glass, b - 0.15, (h1 - 0.3) / 2, -1.3, scene, false)
    }
    if (k === 'bldg') {
      box(w, h1, 0.05, glassEx, cx, h1 / 2, -0.3)
      for (let j = 0; j <= 4; j++) box(0.07, h1, 0.15, alum, a + w * j / 4, h1 / 2, -0.25)
      box(w * 0.5, 2.4, 0.04, new THREE.MeshStandardMaterial({ color: 0xc8d4dc, roughness: 0.05, metalness: 0.4 }), cx, 1.2, -0.27)
      // S1
      box(0.64, 0.34, 0.04, M.dark, a + 0.72, 1.53, 0.02)
      const s1 = new THREE.Mesh(new THREE.PlaneGeometry(0.58, 0.205), new THREE.MeshBasicMaterial({ map: logoTex('#f5f3ef', '#24418f', 512, 182, 120) })); s1.position.set(a + 0.72, 1.48, 0.045); scene.add(s1)
    }
  }
  // 1F庇まわり・2F以上
  box(BW, 0.9, 0.35, ecp, BW / 2, H1 - 0.45, 0.05)
  for (let i = 1; i < N; i++) {
    const y0 = H1 + HT * (i - 1)
    box(BW, 0.65, 0.3, panelA, BW / 2, y0 + 0.325, 0.05)
    box(BW - 1.2, HT - 0.65, 0.05, glassEx, BW / 2, y0 + 0.65 + (HT - 0.65) / 2, -0.1)
    for (let k = 0; k <= 14; k++) box(0.08, HT - 0.65, 0.35, alum, 0.6 + k * (BW - 1.2) / 14, y0 + 0.65 + (HT - 0.65) / 2, 0.1)
    if (i === 3 || i === 4) box(BW - 1.3, 0.9, 0.01, new THREE.MeshStandardMaterial({ color: 0xf2ece2, roughness: 1 }), BW / 2, y0 + HT - 0.6, -0.2) // ロールスクリーン
  }
  box(0.6, H1 + HT * (N - 1), 0.4, panelA, 0.3, (H1 + HT * (N - 1)) / 2, 0.05)
  box(0.6, H1 + HT * (N - 1), 0.4, panelA, BW - 0.3, (H1 + HT * (N - 1)) / 2, 0.05)
  // 隣接建物（簡易）
  const nb = new THREE.MeshStandardMaterial({ color: 0x9a9893, roughness: 0.8 })
  box(10, 30, 10, nb, -5.3, 15, -5); box(10, 22, 10, nb, BW + 5.3, 11, -5)
  for (let y = 4; y < 30; y += 3.6) box(9.6, 1.8, 0.05, glassEx, -5.3, y, 0.02)
  for (let y = 4; y < 22; y += 3.4) box(9.6, 1.6, 0.05, glassEx, BW + 5.3, y, 0.02)
  // 歩道・車道
  const pave = new THREE.MeshStandardMaterial({ map: canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#bdb6ac'; g.fillRect(0, 0, w, h); g.strokeStyle = '#a69e93'; g.lineWidth = 2; for (let i = 0; i <= 8; i++) { g.beginPath(); g.moveTo(i * 64, 0); g.lineTo(i * 64, h); g.stroke(); g.beginPath(); g.moveTo(0, i * 64); g.lineTo(w, i * 64); g.stroke() } }, [12, 3]), roughness: 0.95 })
  const sw = new THREE.Mesh(new THREE.PlaneGeometry(60, 6), pave); sw.rotation.x = -Math.PI / 2; sw.position.set(BW / 2, 0, 3); sw.receiveShadow = true; scene.add(sw)
  const road = new THREE.Mesh(new THREE.PlaneGeometry(60, 30), new THREE.MeshStandardMaterial({ color: 0x6d6f72, roughness: 0.95 })); road.rotation.x = -Math.PI / 2; road.position.set(BW / 2, -0.12, 21); scene.add(road)
  box(60, 0.15, 0.2, ecp, BW / 2, -0.05, 6)
  // 街路樹
  for (const x of [-3, 9, 21]) {
    const tr = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.14, 3.2, 10), M.woodDark); tr.position.set(x, 1.6, 5.2); scene.add(tr)
    for (let i = 0; i < 14; i++) { const l = new THREE.Mesh(new THREE.SphereGeometry(0.7 + rnd() * 0.5, 10, 8), M.plant); l.position.set(x + (rnd() - 0.5) * 2, 3.6 + rnd() * 1.6, 5.2 + (rnd() - 0.5) * 1.6); l.castShadow = true; scene.add(l) }
  }
  const sun = new THREE.DirectionalLight(0xfff3e0, 2.2); sun.position.set(-20, 40, 30); sun.castShadow = true
  sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, { left: -25, right: 25, top: 25, bottom: -10, near: 1, far: 120 }); scene.add(sun)
  scene.add(new THREE.HemisphereLight(0xeaf2ff, 0xb8b0a4, 1.2))
}

// ------------------------------------------------------------ views
const VIEWS = {
  // 4F 待合から受付を望む（銀座院の構図）
  v4_lobby: { build: () => buildUpper('4F'), pos: [17400, 250, 1450], look: [10200, 3900, 1150], fov: 64 },
  v4_aisle: { build: () => buildUpper('4F'), pos: [22800, 5500, 1500], look: [4000, 5300, 1250], fov: 66 },
  v4_room: { build: () => buildUpper('4F'), pos: [12600, 6400, 1500], look: [11000, 8600, 1000], fov: 72, hideCeil: false },
  v5_free: { build: () => buildUpper('5F'), pos: [15200, 1900, 1450], look: [7800, 4700, 1100], fov: 64 },
  v1_lobby: { build: build1F, pos: [350, 500, 1500], look: [4300, 4700, 1200], fov: 68 },
  v1_mri: { build: build1F, pos: [10400, 400, 1600], look: [12400, 4200, 900], fov: 75 },
  ax4: { build: () => buildUpper('4F'), pos: [16500, -15500, 24000], look: [11500, 3600, 0], fov: 29, cutaway: true },
  ax5: { build: () => buildUpper('5F'), pos: [16500, -15500, 24000], look: [11500, 3600, 0], fov: 29, cutaway: true },
  ax1: { build: build1F, pos: [10000, -11000, 15500], look: [6900, 3300, 0], fov: 33, cutaway: true },
  ext: { build: buildExterior, pos: null, fov: 52, exterior: true },
  ext_entry: { build: buildExterior, pos: null, fov: 44, exterior: true },
}
const V = VIEWS[VIEW]
V.build()

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true })
renderer.setSize(WPX, HPX); renderer.setPixelRatio(1)
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = V.exterior ? 0.62 : 0.72
renderer.outputColorSpace = THREE.SRGBColorSpace
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap
document.body.appendChild(renderer.domElement)
const pmrem = new THREE.PMREMGenerator(renderer)
scene.environment = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture
scene.environmentIntensity = V.exterior ? 0.6 : 0.42

if (!V.exterior) {
  scene.add(new THREE.HemisphereLight(0xfff6ea, 0xc9b08e, 0.35))
  const key = new THREE.DirectionalLight(0xfff4e6, 0.5); key.position.set(-8, 20, -14); key.castShadow = true
  key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -16, right: 16, top: 16, bottom: -16, near: 1, far: 60 }); key.shadow.bias = -0.0005
  key.target.position.set(11, 0, -4); scene.add(key, key.target)
}
if (V.cutaway) { // 天井と手前の壁を除去
  scene.traverse(o => { if (o.isMesh && o.material === M.ceil) o.visible = false; if (o.isMesh && o.material === M.light) o.visible = false })
  scene.background = new THREE.Color(0xffffff)
}

const camera = new THREE.PerspectiveCamera(V.fov, WPX / HPX, 0.05, 400)
if (V.exterior) {
  if (VIEW === 'ext') { camera.position.set(11, 1.6, 22); camera.lookAt(6.5, 9.0, 0) }
  else { camera.position.set(1.0, 1.55, 9.5); camera.lookAt(3.6, 2.3, 0) }
} else {
  const [px, py, pz] = V.pos, [lx, ly, lz] = V.look
  camera.position.set(mm(px), mm(pz), -mm(py)); camera.lookAt(mm(lx), mm(lz), -mm(ly))
}
if (V.cutaway) {
  renderer.localClippingEnabled = true
  renderer.clippingPlanes = [new THREE.Plane(new THREE.Vector3(0, -1, 0), 1.75)]
  scene.traverse(o => { if (o.isMesh && (o.material === M.sky || o.material === M.carpet)) o.visible = false })
  const f = DATA[VIEW === 'ax1' ? '1F' : VIEW === 'ax4' ? '4F' : '5F']
  const fl = new THREE.Mesh(new THREE.PlaneGeometry(mm(f.W), mm(f.D)), M.carpet); fl.rotation.x = -Math.PI / 2; fl.position.set(mm(f.W / 2), 0.002, -mm(f.D / 2)); fl.receiveShadow = true; scene.add(fl)
  if (f.core) for (const r of f.core) {
    const c = new THREE.Mesh(new THREE.PlaneGeometry(mm(r.x1 - r.x0 - 100), mm(r.y1 - r.y0 - 100)), new THREE.MeshStandardMaterial({ color: 0xdcdad6 })); c.rotation.x = -Math.PI / 2
    c.position.set(mm((r.x0 + r.x1) / 2), 0.001, -mm((r.y0 + r.y1) / 2)); scene.add(c)
  }
  scene.background = new THREE.Color(0xffffff)
}

const composer = new EffectComposer(renderer)
composer.addPass(new RenderPass(scene, camera))
const ao = new GTAOPass(scene, camera, WPX, HPX)
ao.updateGtaoMaterial({ radius: 0.45, distanceExponent: 1.5, thickness: 1.5, scale: 1.0, samples: 16 })
ao.blendIntensity = V.exterior ? 0.7 : 1.0
composer.addPass(ao)
composer.addPass(new OutputPass())
composer.addPass(new SMAAPass(WPX, HPX))
composer.render()
window.__done = true
