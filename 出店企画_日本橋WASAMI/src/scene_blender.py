"""内装・外装イメージ（Blender Cycles によるフォトリアル・レンダリング）

usage: python scene_blender.py <view> <out.png> [samples] [width] [height]
  （bpy 5.x を pip で導入した Python で実行。平面データは build/floors.json）
座標：平面図と同じ（x=道路側→奥, y=コア側→X1側, mm）を m に換算、Z=高さ
"""
import bpy, bmesh, json, math, os, sys, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "build", "floors.json")))
LOGO_FONT = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
NAVY = (0.141, 0.255, 0.561)
rnd = random.Random(7)
m = lambda v: v / 1000.0

# ====================================================================== scene setup
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.015
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.max_bounces = 8
    sc.cycles.diffuse_bounces = 4
    sc.cycles.glossy_bounces = 3
    sc.cycles.transmission_bounces = 6
    sc.cycles.sample_clamp_indirect = 8
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Punchy"
    except Exception:
        pass
    sc.render.film_transparent = False
    return sc


# ====================================================================== materials
MATS = {}


def principled(name, color, rough=0.5, metal=0.0, spec=0.5, **kw):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k, v in kw.items():
        b.inputs[k].default_value = v
    MATS[name] = mat
    return mat


def node(mat, typ, **props):
    n = mat.node_tree.nodes.new(typ)
    for k, v in props.items():
        setattr(n, k, v)
    return n


def link(mat, a, b):
    mat.node_tree.links.new(a, b)


def mat_carpet():
    mat = principled("carpet", (0.62, 0.52, 0.38), rough=1.0)
    b = mat.node_tree.nodes["Principled BSDF"]
    tc = node(mat, "ShaderNodeTexCoord")
    # 細かなループ（パイル）
    n1 = node(mat, "ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 900; n1.inputs["Detail"].default_value = 2
    # 葉脈状の大柄（銀座院のカーペット柄）
    n2 = node(mat, "ShaderNodeTexWave"); n2.wave_type = "BANDS"; n2.inputs["Scale"].default_value = 3.5
    n2.inputs["Distortion"].default_value = 9; n2.inputs["Detail"].default_value = 3; n2.inputs["Detail Scale"].default_value = 1.2
    n3 = node(mat, "ShaderNodeTexNoise"); n3.inputs["Scale"].default_value = 3.0
    for n in (n1, n2, n3):
        link(mat, tc.outputs["Object"], n.inputs["Vector"])
    ramp = node(mat, "ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[0].color = (0.50, 0.41, 0.29, 1)
    ramp.color_ramp.elements[1].position = 0.75; ramp.color_ramp.elements[1].color = (0.70, 0.60, 0.45, 1)
    mix = node(mat, "ShaderNodeMix"); mix.data_type = "FLOAT"; mix.inputs[0].default_value = 0.12
    link(mat, n1.outputs["Fac"], mix.inputs[2]); link(mat, n2.outputs["Fac"], mix.inputs[3])
    link(mat, mix.outputs[0], ramp.inputs["Fac"])
    link(mat, ramp.outputs["Color"], b.inputs["Base Color"])
    bump = node(mat, "ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.35; bump.inputs["Distance"].default_value = 0.002
    link(mat, n1.outputs["Fac"], bump.inputs["Height"]); link(mat, bump.outputs["Normal"], b.inputs["Normal"])
    return mat


def mat_plaster(name="plaster", color=(0.80, 0.77, 0.72)):
    mat = principled(name, color, rough=0.85)
    b = mat.node_tree.nodes["Principled BSDF"]
    tc = node(mat, "ShaderNodeTexCoord")
    n = node(mat, "ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 14; n.inputs["Detail"].default_value = 8; n.inputs["Roughness"].default_value = 0.6
    link(mat, tc.outputs["Object"], n.inputs["Vector"])
    ramp = node(mat, "ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (color[0] * 0.95, color[1] * 0.95, color[2] * 0.95, 1)
    ramp.color_ramp.elements[1].color = (min(1, color[0] * 1.04), min(1, color[1] * 1.04), min(1, color[2] * 1.04), 1)
    link(mat, n.outputs["Fac"], ramp.inputs["Fac"]); link(mat, ramp.outputs["Color"], b.inputs["Base Color"])
    bump = node(mat, "ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08
    link(mat, n.outputs["Fac"], bump.inputs["Height"]); link(mat, bump.outputs["Normal"], b.inputs["Normal"])
    return mat


def mat_wood(name, light, dark, rough=0.45, scale=6.0, vertical=True):
    mat = principled(name, light, rough=rough)
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Coat Weight"].default_value = 0.15
    tc = node(mat, "ShaderNodeTexCoord")
    mp = node(mat, "ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1, 1, 22) if vertical else (22, 1, 1)
    link(mat, tc.outputs["Object"], mp.inputs["Vector"])
    nz = node(mat, "ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3; nz.inputs["Detail"].default_value = 6
    link(mat, mp.outputs["Vector"], nz.inputs["Vector"])
    wv = node(mat, "ShaderNodeTexWave"); wv.inputs["Scale"].default_value = scale; wv.inputs["Distortion"].default_value = 6
    wv.inputs["Detail"].default_value = 4; wv.bands_direction = "Z" if vertical else "X"
    link(mat, mp.outputs["Vector"], wv.inputs["Vector"])
    ramp = node(mat, "ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*dark, 1); ramp.color_ramp.elements[1].color = (*light, 1)
    ramp.color_ramp.elements[0].position = 0.2; ramp.color_ramp.elements[1].position = 0.85
    link(mat, wv.outputs["Fac"], ramp.inputs["Fac"]); link(mat, ramp.outputs["Color"], b.inputs["Base Color"])
    bump = node(mat, "ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.05
    link(mat, wv.outputs["Fac"], bump.inputs["Height"]); link(mat, bump.outputs["Normal"], b.inputs["Normal"])
    return mat


def mat_fabric(name, color):
    mat = principled(name, color, rough=0.95)
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Sheen Weight"].default_value = 0.15
    b.inputs["Sheen Tint"].default_value = (1, 1, 1, 1)
    tc = node(mat, "ShaderNodeTexCoord")
    n = node(mat, "ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 400
    link(mat, tc.outputs["Object"], n.inputs["Vector"])
    bump = node(mat, "ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.15
    link(mat, n.outputs["Fac"], bump.inputs["Height"]); link(mat, bump.outputs["Normal"], b.inputs["Normal"])
    return mat


def mat_emit(name, color, strength):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (*color, 1); e.inputs["Strength"].default_value = strength
    nt.links.new(e.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    MATS[name] = mat
    return mat


def mat_glass(name="glass", tint=(0.92, 0.96, 0.97), rough=0.0):
    mat = principled(name, tint, rough=rough)
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Transmission Weight"].default_value = 1.0
    b.inputs["IOR"].default_value = 1.45
    return mat


def mat_image(name, path, rough=0.8, emission=0.0):
    mat = principled(name, (1, 1, 1), rough=rough)
    b = mat.node_tree.nodes["Principled BSDF"]
    tex = node(mat, "ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path)
    tex.extension = "CLIP"
    link(mat, tex.outputs["Color"], b.inputs["Base Color"])
    if emission:
        link(mat, tex.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emission
    return mat


def make_logo_png(path, bg, fg, w=1600, h=800, size=330, sub=None, texture=False):
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    im = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(im)
    if texture:  # 白い塗り壁の左官テクスチャ
        r = random.Random(3)
        for _ in range(900):
            x, y = r.randrange(w), r.randrange(h)
            c = tuple(max(0, v - r.randrange(4, 12)) for v in bg)
            d.arc([x, y, x + r.randrange(40, 180), y + r.randrange(20, 90)], r.randrange(0, 180), r.randrange(180, 360), fill=c, width=2)
        im = im.filter(ImageFilter.GaussianBlur(1.2))
        d = ImageDraw.Draw(im)
    f = ImageFont.truetype(LOGO_FONT, size)
    tw = d.textlength("fukka", font=f)
    d.text(((w - tw) / 2, h / 2 - size * 0.62), "fukka", font=f, fill=fg)
    if sub:
        f2 = ImageFont.truetype(LOGO_FONT, int(size * 0.2))
        tw2 = d.textlength(sub, font=f2)
        d.text(((w - tw2) / 2, h / 2 + size * 0.45), sub, font=f2, fill=fg)
    im.save(path)
    return path


def init_materials(tmpdir):
    mat_carpet()
    mat_plaster("plaster")
    mat_plaster("ceiling", (0.86, 0.85, 0.83))
    mat_wood("oak", (0.50, 0.33, 0.19), (0.28, 0.17, 0.09))
    mat_wood("oakH", (0.50, 0.33, 0.19), (0.28, 0.17, 0.09), vertical=False)
    mat_wood("walnut", (0.24, 0.14, 0.08), (0.14, 0.08, 0.045), rough=0.4)
    mat_wood("door", (0.44, 0.31, 0.19), (0.26, 0.17, 0.10), rough=0.5)
    mat_wood("leg", (0.70, 0.52, 0.33), (0.58, 0.41, 0.25), rough=0.5)
    mat_fabric("fabric", (0.36, 0.31, 0.25))
    mat_fabric("fabric2", (0.33, 0.29, 0.24))
    mat_fabric("bedcover", (0.86, 0.83, 0.78))
    mat_fabric("towel", (0.78, 0.70, 0.58))
    principled("white", (0.86, 0.85, 0.83), rough=0.35)
    principled("top", (0.90, 0.89, 0.87), rough=0.15, **{"Coat Weight": 0.3})
    principled("metal", (0.75, 0.75, 0.74), rough=0.28, metal=1.0)
    principled("steel", (0.55, 0.56, 0.57), rough=0.35, metal=1.0)
    principled("dark", (0.03, 0.03, 0.035), rough=0.3)
    principled("screen", (0.01, 0.012, 0.02), rough=0.08)
    principled("mri", (0.85, 0.86, 0.87), rough=0.2, **{"Coat Weight": 0.5})
    principled("mriblue", (0.30, 0.45, 0.62), rough=0.3)
    principled("pot", (0.72, 0.69, 0.64), rough=0.7)
    principled("soil", (0.08, 0.06, 0.04), rough=1)
    principled("baseboard", (0.80, 0.78, 0.74), rough=0.5)
    principled("vinyl", (0.66, 0.63, 0.58), rough=0.35)
    principled("rug", (0.32, 0.27, 0.21), rough=1)
    mat_glass("glass")
    mat_glass("frosted", (0.95, 0.95, 0.95), rough=0.35)
    leaf = principled("leaf", (0.10, 0.22, 0.07), rough=0.45)
    leaf.node_tree.nodes["Principled BSDF"].inputs["Subsurface Weight"].default_value = 0.2
    mat_emit("led", (1.0, 0.93, 0.82), 12.0)
    mat_emit("led_soft", (1.0, 0.90, 0.75), 4.0)
    mat_image("logo_wall", make_logo_png(os.path.join(tmpdir, "logo_wall.png"), (236, 232, 225), (36, 65, 143), 1000, 1600, 230, texture=True), rough=0.85)
    mat_image("logo_small", make_logo_png(os.path.join(tmpdir, "logo_small.png"), (243, 238, 229), (36, 65, 143), 1200, 400, 240))
    mat_image("logo_wood", make_logo_png(os.path.join(tmpdir, "logo_wood.png"), (160, 120, 80), (246, 238, 222), 1200, 400, 240), rough=0.5)
    mat_image("logo_s1", make_logo_png(os.path.join(tmpdir, "logo_s1.png"), (246, 244, 239), (36, 65, 143), 1160, 470, 230), emission=0.6)


# ====================================================================== geometry helpers
COL = None


def add_obj(name, bm, mat, bevel=0.0):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    COL.objects.link(ob)
    if mat:
        ob.data.materials.append(MATS[mat] if isinstance(mat, str) else mat)
    if bevel:
        mod = ob.modifiers.new("bev", "BEVEL"); mod.width = bevel; mod.segments = 3; mod.limit_method = "ANGLE"
    for p in ob.data.polygons:
        p.use_smooth = bevel > 0
    return ob


def box(name, sx, sy, sz, x, y, z, mat, rot=0.0, bevel=0.0):
    """中心(x,y)・底面z（m）"""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= sx; v.co.y *= sy; v.co.z = (v.co.z + 0.5) * sz
    ob = add_obj(name, bm, mat, bevel)
    ob.location = (x, y, z); ob.rotation_euler = (0, 0, rot)
    return ob


def cyl(name, r, h, x, y, z, mat, seg=48, r2=None, rot=(0, 0, 0), bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts:
        v.co.z += h / 2
    ob = add_obj(name, bm, mat, bevel)
    ob.location = (x, y, z); ob.rotation_euler = rot
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def plane(name, sx, sy, x, y, z, mat, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    for v in bm.verts:
        v.co.x *= sx; v.co.y *= sy
    ob = add_obj(name, bm, mat)
    ob.location = (x, y, z); ob.rotation_euler = rot
    # UV
    me = ob.data
    uv = me.uv_layers.new()
    for poly in me.polygons:
        for li in poly.loop_indices:
            vco = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (vco.x / sx + 0.5, vco.y / sy + 0.5)
    return ob


def arc_ring(name, cx, cy, r_out, r_in, a0, a1, z0, h, mat, seg=72):
    bm = bmesh.new()
    pts = []
    for i in range(seg + 1):
        a = math.radians(a0 + (a1 - a0) * i / seg)
        pts.append((math.cos(a), math.sin(a)))
    vo = [bm.verts.new((cx + r_out * c, cy + r_out * s_, z0)) for c, s_ in pts]
    vi = [bm.verts.new((cx + r_in * c, cy + r_in * s_, z0)) for c, s_ in pts]
    for i in range(seg):
        bm.faces.new((vo[i], vo[i + 1], vi[i + 1], vi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    geom = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    for v in [e for e in geom["geom"] if isinstance(e, bmesh.types.BMVert)]:
        v.co.z += h
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = add_obj(name, bm, mat, bevel=0.006)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def wall(x0, y0, x1, y1, h, t=100, mat="plaster", openings=(), base=0, name="wall"):
    """平面座標(mm)。openings: [(a,b,bottom,top)] 区間は始点からの距離 mm"""
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 1:
        return
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    ang = math.atan2(y1 - y0, x1 - x0)

    def piece(s0, s1, z0, z1):
        if s1 - s0 < 1 or z1 - z0 < 1:
            return
        cx, cy = x0 + ux * (s0 + s1) / 2, y0 + uy * (s0 + s1) / 2
        box(name, m(s1 - s0), m(t), m(z1 - z0), m(cx), m(cy), m(base + z0), mat, rot=ang)
    s = 0
    for a, b, bot, top in sorted(openings):
        piece(s, a, 0, h)
        piece(a, b, top, h)
        if bot:
            piece(a, b, 0, bot)
        s = b
    piece(s, L, 0, h)


def area_light(name, x, y, z, sx, sy, power, color=(1.0, 0.92, 0.82), rot=(0, 0, 0)):
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape = "RECTANGLE"; ld.size = sx; ld.size_y = sy; ld.energy = power; ld.color = color
    ob = bpy.data.objects.new(name, ld); COL.objects.link(ob)
    ob.location = (x, y, z); ob.rotation_euler = rot
    return ob


def spot(name, x, y, z, power, angle=60, color=(1.0, 0.88, 0.72), target=None, radius=0.03):
    ld = bpy.data.lights.new(name, "SPOT")
    ld.energy = power; ld.spot_size = math.radians(angle); ld.spot_blend = 0.6; ld.color = color
    ld.shadow_soft_size = radius
    ob = bpy.data.objects.new(name, ld); COL.objects.link(ob)
    ob.location = (x, y, z)
    if target:
        d = Vector(target) - Vector((x, y, z))
        ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return ob


# ====================================================================== furniture
def chair(x, y, face_deg):
    """face_deg：座面の向き（0=+x, 90=+y）。x,y mm"""
    g = []
    rot = math.radians(face_deg)
    def local(dx, dy):  # 座の前方向 = +dx
        return m(x) + dx * math.cos(rot) - dy * math.sin(rot), m(y) + dx * math.sin(rot) + dy * math.cos(rot)
    for dx, dy, sx, sy, sz, z in [(0.0, 0, 0.58, 0.62, 0.19, 0.27),        # 座ベース
                                   (0.04, 0, 0.46, 0.46, 0.07, 0.462),    # 座クッション
                                   (-0.235, 0, 0.11, 0.62, 0.42, 0.462),  # 背
                                   (0.055, 0.27, 0.47, 0.08, 0.21, 0.462),   # 肘
                                   (0.055, -0.27, 0.47, 0.08, 0.21, 0.462)]:
        px, py = local(dx, dy)
        box("chair", sx, sy, sz, px, py, z, "fabric", rot=rot, bevel=0.02)
    for dx in (-0.23, 0.23):
        for dy in (-0.25, 0.25):
            px, py = local(dx, dy)
            cyl("leg", 0.018, 0.27, px, py, 0, "leg", seg=12, r2=0.014)


def bed(cx, cy, along_x=False):
    """施術ベッド 700×1900（中心 mm）"""
    rot = 0 if not along_x else math.pi / 2
    box("bedbase", 0.60, 1.78, 0.50, m(cx), m(cy), 0, "oak", rot=rot, bevel=0.01)
    box("bedtop", 0.70, 1.90, 0.12, m(cx), m(cy), 0.50, "bedcover", rot=rot, bevel=0.04)
    o = (0, -0.72) if not along_x else (-0.72, 0)
    box("pillow", 0.48, 0.30, 0.08, m(cx) + o[0], m(cy) + o[1], 0.62, "white", rot=rot, bevel=0.035)
    o2 = (0, 0.42) if not along_x else (0.42, 0)
    box("towel", 0.72, 0.55, 0.012, m(cx) + o2[0], m(cy) + o2[1], 0.62, "towel", rot=rot, bevel=0.004)


def stool(x, y):
    cyl("stool", 0.19, 0.06, m(x), m(y), 0.46, "fabric2", bevel=0.01)
    cyl("stleg", 0.022, 0.46, m(x), m(y), 0, "metal", seg=16)
    cyl("stbase", 0.2, 0.015, m(x), m(y), 0, "metal")


def plant(x, y, h=1.3, pot=0.36):
    cyl("pot", pot / 2, 0.42, m(x), m(y), 0, "pot", r2=pot / 2 * 0.8, bevel=0.01)
    cyl("soil", pot / 2 * 0.95, 0.01, m(x), m(y), 0.41, "soil")
    r = random.Random(int(x + y))
    for i in range(int(36 * h)):
        z = 0.5 + r.random() * h
        a = r.random() * 6.28
        rr = 0.05 + r.random() * 0.25 * (1 - (z - 0.5) / h * 0.4)
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=1)
        for v in bm.verts:
            v.co.x *= 0.13; v.co.y *= 0.06; v.co.z *= 0.012
        ob = add_obj("leaf", bm, "leaf")
        ob.location = (m(x) + math.cos(a) * rr, m(y) + math.sin(a) * rr, z)
        ob.rotation_euler = (r.uniform(-0.6, 0.6), r.uniform(-0.6, 0.6), a)
        for p in ob.data.polygons:
            p.use_smooth = True
    cyl("stem", 0.012, h * 0.85, m(x), m(y), 0.42, "walnut", seg=8)


def sliding_door(side, r, d, h=2100):
    w = d["w"]; at = d["at"]
    if side in ("S", "N"):
        yy = r["y0"] if side == "S" else r["y1"]
        off = -60 if side == "S" else 60
        box("door", m(w + 60), 0.035, m(h), m(at), m(yy + off), 0, "door", bevel=0.003)
        for sgn in (1, -1):
            box("handle", 0.02, 0.025, 0.45, m(at + w / 2 - 70), m(yy + off + sgn * 30), 0.85, "steel", bevel=0.004)
        box("frame", m(w + 120), 0.12, 0.04, m(at), m(yy), m(h), "white")
        box("plate", 0.16, 0.006, 0.07, m(at - w / 2 + 160), m(yy + off * 1.4), 1.45, "white", bevel=0.002)
    else:
        xx = r["x0"] if side == "W" else r["x1"]
        off = -60 if side == "W" else 60
        box("door", 0.035, m(w + 60), m(h), m(xx + off), m(at), 0, "door", bevel=0.003)
        for sgn in (1, -1):
            box("handle", 0.025, 0.02, 0.45, m(xx + off + sgn * 30), m(at + w / 2 - 70), 0.85, "steel", bevel=0.004)
        box("frame", 0.12, m(w + 120), 0.04, m(xx), m(at), m(h), "white")


def swing_door(side, r, d, h=2100, mat="door"):
    w = d["w"]; at = d["at"]
    if side in ("S", "N"):
        yy = r["y0"] if side == "S" else r["y1"]
        box("door", m(w), 0.045, m(h), m(at), m(yy), 0, mat, bevel=0.003)
        box("lever", 0.12, 0.02, 0.02, m(at + w / 2 - 120), m(yy) + (0.04 if side == "S" else -0.04), 1.0, "steel")
    else:
        xx = r["x0"] if side == "W" else r["x1"]
        box("door", 0.045, m(w), m(h), m(xx), m(at), 0, mat, bevel=0.003)
        box("lever", 0.02, 0.12, 0.02, m(xx) + (0.04 if side == "E" else -0.04), m(at + w / 2 - 120), 1.0, "steel")


# ====================================================================== rooms / walls
def room_walls(f, H, cut=None, ch=None):
    """間仕切壁：同一線上の壁を統合して1回だけ作る（重複面による黒斑を防ぐ）"""
    hh = lambda h: min(h, cut) if cut else h
    lines = {}   # (axis, coord) -> list of [a, b, height]
    ops = {}     # (axis, coord) -> list of (a, b, bottom, top)  絶対座標
    for r in f["rooms"]:
        if r["kind"] in ("open", "existing", "hall"):
            continue
        x0, y0, x1, y1 = r["x0"], r["y0"], r["x1"], r["y1"]
        h = (ch or 2800) if r["kind"] == "mri" else H
        for k, key, a, b in (("S", ("H", y0), x0, x1), ("N", ("H", y1), x0, x1), ("W", ("V", x0), y0, y1), ("E", ("V", x1), y0, y1)):
            if (k == "S" and y0 <= 0) or (k == "N" and y1 >= f["D"]) or (k == "W" and x0 <= 0) or (k == "E" and x1 >= f["W"]):
                continue
            lines.setdefault(key, []).append([a, b, h])
        for dd in r["doors"]:
            sd = dd["side"]
            key = ("H", y0 if sd == "S" else y1) if sd in ("S", "N") else ("V", x0 if sd == "W" else x1)
            ops.setdefault(key, []).append((dd["at"] - dd["w"] / 2, dd["at"] + dd["w"] / 2, 0, 2100))
        for w in r.get("windows", []):
            key = ("V", x1 if w["side"] == "E" else x0)
            ops.setdefault(key, []).append((w["a"], w["b"], 900, 2100))
    for key, segs in lines.items():
        segs.sort()
        merged = []
        for a, b, h in segs:
            if merged and a <= merged[-1][1] + 1:
                merged[-1][1] = max(merged[-1][1], b); merged[-1][2] = max(merged[-1][2], h)
            else:
                merged.append([a, b, h])
        axis, c = key
        for a, b, h in merged:
            hz = hh(h)
            o = [(oa - a, ob - a, bot, min(top, hz)) for oa, ob, bot, top in ops.get(key, []) if oa >= a - 1 and ob <= b + 1]
            if axis == "H":
                wall(a, c, b, c, hz, 100, "plaster", o)
            else:
                wall(c, a, c, b, hz, 100, "plaster", o)
    if not cut:
        for r in f["rooms"]:
            for dd in r["doors"]:
                (sliding_door if dd["type"] == "slide" else swing_door)(dd["side"], r, dd)
            for w in r.get("windows", []):
                xx = r["x1"] if w["side"] == "E" else r["x0"]
                box("obs_glass", 0.012, m(w["b"] - w["a"]), 1.2, m(xx), m((w["a"] + w["b"]) / 2), 0.9, "glass")
                for z in (0.9, 2.1):
                    box("obs_frame", 0.12, m(w["b"] - w["a"] + 60), 0.04, m(xx), m((w["a"] + w["b"]) / 2), z - 0.02, "white")


def linear_light(x0, y0, x1, y1, z, power_per_m=55):
    L = math.hypot(m(x1 - x0), m(y1 - y0))
    ang = math.atan2(y1 - y0, x1 - x0)
    cx, cy = m((x0 + x1) / 2), m((y0 + y1) / 2)
    box("ledbody", L + 0.04, 0.10, 0.015, cx, cy, z - 0.012, "white", rot=ang)
    box("led", L, 0.07, 0.004, cx, cy, z - 0.016, "led", rot=ang)
    area_light("ledA", cx, cy, z - 0.02, L, 0.08, power_per_m * L, rot=(0, 0, ang))


def downlight(x, y, z, power=25, target=None):
    cyl("dl", 0.05, 0.004, m(x), m(y), z - 0.004, "led", seg=24)
    spot("dlS", m(x), m(y), z - 0.01, power, 70, target=target or (m(x), m(y), 0))


def baseboards(f):
    pass


# ====================================================================== reception（銀座院同型）
def reception(f, rc, ch, ring=True):
    cx, cy, r = m(rc["cx"]), m(rc["cy"]), m(rc["r"])
    a0, a1 = rc["a0"], rc["a1"]
    arc_ring("counter", cx, cy, r, r - 0.05, a0, a1, 0.0, 1.0, "oakH")
    arc_ring("counter_in", cx, cy, r - 0.05, r - 0.45, a0, a1, 0.0, 0.72, "white")
    arc_ring("countertop", cx, cy, r + 0.03, r - 0.6, a0 - 1, a1 + 1, 1.0, 0.035, "top")
    arc_ring("counter_kick", cx, cy, r - 0.02, r - 0.07, a0, a1, 0.0, 0.08, "walnut")
    mid = math.radians((a0 + a1) / 2)
    for k in (-0.62, 0.62):
        a = mid + k
        px, py = cx + (r - 0.35) * math.cos(a), cy + (r - 0.35) * math.sin(a)
        box("monitor", 0.48, 0.03, 0.30, px, py, 1.12, "screen", rot=a + math.pi / 2, bevel=0.005)
        box("monarm", 0.04, 0.04, 0.1, px - 0.03 * math.cos(a), py - 0.03 * math.sin(a), 1.035, "steel", rot=a)
    for k in (-0.6, 0.6):
        a = mid + k
        stool(rc["cx"] + (rc["r"] - 900) * math.cos(a), rc["cy"] + (rc["r"] - 900) * math.sin(a))
    # 背面：収納棚＋木の斜めパネル＋白い塗り壁ロゴ
    bx0, by0, bx1, by1 = rc["back"]
    horiz = (bx1 - bx0) > (by1 - by0)
    L = m(bx1 - bx0) if horiz else m(by1 - by0)
    D = m(by1 - by0) if horiz else m(bx1 - bx0)
    Hh = 2.45
    # 正面方向（カウンター側）の単位ベクトル
    if horiz:
        n = (0, -1 if rc["cy"] < by0 else 1)
    else:
        n = (-1 if rc["cx"] < bx0 else 1, 0)
    rot = math.atan2(n[0], -n[1])          # 板の法線（-Y局所）を正面方向 n に向ける
    t = (math.cos(rot), math.sin(rot))
    gx, gy = m((bx0 + bx1) / 2), m((by0 + by1) / 2)
    box("backwall", L, D, Hh, gx, gy, 0, "plaster", rot=rot)
    def P(u, v):  # u: 壁沿い, v: 正面方向
        return gx + t[0] * u + n[0] * v, gy + t[1] * u + n[1] * v
    # 左：升目の収納棚（木）
    sw = L * 0.34
    u0 = -L / 2 + sw / 2
    px, py = P(u0, D / 2 + 0.16)
    box("shelf_back", sw, 0.02, Hh - 0.1, *P(u0, D / 2 + 0.01), 0.05, "oak", rot=rot)
    for i in range(6):
        box("shelf", sw, 0.30, 0.025, *P(u0, D / 2 + 0.16), 0.08 + i * 0.46, "oak", rot=rot)
    for j in range(3):
        box("shelfv", 0.025, 0.30, Hh - 0.1, *P(-L / 2 + j * sw / 2 + 0.012, D / 2 + 0.16), 0.05, "oak", rot=rot)
    # 中：斜めの木パネル
    box("woodpanel", L * 0.2, 0.06, Hh, *P(-L / 2 + sw + L * 0.12, D / 2 + 0.06), 0, "oak", rot=rot + 0.15, bevel=0.005)
    # 右：ロゴ壁
    lw = L * 0.40
    ob = plane("logo_wall", lw, Hh - 0.08, *P(L / 2 - lw / 2 - 0.02, D / 2 + 0.006), Hh / 2, "logo_wall",
               rot=(math.pi / 2, 0, rot))
    # 天井：木の円形リング＋間接照明＋ダウンライト
    R = r + 0.55
    cyl("rug", R + 0.2, 0.006, cx, cy, 0.0, "rug", seg=128)
    if not ring:
        return
    arc_ring("ring", cx, cy, R, R - 0.04, 0, 360, ch - 0.34, 0.34, "walnut", seg=128)
    arc_ring("ring_soffit", cx, cy, R - 0.04, 0.001, 0, 360, ch - 0.35, 0.012, "ceiling", seg=128)
    arc_ring("ring_glow", cx, cy, R + 0.002, R - 0.01, 0, 360, ch - 0.352, 0.004, "led_soft", seg=128)
    for i in range(8):
        a = math.radians(a0 + (a1 - a0) * (i + 0.5) / 8)
        downlight(m(1000) * 0 + (rc["cx"] + (rc["r"] * 0.8) * math.cos(a)), rc["cy"] + (rc["r"] * 0.8) * math.sin(a), ch - 0.35, 35)
    for (u, v) in ((-L * 0.3, 0.6), (L * 0.25, 0.6)):
        px, py = P(u, v)
        spot("wallwash", px, py, ch - 0.36, 40, 50, target=(px - n[0] * 0.55, py - n[1] * 0.55, 1.4))


# ====================================================================== floors
def build_upper(key, cut=None):
    f = DATA[key]
    W, D, CH = f["W"], f["D"], m(f["ch"])
    H = f["partition_h"]
    hh = (lambda h: min(h, cut)) if cut else (lambda h: h)
    # 床
    plane("floor", m(W + 1000), m(D + 1000), m(W / 2), m(D / 2), 0, "carpet")
    e0, e1, ed = f["evh"]
    plane("evfloor", m(e1 - e0), m(-ed), m((e0 + e1) / 2), m(ed / 2), 0.001, "vinyl")
    if not cut:
        plane("ceiling", m(W + 1000), m(D + 6000), m(W / 2), m(D / 2 - 2500), CH, "ceiling", rot=(math.pi, 0, 0))
    # 外周：道路側（窓）、X1側（窓なし・柱型）、奥、コア側
    ch_mm = f["ch"]
    wops = []
    s = 400
    while s < D - 300:
        wops.append((s, min(s + 2500, D - 100), 700, 2550)); s += 2900
    wall(-150, -100, -150, D + 250, hh(ch_mm), 300, "plaster", [(a + 100, b + 100, bb, min(tt, hh(ch_mm))) for a, b, bb, tt in wops])
    for a, b, bb, tt in wops:
        box("mullion", 0.05, m(b - a), 0.05, -0.12, m((a + b) / 2), m(bb), "steel")
        box("win_glass", 0.012, m(b - a), m(tt - bb), -0.2, m((a + b) / 2), m(bb), "glass")
        if not cut:
            box("rollscreen", 0.02, m(b - a), 0.35, -0.03, m((a + b) / 2), m(tt) - 0.35, "frosted")
    wall(-300, D + 150, W + 300, D + 150, hh(ch_mm), 300, "plaster")
    for c, _ in f["columns"]:
        box("column", 0.8, 0.45, hh(CH * 1000) / 1000, m(c), m(D - 175), 0, "plaster")
    wall(W + 150, D + 250, W + 150, -100, hh(ch_mm), 300, "plaster")
    sd, td = f["stair_door"], f["toilet_door"]
    wall(-300, -50, e0, -50, hh(ch_mm), 100, "plaster", [(sd[0] + 300, sd[1] + 300, 0, min(2100, hh(ch_mm)))])
    wall(e1, -50, W + 300, -50, hh(ch_mm), 100, "plaster", [(td[0] - e1, td[1] - e1, 0, min(2100, hh(ch_mm)))])
    if not cut:
        swing_door("S", dict(y0=-50, x0=0, x1=0, y1=0), dict(at=(sd[0] + sd[1]) / 2, w=sd[1] - sd[0]), mat="steel")
        swing_door("S", dict(y0=-50, x0=0, x1=0, y1=0), dict(at=(td[0] + td[1]) / 2, w=td[1] - td[0]), mat="steel")
        box("sign_wc", 0.2, 0.01, 0.2, m((td[0] + td[1]) / 2), -0.0, 2.25, "white")
    # EVホール
    wall(e0, -50, e0, ed, hh(ch_mm), 100, "plaster"); wall(e1, -50, e1, ed, hh(ch_mm), 100, "plaster")
    wall(e0, ed, e1, ed, hh(ch_mm), 100, "plaster")
    if not cut:
        for yy in (ed / 2 - 900, ed / 2 + 900):
            box("evdoor", 0.04, 0.95, 2.1, m(e0) + 0.05, m(yy), 0, "steel")
        plane("evceil", m(e1 - e0), m(-ed), m((e0 + e1) / 2), m(ed / 2), 2.6, "ceiling", rot=(math.pi, 0, 0))
        box("firedoor_frame", m(e1 - e0), 0.12, 0.25, m((e0 + e1) / 2), -0.05, 2.55, "plaster")
    # 既設カウンターキッチン（5Fは物品庫内）
    # 間仕切・建具
    room_walls(f, H, cut=cut, ch=ch_mm)
    for r in f["rooms"]:
        if r["kind"] == "treat":
            treat_furnish(r, cut)
    if f.get("reception"):
        reception(f, f["reception"], CH, ring=not cut)
    for x, y, rot in f.get("chairs", []):
        face = {180: 0, 0: 180, 90: 270, 270: 90}[rot]
        chair(x, y, face)
    for (px, py) in f.get("plants", []):
        plant(px, py, 1.25)
    for r in f["rooms"]:
        if r["id"] in ("lm", "lw", "slm", "slw"):
            lockers(r)
        if r["id"] == "sr":
            staff_room(r)
        if r["id"] == "dk":
            box("kitchen", m(2400), 0.6, 0.86, m(17650), 0.35, 0, "white", bevel=0.005)
            box("kitchentop", m(2400), 0.62, 0.03, m(17650), 0.35, 0.86, "top")
            box("server", 0.33, 0.36, 1.15, m(16700), 0.3, 0, "white", bevel=0.02)
        if r["id"] == "cs":
            box("table", 0.9, 0.7, 0.72, m((r["x0"] + r["x1"]) / 2), m(1100), 0, "oakH", bevel=0.005)
    if f.get("lounge"):
        lounge(f["lounge"])
    # TV（銀座院同様）
    # 照明
    if not cut:
        z = CH
        for r in f["rooms"]:
            if r["kind"] == "treat":
                linear_light(r["x0"] + 500, (r["y0"] + r["y1"]) / 2, r["x1"] - 500, (r["y0"] + r["y1"]) / 2, z, 45)
            elif r["kind"] in ("room", "service"):
                linear_light(r["x0"] + 400, (r["y0"] + r["y1"]) / 2, r["x1"] - 400, (r["y0"] + r["y1"]) / 2, z, 45)
        linear_light(300, 5500, W - 300, 5500, z, 40)
        for y in (700, 2300):
            linear_light(6000, y, 8300, y, z, 45); linear_light(11900, y, 14800, y, z, 45)
        linear_light(2300, 650, 5400 if key == "4F" else 7400, 650, z, 45)
        linear_light(15800, 400, 15800, 4500, z, 40)
        if key == "5F":
            for y in (1200, 3400):
                linear_light(8200, y, 14600, y, z, 50)
        # 道路側の昼光
        sun_world(strength=0.35)


def treat_furnish(r, cut):
    x0, y0, x1, y1 = r["x0"], r["y0"], r["x1"], r["y1"]
    if (y1 - y0) > (x1 - x0) - 100:
        bed((x0 + x1) / 2 - 250, (y0 + y1) / 2 + 150)
        stool(x1 - 380, y0 + 700)
        box("basket", 0.42, 0.34, 0.24, m(x1 - 300), m(y1 - 300), 0, "oak", bevel=0.01)
    else:
        bed(x0 + 1275, y1 - 650, along_x=True)
        stool(x1 - 420, y1 - 1500)
        box("wagon", 0.42, 0.42, 0.75, m(x0 + 360), m(y0 + 360), 0, "oak", bevel=0.008)
        box("wagontop", 0.44, 0.44, 0.02, m(x0 + 360), m(y0 + 360), 0.75, "top")
        box("basket", 0.42, 0.34, 0.24, m(x1 - 300), m(y0 + 300), 0, "oak", bevel=0.01)
    if not cut:
        box("hookshelf", 0.6, 0.2, 0.025, m((x0 + x1) / 2 + 400), m(y1 - 110), 1.6, "oak")
        for k in range(3):
            cyl("hook", 0.01, 0.05, m((x0 + x1) / 2 + 200 + k * 200), m(y1 - 25), 1.5, "steel", rot=(math.pi / 2, 0, 0))


def lockers(r):
    x0, y0, x1, y1 = r["x0"], r["y0"], r["x1"], r["y1"]
    if (x1 - x0) < (y1 - y0) or r["id"] in ("slm", "slw"):
        n = int((y1 - y0 - 600) / 450)
        for i in range(n):
            box("locker", 0.45, 0.43, 1.8, m(x0 + 280), m(y0 + 450 + i * 450), 0, "oak", bevel=0.004)
    else:
        n = int((x1 - x0 - 300) / 450)
        for i in range(n):
            box("locker", 0.43, 0.45, 1.8, m(x0 + 350 + i * 450), m(y1 - 280), 0, "oak", bevel=0.004)
        box("vanity", 1.6, 0.5, 0.75, m(x1 - 900), m(y0 + 300), 0, "white", bevel=0.005)
        box("mirror", 1.5, 0.01, 0.8, m(x1 - 900), m(y0 + 60), 1.1, "metal")
    box("bench", 1.0, 0.38, 0.42, m((x0 + x1) / 2 + 200), m((y0 + y1) / 2), 0, "fabric", rot=math.pi / 2 if (x1 - x0) < (y1 - y0) else 0, bevel=0.02)


def staff_room(r):
    x0, y0, x1, y1 = r["x0"], r["y0"], r["x1"], r["y1"]
    box("table", 2.0, 0.9, 0.72, m((x0 + x1) / 2), m((y0 + y1) / 2 - 200), 0, "oakH", bevel=0.006)
    for dx in (-0.6, 0.0, 0.6):
        for dy, face in ((-0.75, 90), (0.35, 270)):
            chair((x0 + x1) / 2 + dx * 1000, (y0 + y1) / 2 - 200 + dy * 1000 + 200, face)
    box("kitchen", m(x1 - x0 - 600), 0.6, 0.86, m((x0 + x1) / 2), m(y1 - 320), 0, "white", bevel=0.005)
    box("kitchentop", m(x1 - x0 - 600), 0.62, 0.03, m((x0 + x1) / 2), m(y1 - 320), 0.86, "top")
    box("fridge", 0.6, 0.62, 1.7, m(x0 + 350), m(y1 - 320), 0, "white", bevel=0.01)


def lounge(L):
    x0, y0, x1, y1 = L["x0"], L["y0"], L["x1"], L["y1"]
    # L型造作ベンチ
    box("bench", 0.6, m(y1 - y0), 0.42, m(x0 + 300), m((y0 + y1) / 2), 0, "fabric", bevel=0.03)
    box("benchback", 0.14, m(y1 - y0), 0.45, m(x0 + 70), m((y0 + y1) / 2), 0.42, "fabric2", bevel=0.03)
    box("bench2", m(3800), 0.6, 0.42, m(x0 + 1900), m(y1 - 300), 0, "fabric", bevel=0.03)
    box("bench2back", m(3800), 0.14, 0.45, m(x0 + 1900), m(y1 - 70), 0.42, "fabric2", bevel=0.03)
    for tx, ty in ((1700, 1500), (3300, 700)):
        cyl("table", 0.45, 0.03, m(x0 + tx), m(y0 + ty), 0.7, "top", seg=64, bevel=0.005)
        cyl("tleg", 0.03, 0.7, m(x0 + tx), m(y0 + ty), 0, "oak", seg=16)
    for tx, ty, face in ((5200, 1900, 270), (6200, 1900, 270), (5200, 500, 90), (6200, 500, 90)):
        chair(x0 + tx, y0 + ty, face)
    box("ltable", 0.9, 0.55, 0.45, m(x0 + 5700), m(y0 + 1200), 0, "oakH", bevel=0.006)


def build_1F(cut=None):
    f = DATA["1F"]
    W, D = f["W"], f["D"]
    CHmm = 3000
    CH = m(CHmm)
    H = 2700
    hh = (lambda h: min(h, cut)) if cut else (lambda h: h)
    plane("floor", m(W + 400), m(D + 400), m(W / 2), m(D / 2), 0, "carpet")
    mri = next(r for r in f["rooms"] if r["id"] == "mri")
    plane("mrifloor", m(mri["x1"] - mri["x0"]), m(mri["y1"] - mri["y0"]), m((mri["x0"] + mri["x1"]) / 2), m((mri["y0"] + mri["y1"]) / 2), 0.001, "vinyl")
    tr = next(r for r in f["rooms"] if r["id"] == "tr")
    plane("trfloor", m(tr["x1"] - tr["x0"]), m(tr["y1"] - tr["y0"]), m((tr["x0"] + tr["x1"]) / 2), m((tr["y0"] + tr["y1"]) / 2), 0.001, "vinyl")
    if not cut:
        plane("ceiling", m(W + 400), m(D + 400), m(W / 2), m(D / 2), CH, "ceiling", rot=(math.pi, 0, 0))
    vs = next(r for r in f["rooms"] if r["id"] == "vest")
    # 外周
    wall(-150, -100, -150, vs["y0"], hh(CHmm), 300, "plaster", [(1650, 3350, 150, min(2900, hh(CHmm)))])
    box("ssw_glass", 0.012, m(1700), m(2750), -0.25, m(2400), 0.15, "glass")
    wall(-300, -150, W + 300, -150, hh(CHmm), 300, "plaster", [(2900, 3700, 0, min(2100, hh(CHmm)))])
    wall(-300, D + 150, f["notch"][0] + 300, D + 150, hh(CHmm), 300, "plaster")
    n0, n1 = f["notch"][0], f["notch"][1]
    wall(W + 150, -100, W + 150, n1 + 150, hh(CHmm), 300, "plaster")
    wall(W + 300, n1 + 150, n0 + 150, n1 + 150, hh(CHmm), 300, "plaster")
    wall(n0 + 150, n1, n0 + 150, D + 300, hh(CHmm), 300, "plaster")
    for c, _ in f["columns"]:
        if c < n0 - 400:
            box("column", 0.8, 0.4, hh(CHmm) / 1000, m(c), m(D - 200), 0, "plaster")
    # 道路側：600mm後退の木調縦ルーバー＋小型ロゴ
    for i in range(13):
        box("louver", 0.05, 0.035, 2.5, 0.65, m(1620 + i * 140), 0.1, "oak", bevel=0.004)
    plane("louver_logo", 0.42, 0.14, 0.62, m(2400), 1.7, "logo_small", rot=(math.pi / 2, 0, -math.pi / 2))
    box("louver_logo_back", 0.01, 0.46, 0.18, 0.632, m(2400), 1.61, "oak")
    # エントランス（既設アプローチ）とのガラス間仕切
    wall(vs["x1"], vs["y0"], vs["x1"], D, hh(CHmm), 30, "glass", [(400, 1600, 0, min(2400, hh(CHmm)))])
    wall(0, vs["y0"], vs["x1"], vs["y0"], hh(CHmm), 100, "plaster")
    room_walls(f, H, cut=cut, ch=CHmm)
    reception(f, f["reception"], CH, ring=not cut)
    for x, y, rot in f["chairs"]:
        chair(x, y, {270: 90, 90: 270, 0: 180, 180: 0}[rot])
    for px, py in f.get("plants", []):
        plant(px, py, 1.2)
    # MRI装置（平面図と同じ：ボア軸X方向、ガントリーは東側）
    my = m((mri["y0"] + mri["y1"]) / 2)
    gx = m(mri["x1"] - 1500)
    box("gantry", 1.9, 2.2, 2.0, gx, my, 0, "mri", bevel=0.25)
    cyl("bore", 0.33, 1.95, gx - 0.975, my, 1.0, "dark", rot=(0, math.pi / 2, 0))
    cyl("bore_ring", 0.43, 0.03, gx - 0.965, my, 1.0, "mriblue", rot=(0, math.pi / 2, 0), bevel=0.01)
    tl = m(mri["x1"] - 2450 - mri["x0"] - 450)
    box("mritable", tl, 0.6, 0.72, m(mri["x0"] + 450) + tl / 2, my, 0, "mri", bevel=0.05)
    box("mripad", tl + 0.3, 0.55, 0.06, m(mri["x0"] + 450) + tl / 2 + 0.15, my, 0.72, "bedcover", bevel=0.025)
    # 操作室：操作卓・モニター
    op = next(r for r in f["rooms"] if r["id"] == "op")
    box("console", 0.6, 1.6, 0.72, m(op["x1"] - 400), m(1450), 0, "white", bevel=0.005)
    for k in (-0.35, 0.35):
        box("opmon", 0.03, 0.5, 0.32, m(op["x1"] - 500), m(1450) + k, 0.8, "screen")
    # 診察室・処置室
    ex = next(r for r in f["rooms"] if r["id"] == "ex")
    box("desk", 1.4, 0.6, 0.72, m(ex["x0"] + 900), m(ex["y0"] + 600), 0, "oakH", bevel=0.005)
    bed(ex["x1"] - 550, ex["y1"] - 1150)
    bed(tr["x0"] + 1400, tr["y0"] + 1250, along_x=True)
    if not cut:
        linear_light(600, 1600, 3600, 1600, CH, 55); linear_light(600, 3300, 3600, 3300, CH, 55)
        linear_light(5300, 3500, 9500, 3500, CH, 45)
        linear_light(5400, 5300, 7700, 5300, CH, 45); linear_light(5400, 1450, 7700, 1450, CH, 45)
        linear_light(8300, 1450, 9500, 1450, CH, 40); linear_light(8300, 5300, 9500, 5300, CH, 40)
        linear_light(10400, 1100, 13300, 1100, CH, 55); linear_light(10400, 3200, 13300, 3200, CH, 55)
        sun_world(strength=0.6)


# ====================================================================== world / exterior
def sun_world(strength=1.0, elev=35, rot=-50):
    w = bpy.data.worlds.new("world")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    sky = nt.nodes.new("ShaderNodeTexSky")
    try:
        sky.sky_type = "SINGLE_SCATTERING"
    except Exception:
        pass
    try:
        sky.sun_elevation = math.radians(elev); sky.sun_rotation = math.radians(rot)
    except Exception:
        pass
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength


def build_exterior():
    sys.path.insert(0, HERE)
    from elevations import F1_PARTS, H1, HT, FLOORS as NF, BW
    H1m, HTm, BWm = H1 / 1000, HT / 1000, BW / 1000
    ecp = principled("ecp", (0.62, 0.60, 0.56), rough=0.8)
    pnl = principled("panelA", (0.58, 0.57, 0.55), rough=0.35, metal=0.4)
    alu = principled("alu", (0.70, 0.71, 0.72), rough=0.3, metal=1.0)
    gl = principled("glass_ext", (0.10, 0.12, 0.13), rough=0.03, metal=0.0, **{"Coat Weight": 1.0})
    gl.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 1.0
    stone = principled("stone", (0.48, 0.46, 0.43), rough=0.6)
    warm = mat_emit("warm_interior", (1.0, 0.85, 0.65), 1.2)
    lobby = mat_emit("lobby_interior", (0.95, 0.93, 0.88), 0.8)
    # 立面は X 軸方向（u = 立面左端=X1側から）、建物前面 Y=0、奥 +Y
    h1 = H1m - 0.9
    for u0, u1, k, _ in F1_PARTS:
        a, b = u0 / 1000, u1 / 1000
        w_ = b - a; cx = a + w_ / 2
        if k == "panel":
            box("pA", w_, 0.25, h1, cx, 0.125, 0, "panelA")
            for j in range(1, 4):
                box("pAj", w_, 0.01, 0.008, cx, -0.002, h1 * j / 4, "dark")
        elif k == "ecp":
            box("ecp", w_, 0.25, h1, cx, 0.125, 0, "ecp")
            for j in range(1, 8):
                box("ecpj", w_, 0.01, 0.006, cx, -0.002, h1 * j / 8, "dark")
        elif k == "window":
            box("frameT", w_, 0.12, 0.08, cx, 0.06, h1 - 0.08, "alu"); box("frameB", w_, 0.12, 0.1, cx, 0.06, 0, "alu")
            box("frameL", 0.06, 0.12, h1, a + 0.03, 0.06, 0, "alu"); box("frameR", 0.06, 0.12, h1, b - 0.03, 0.06, 0, "alu")
            box("glassW", w_ - 0.1, 0.012, h1 - 0.18, cx, 0.1, 0.1, "glass")
            # 室内：600mm後退の木調ルーバー＋小型ロゴ＋電球色の間接光
            box("inside_back", w_ + 0.6, 0.02, h1, cx, 1.6, 0, "plaster")
            plane("inside_floor", w_ + 0.6, 1.6, cx, 0.9, 0.0, "carpet")
            for i in range(12):
                box("louver", 0.05, 0.035, 2.6, a + 0.12 + i * (w_ - 0.24) / 11, 0.75, 0.1, "oak", bevel=0.004)
            plane("louver_logo", 0.42, 0.14, cx, 0.72, 1.7, "logo_small", rot=(math.pi / 2, 0, 0))
            area_light("win_glow", cx, 1.2, h1 - 0.1, w_, 0.4, 60, color=(1, 0.8, 0.6))
        elif k == "entry":
            # 既設アプローチ（風除室・奥行1.73m）：道路側に既設ガラス両開き扉、
            # 奥は店内へのガラス扉＋木調の欄間・袖壁に店名ロゴ（リースライン内）
            dep = 1.73
            box("entryL", 0.12, dep, h1, a + 0.06, dep / 2 + 0.1, 0, "oak")
            box("entryR", 0.12, dep, h1, b - 0.06, dep / 2 + 0.1, 0, "oak")
            box("entryCeil", w_, dep, 0.12, cx, dep / 2 + 0.1, h1 - 0.12, "ceiling")
            box("transom", w_, 0.06, h1 - 2.5, cx, dep + 0.1, 2.5, "oak")
            for i in range(1, 12):
                box("slat", 0.012, 0.05, h1 - 2.5, a + i * w_ / 12, dep + 0.07, 2.5, "walnut")
            plane("entry_logo", 0.9, 0.3, cx, dep + 0.065, 2.95, "logo_wood", rot=(math.pi / 2, 0, 0))
            box("innerframe", w_ - 0.2, 0.06, 0.05, cx, dep + 0.1, 2.45, "steel")
            box("innerglass", w_ - 0.24, 0.012, 2.45, cx, dep + 0.1, 0, "glass")
            box("innermull", 0.03, 0.05, 2.45, cx, dep + 0.1, 0, "steel")
            box("outerglass", w_ - 0.2, 0.012, 2.6, cx, 0.12, 0, "glass")
            for xx in (a + 0.1, cx, b - 0.1):
                box("outerframe", 0.05, 0.08, 2.6, xx, 0.12, 0, "steel")
            box("outertop", w_ - 0.2, 0.08, 0.06, cx, 0.12, 2.6, "steel")
            for xx in (cx - 0.08, cx + 0.08):
                box("pull", 0.025, 0.06, 0.9, xx, 0.05, 0.7, "steel")
            plane("entry_floor", w_, dep, cx, dep / 2 + 0.1, 0.001, "stone")
            area_light("entry_cove", cx, dep / 2 + 0.1, h1 - 0.14, w_ - 0.4, dep - 0.3, 35, color=(1, 0.82, 0.6))
            # 扉の奥：店内（受付）の暖かい光
            box("shop_inside", w_ + 1.0, 0.05, h1, cx, dep + 3.0, 0, "oakH")
            plane("shop_floor", w_ + 1.0, 3.0, cx, dep + 1.6, 0.0, "carpet")
            area_light("shop_glow", cx, dep + 1.5, h1 - 0.2, 2.0, 2.0, 120, color=(1, 0.85, 0.65))
        elif k == "bldg_entry":
            box("bglass", w_, 0.012, h1, cx, 0.35, 0, "glass")
            for j in range(5):
                box("bmull", 0.07, 0.15, h1, a + w_ * j / 4, 0.3, 0, "alu")
            box("lobby_back", w_, 0.05, h1, cx, 4.0, 0, lobby)
            plane("lobby_floor", w_, 4.0, cx, 2.0, 0.0, "stone")
            # S1 案内板（ビル標準）
            box("S1", 0.64, 0.04, 0.34, a + 0.72, -0.02, 1.36, "dark", bevel=0.004)
            plane("S1face", 0.58, 0.205, a + 0.72, -0.041, 1.43, "logo_s1", rot=(math.pi / 2, 0, 0))
    # 1F 上部の庇・2F以上（バンド＋ガラス＋縦フィン）
    box("canopy", BWm, 0.4, 0.9, BWm / 2, 0.1, h1, "ecp")
    for i in range(1, NF):
        z0 = H1m + HTm * (i - 1)
        box("band", BWm, 0.35, 0.7, BWm / 2, 0.05, z0, "panelA")
        box("glassU", BWm - 1.2, 0.012, HTm - 0.7, BWm / 2, 0.25, z0 + 0.7, "glass_ext")
        if i in (3, 4):  # 当社 4・5F：内側の防炎ロールスクリーン
            box("screen", BWm - 1.3, 0.01, 0.9, BWm / 2, 0.32, z0 + HTm - 0.95, "white")
        box("ceilglow", BWm - 1.3, 3.0, 0.02, BWm / 2, 1.9, z0 + HTm - 0.05, "led_soft")
        for k_ in range(15):
            box("fin", 0.06, 0.32, HTm - 0.7, 0.6 + k_ * (BWm - 1.2) / 14, 0.05, z0 + 0.7, "alu")
    Htot = H1m + HTm * (NF - 1)
    box("pierL", 0.6, 0.45, Htot + 1.2, 0.3, 0.1, 0, "panelA"); box("pierR", 0.6, 0.45, Htot + 1.2, BWm - 0.3, 0.1, 0, "panelA")
    box("parapet", BWm, 0.45, 1.2, BWm / 2, 0.1, Htot, "panelA")
    box("building_body", BWm, 8.0, Htot, BWm / 2, 8.3, 0, "ecp")
    box("upper_body", BWm, 3.9, Htot - H1m, BWm / 2, 2.4, H1m, "ecp")
    # 隣接建物（簡素）
    for (x0, w_, h_, col) in ((-11.0, 10.5, 30, (0.55, 0.54, 0.52)), (BWm + 0.5, 11, 22, (0.62, 0.6, 0.57))):
        mt = principled(f"nb{x0}", col, rough=0.8)
        box("nb", w_, 12, h_, x0 + w_ / 2, 6.2, 0, mt)
        for z in [4.0 + 3.4 * i for i in range(int((h_ - 4.5) / 3.4))]:
            for xi in range(int((w_ - 1) / 2.2)):
                box("nbwin", 1.4, 0.06, 1.7, x0 + 1.2 + xi * 2.2, 0.17, z, "glass_ext")
        box("nbbase", w_, 0.05, 3.2, x0 + w_ / 2, 0.17, 0, "glass_ext")
    # 歩道・縁石・車道
    tile = principled("paving", (0.42, 0.40, 0.37), rough=0.8)
    plane("sidewalk", 60, 5.5, BWm / 2, -2.75, 0.0, tile)
    for i in range(-30, 45):
        box("joint", 0.008, 5.5, 0.002, i * 0.6, -2.75, 0.0, "dark")
    for j in range(1, 10):
        box("jointy", 60, 0.008, 0.002, BWm / 2, -j * 0.6, 0.0, "dark")
    box("curb", 60, 0.2, 0.15, BWm / 2, -5.6, -0.0, "stone")
    asphalt = principled("asphalt", (0.07, 0.07, 0.075), rough=0.9)
    plane("road", 60, 30, BWm / 2, -20.6, -0.12, asphalt)
    for i in range(-6, 8):
        box("lane", 3.0, 0.15, 0.003, i * 6, -13, -0.12, "white")
    # 街路樹（簡素なスフィア群）
    for tx in (-6.5, 18.0):
        cyl("trunk", 0.08, 3.2, tx, -4.6, 0, "walnut", seg=12)
        r = random.Random(int(tx * 10))
        for i in range(160):
            a = r.random() * 6.28; rr = r.random() ** 0.5 * 1.3
            bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.16 + r.random() * 0.14)
            ob = add_obj("crown", bm, "leaf"); ob.location = (tx + math.cos(a) * rr, -4.6 + math.sin(a) * rr * 0.8, 3.3 + r.random() * 2.0 * (1 - rr / 1.6))
            for p in ob.data.polygons:
                p.use_smooth = True
    sun_world(strength=0.5, elev=38, rot=-35)
    ld = bpy.data.lights.new("sun", "SUN"); ld.energy = 5.5; ld.angle = math.radians(1.0); ld.color = (1.0, 0.94, 0.86)
    ob = bpy.data.objects.new("sun", ld); COL.objects.link(ob)
    ob.rotation_euler = (math.radians(38), 0, math.radians(18))   # 道路側（-Y）右前方・高めの日射（隣棟の影を避ける）


# ====================================================================== cameras / views
def camera(pos, look, lens=24, shift_y=0.0):
    cd = bpy.data.cameras.new("cam"); cd.lens = lens; cd.shift_y = shift_y
    cd.clip_start = 0.05; cd.clip_end = 300
    ob = bpy.data.objects.new("cam", cd); COL.objects.link(ob)
    ob.location = pos
    d = Vector(look) - Vector(pos)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = ob
    return ob


def V(x, y, z):  # mm → m（平面座標）
    return (m(x), m(y), m(z))


VIEWS = {
    # 4F：EVホールから正面の受付を望む（銀座院と同じ構図）
    "v4_lobby": dict(build=lambda: build_upper("4F"), cam=(V(14700, 350, 1450), V(9300, 3700, 1250)), lens=17, exposure=-0.8),
    "v4_front": dict(build=lambda: build_upper("4F"), cam=(V(10075, 250, 1400), V(10075, 4500, 1350)), lens=15, exposure=-0.8),
    "v4_lobby2": dict(build=lambda: build_upper("4F"), cam=(V(14900, 700, 1450), V(7600, 3600, 1150)), lens=18, exposure=-0.8),
    "v4_aisle": dict(build=lambda: build_upper("4F"), cam=(V(20600, 5500, 1500), V(3000, 5500, 1250)), lens=20, exposure=-0.8),
    "v4_room": dict(build=lambda: build_upper("4F"), cam=(V(12900, 6350, 1550), V(11400, 8600, 800)), lens=16, exposure=-0.8),
    "v5_free": dict(build=lambda: build_upper("5F"), cam=(V(14700, 600, 1450), V(8200, 4000, 1100)), lens=18, exposure=-0.8),
    "v5_staff": dict(build=lambda: build_upper("5F"), cam=(V(4700, 1650, 1500), V(800, 4300, 1000)), lens=17, exposure=-0.8),
    "v1_lobby": dict(build=build_1F, cam=(V(350, 350, 1500), V(4300, 4800, 1250)), lens=18, exposure=-0.8),
    "v1_mri": dict(build=build_1F, cam=(V(13650, 250, 1650), V(9900, 2600, 1100)), lens=16, exposure=-0.8),
    "v1_op": dict(build=build_1F, cam=(V(8250, 2500, 1500), V(12400, 1500, 1050)), lens=18, exposure=-0.8),
    "ax1": dict(build=lambda: build_1F(cut=1500), cam=(V(9500, -7500, 12000), V(6900, 3300, 0)), lens=32, exposure=-0.5, axo=True),
    "ax4": dict(build=lambda: build_upper("4F", cut=1500), cam=(V(13500, -11000, 19000), V(10500, 3300, 0)), lens=30, exposure=-0.5, axo=True),
    "ax5": dict(build=lambda: build_upper("5F", cut=1500), cam=(V(13500, -11000, 19000), V(10500, 3300, 0)), lens=30, exposure=-0.5, axo=True),
    "ext": dict(build=build_exterior, cam=((-2.0, -11.5, 1.6), (6.6, 0, 4.6)), lens=18, exposure=-0.7, ext=True),
    "ext_front": dict(build=build_exterior, cam=((7.15, -24.0, 1.6), (7.15, 0, 1.6)), lens=18, exposure=-0.7, ext=True, shift=0.18),
    "ext_entry": dict(build=build_exterior, cam=((0.4, -7.8, 1.55), (3.8, 0, 2.0)), lens=24, exposure=-0.7, ext=True),
}


def main():
    global COL
    view, out = sys.argv[1], sys.argv[2]
    samples = int(sys.argv[3]) if len(sys.argv) > 3 else 160
    W = int(sys.argv[4]) if len(sys.argv) > 4 else 1800
    Hh = int(sys.argv[5]) if len(sys.argv) > 5 else 1125
    sc = reset()
    COL = sc.collection
    tmp = os.path.join(HERE, "build", "tex"); os.makedirs(tmp, exist_ok=True)
    init_materials(tmp)
    v = VIEWS[view]
    v["build"]()
    if v.get("axo"):
        w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
        w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.92, 0.92, 0.91, 1)
        w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
        ld = bpy.data.lights.new("sun", "SUN"); ld.energy = 2.5; ld.angle = math.radians(8)
        ob = bpy.data.objects.new("sun", ld); COL.objects.link(ob); ob.rotation_euler = (math.radians(35), math.radians(15), math.radians(-30))
    pos, look = v["cam"]
    camera(pos, look, v["lens"], v.get("shift", 0.0))
    sc.view_settings.exposure = v.get("exposure", 0)
    sc.cycles.samples = samples
    sc.render.resolution_x, sc.render.resolution_y = W, Hh
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
