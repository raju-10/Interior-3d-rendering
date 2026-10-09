# Bedroom 2 (10'0" x 12'0") — giraffe kids' room, Cycles photoreal render.
# Run: Blender -b -P kids_giraffe.py -- [samples] [width] [height]
import bpy, bmesh, math, os, sys
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'assets')
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SAMPLES = int(argv[0]) if len(argv) > 0 else 384
RES_X = int(argv[1]) if len(argv) > 1 else 1200
RES_Y = int(argv[2]) if len(argv) > 2 else 1600

F = 0.3048  # feet -> metres
def P(x, z, y=0.0):  # plan (x east, z south, y up) in feet -> Blender
    return Vector((x * F, -z * F, y * F))

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
col = scene.collection

# ---------------- materials ----------------
def principled(name, color=(0.8, 0.8, 0.8), rough=0.5, metal=0.0, sheen=0.0, coat=0.0, emit=None, strength=0.0, spec=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Sheen Weight'].default_value = sheen
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Specular IOR Level'].default_value = spec
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = strength
    return m

def srgb(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)

def add_bump(m, scale=400.0, strength=0.35, kind='noise', detail=6.0):
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    if kind == 'voronoi':
        t = nt.nodes.new('ShaderNodeTexVoronoi'); t.inputs['Scale'].default_value = scale; out = t.outputs['Distance']
    else:
        t = nt.nodes.new('ShaderNodeTexNoise'); t.inputs['Scale'].default_value = scale; t.inputs['Detail'].default_value = detail; out = t.outputs['Fac']
    nt.links.new(tc.outputs['Object'], t.inputs['Vector'])
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = strength; bump.inputs['Distance'].default_value = 0.002
    nt.links.new(out, bump.inputs['Height']); nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m

def image_mat(name, path, rough=0.5, scale=(1, 1), nor=None, rough_map=None, sheen=0.0, alpha=False, coords='UV'):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (*scale, 1)
    nt.links.new(tc.outputs[coords], mp.inputs['Vector'])
    def img(p, non_color=False):
        n = nt.nodes.new('ShaderNodeTexImage'); n.image = bpy.data.images.load(p)
        if non_color: n.image.colorspace_settings.name = 'Non-Color'
        nt.links.new(mp.outputs['Vector'], n.inputs['Vector']); return n
    d = img(path); nt.links.new(d.outputs['Color'], b.inputs['Base Color'])
    if alpha: nt.links.new(d.outputs['Alpha'], b.inputs['Alpha'])
    b.inputs['Roughness'].default_value = rough; b.inputs['Sheen Weight'].default_value = sheen
    if nor:
        n = img(nor, True); nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 0.8
        nt.links.new(n.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    if rough_map:
        r = img(rough_map, True); nt.links.new(r.outputs['Color'], b.inputs['Roughness'])
    return m

MAT = {
    'flute': principled('flute', srgb('#CFC5BA'), 0.6),
    'wall': principled('wall', srgb('#D8CFC4'), 0.75),
    'groove': principled('groove', srgb('#9E9387'), 0.8),
    'ceiling': principled('ceiling', srgb('#F2EFEA'), 0.9),
    'archframe': add_bump(principled('archframe', srgb('#E6DED3'), 0.7), 300, 0.05),
    'navyball': principled('navyball', srgb('#2D4D96'), 0.25, coat=0.6),
    'boucle': add_bump(principled('boucle', srgb('#E9E3D9'), 0.95, sheen=0.6), 900, 0.6, 'voronoi'),
    'linen': add_bump(principled('linen', srgb('#F3EFE8'), 0.9, sheen=0.4), 600, 0.15),
    'throw': add_bump(principled('throw', srgb('#B9B3AA'), 0.95, sheen=0.5), 700, 0.25),
    'bluelac': principled('bluelac', srgb('#2F4E92'), 0.18, coat=0.8),
    'bead': principled('bead', srgb('#9DB2D8'), 0.2, coat=0.5),
    'beadwhite': principled('beadwhite', srgb('#E9EDF2'), 0.25, coat=0.4),
    'brass': principled('brass', srgb('#C9A15E'), 0.25, metal=1.0),
    'net': principled('net', srgb('#8EA4CC'), 0.6),
    'velvetnavy': principled('velvetnavy', srgb('#2B3F78'), 0.7, sheen=1.0),
    'fringe': principled('fringe', srgb('#22356A'), 0.8, sheen=0.8),
    'teddy': add_bump(principled('teddy', srgb('#F4F1EC'), 1.0, sheen=1.0), 1200, 0.8, 'voronoi'),
    'toyblue': principled('toyblue', srgb('#3C64B4'), 0.4), 'toywhite': principled('toywhite', srgb('#F4F2EE'), 0.4),
    'led': principled('led', (1, 1, 1), 0.5, emit=srgb('#FFE7C4'), strength=4.0),
    'bulb': principled('bulb', (1, 1, 1), 0.5, emit=srgb('#FFD8A0'), strength=8.0),
    'black': principled('black', srgb('#1A1A1A'), 0.5),
    'skirting': principled('skirting', srgb('#D3C9BE'), 0.5),
}
MAT['floor'] = image_mat('parquet', os.path.join(A, 'parquet_diff.jpg'), 0.45, (2.2, 2.6), nor=os.path.join(A, 'parquet_nor.jpg'), rough_map=os.path.join(A, 'parquet_rough.jpg'))
MAT['rug'] = image_mat('rug', os.path.join(A, 'rug_kids.jpg'), 0.95, sheen=0.6)
add_bump(MAT['rug'], 1500, 0.4, 'voronoi')
MAT['ottotop'] = image_mat('ottotop', os.path.join(A, 'ottoman_top.jpg'), 0.7, (1, 1), sheen=1.0)
MAT['giraffe'] = image_mat('giraffe', os.path.join(A, 'giraffe.png'), 0.75, alpha=True)

# ---------------- mesh helpers ----------------
def obj_from_bm(bm, name, mat, loc=(0, 0, 0), smooth=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); col.objects.link(o); o.location = loc
    if mat: me.materials.append(mat)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    return o

def cube(name, size, loc, mat, bevel=0.0, seg=3, subsurf=0, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    o = obj_from_bm(bm, name, mat, loc, smooth=bool(bevel or subsurf)); o.rotation_euler = rot
    if bevel:
        md = o.modifiers.new('bev', 'BEVEL'); md.width = bevel; md.segments = seg; md.limit_method = 'NONE'
    if subsurf:
        md = o.modifiers.new('sub', 'SUBSURF'); md.levels = subsurf; md.render_levels = subsurf
    return o

def cylinder(name, r, h, loc, mat, seg=48, r2=None, rot=(0, 0, 0), bevel=0.0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    o = obj_from_bm(bm, name, mat, loc, smooth=True); o.rotation_euler = rot
    if bevel:
        md = o.modifiers.new('bev', 'BEVEL'); md.width = bevel; md.segments = 3; md.limit_method = 'ANGLE'
    return o

def spheres(name, items, mat, seg=20):
    """items: list of (Vector center, radius) -> one joined mesh"""
    bm = bmesh.new()
    for c, r in items:
        bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(8, seg // 2), radius=r, matrix=Matrix.Translation(c))
    return obj_from_bm(bm, name, mat, smooth=True)

def arch_pts(w, hs, n=56):
    pts = [(-w / 2, 0.0), (-w / 2, hs)]
    for i in range(1, n):
        t = math.pi - math.pi * i / n
        pts.append((w / 2 * math.cos(t), hs + w / 2 * math.sin(t)))
    pts += [(w / 2, hs), (w / 2, 0.0)]
    return pts

def extrude(name, pts, depth, mat, loc, y0=0.0):
    """2D profile in XZ (metres), extruded toward -Y (into the room is +Y; we build then place)."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, y0, z)) for x, z in pts]
    f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    nv = [g for g in r['geom'] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, depth, 0), verts=nv)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(bm, name, mat, loc)

def arch_ring(name, w_out, hs_out, thick, depth, mat, loc, bevel=0.01, subsurf=0):
    outer = extrude(name, arch_pts(w_out, hs_out), depth, mat, loc)
    inner = extrude(name + '_cut', [(x, z - 0.05) if z <= 0.0001 else (x, z) for x, z in arch_pts(w_out - 2 * thick, hs_out)], depth + 0.04, None, loc, -0.02)
    md = outer.modifiers.new('cut', 'BOOLEAN'); md.object = inner; md.operation = 'DIFFERENCE'; md.solver = 'EXACT'
    bpy.context.view_layer.objects.active = outer
    bpy.ops.object.modifier_apply(modifier='cut')
    bpy.data.objects.remove(inner)
    if bevel:
        b = outer.modifiers.new('bev', 'BEVEL'); b.width = bevel; b.segments = 4; b.limit_method = 'ANGLE'
    if subsurf:
        s = outer.modifiers.new('sub', 'SUBSURF'); s.levels = subsurf; s.render_levels = subsurf
    for p in outer.data.polygons: p.use_smooth = True
    return outer

# ---------------- room shell (plan feet) ----------------
X0, X1, Z0, Z1, HT = 0.5, 10.5, 0.5, 12.5, 10.0
W_ = (X1 - X0) * F; D_ = (Z1 - Z0) * F
cx, cz = (X0 + X1) / 2, (Z0 + Z1) / 2
# floor
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
bmesh.ops.scale(bm, vec=(W_, D_, 1), verts=bm.verts)
floor = obj_from_bm(bm, 'floor', MAT['floor'], P(cx, cz))
floor.data.uv_layers.new(name='UV')
# ceiling
ceil = cube('ceiling', (W_ + .4, D_ + .4, .05), P(cx, cz, HT) + Vector((0, 0, .025)), MAT['ceiling'])
# walls (thick boxes); window holes on north (x 3–8, sill 3, head 7.5) and west (z 7–10.4)
def wall(name, size, loc, holes=()):
    o = cube(name, size, loc, MAT['wall'])
    for i, (hs, hl) in enumerate(holes):
        c = cube(name + f'_h{i}', hs, hl, None)
        md = o.modifiers.new(f'h{i}', 'BOOLEAN'); md.object = c; md.operation = 'DIFFERENCE'; md.solver = 'EXACT'
        bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier=f'h{i}'); bpy.data.objects.remove(c)
    return o
t = 0.5 * F
wall('wall_N', (W_ + 2 * t, t, HT * F), P(cx, Z0 - .25, HT / 2), [((5 * F, 1.0, 4.5 * F), P(5.5, Z0 - .25, 5.25))])
wall('wall_S', (W_ + 2 * t, t, HT * F), P(cx, Z1 + .25, HT / 2))
wall('wall_W', (t, D_, HT * F), P(X0 - .25, cz, HT / 2), [((1.0, 3.4 * F, 4.5 * F), P(X0 - .25, 8.7, 5.25))])
wall('wall_E', (t, D_, HT * F), P(X1 + .25, cz, HT / 2))
for nm, sz, lc in [('skirt_E', (.06 * F, D_, .45 * F), P(X1 - .03, cz, .225)), ('skirt_W', (.06 * F, D_, .45 * F), P(X0 + .03, cz, .225)), ('skirt_N', (W_, .06 * F, .45 * F), P(cx, Z0 + .03, .225))]:
    cube(nm, sz, lc, MAT['skirting'])

# ---------------- fluted feature wall (south wall, faces north) ----------------
FACE = Z1  # wall face
groove = cube('flute_back', (W_, .02, (HT - .1) * F), P(cx, FACE - .03, HT / 2), MAT['groove'])
slat_w, gap = .085, .035
n = int((X1 - X0) / (slat_w + gap))
s = cube('flutes', (slat_w * F, .06 * F, (HT - .35) * F), P(X0 + slat_w / 2 + .01, FACE - .1, .3 + (HT - .35) / 2), MAT['flute'], bevel=.006, seg=2)
ar = s.modifiers.new('arr', 'ARRAY'); ar.count = n; ar.relative_offset_displace = (1 + gap / slat_w, 0, 0)
cube('flute_skirt', (W_, .12 * F, .3 * F), P(cx, FACE - .1, .15), MAT['skirting'])
# fluted quarter column in the west corner
bm = bmesh.new(); R0 = 1.0; seg = 160; zs = (0.3, HT)
ring = []
for k in range(seg + 1):
    a = math.pi / 2 * k / seg
    r = R0 + .035 * abs(math.sin(a * 40))
    ring.append((X0 + r * math.sin(a) * 0 + (r * (1 - math.cos(a))) * 0, a, r))
vs_lo, vs_hi = [], []
for k in range(seg + 1):
    a = math.pi / 2 * k / seg; r = R0 + .035 * abs(math.sin(a * 40))
    x = X0 + R0 - r * math.cos(a); z = FACE - R0 + r * math.sin(a)
    vs_lo.append(bm.verts.new(P(x, z, zs[0]))); vs_hi.append(bm.verts.new(P(x, z, zs[1])))
for k in range(seg):
    bm.faces.new((vs_lo[k], vs_lo[k + 1], vs_hi[k + 1], vs_hi[k]))
col_o = obj_from_bm(bm, 'corner_column', MAT['flute'], smooth=True)
sol = col_o.modifiers.new('sol', 'SOLIDIFY'); sol.thickness = .02
cube('corner_fill', (R0 * F, R0 * F, (HT - .3) * F), P(X0 + R0 / 2, FACE - R0 / 2, .3 + (HT - .3) / 2), MAT['groove'])

# ---------------- arch with navy beads + giraffe ----------------
AC = 4.3  # composition centre (x)
arch_w, arch_hs, thick = 5.6, 5.2, .45
ring_o = arch_ring('arch', arch_w * F, arch_hs * F, thick * F, .45 * F, MAT['archframe'], P(AC, FACE - .55), bevel=.012)
# beads along the arch centreline
beads = []
mid_w = arch_w - thick
pts = arch_pts(mid_w, arch_hs, 400)
L = 0; seglen = []
for i in range(1, len(pts)):
    d = math.dist(pts[i - 1], pts[i]); seglen.append(d); L += d
step = 0.62; target = 0.55; acc = 0
for i in range(1, len(pts)):
    d = seglen[i - 1]
    while acc + d >= target:
        t2 = (target - acc) / d
        x = pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * t2; y = pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * t2
        if y > 0.3: beads.append((P(AC + x, FACE - 1.12, y), .17 * F))
        target += step
    acc += d
spheres('arch_beads', beads, MAT['navyball'], 24)
# giraffe painted on the flutes inside the arch
gw = 3.6; gh = gw * 1120 / 888
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
bmesh.ops.scale(bm, vec=(gw * F, gh * F, 1), verts=bm.verts)
bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'))
g = obj_from_bm(bm, 'giraffe', MAT['giraffe'], P(AC - .3, FACE - .145, 2.9 + gh / 2))
uvg = g.data.uv_layers.new(name='UV')
for d in uvg.data: d.uv = (1 - d.uv[0], d.uv[1])

# ---------------- rainbow bouclé headboard ----------------
hb_y = FACE - .62
bands = [(5.2, .55), (4.1, .55)]
for i, (w, th) in enumerate(bands):
    arch_ring(f'head_band{i}', w * F, 1.05 * F, th * F, (.55 + .12 * i) * F, MAT['boucle'], P(AC, hb_y - .12 * i, 1.1), bevel=.05, subsurf=1)
core = extrude('head_core', arch_pts(3.0 * F, 1.05 * F), .78 * F, MAT['boucle'], P(AC, hb_y - .25, 1.1))
b = core.modifiers.new('bev', 'BEVEL'); b.width = .05; b.segments = 4; b.limit_method = 'ANGLE'
s2 = core.modifiers.new('sub', 'SUBSURF'); s2.levels = 1; s2.render_levels = 1
for p in core.data.polygons: p.use_smooth = True
# channel seams on the core
for k in ():
    cube(f'seam{k}', (.012, .02, 2.1 * F), P(AC + k * .5, hb_y - 1.05, 1.1 + 1.0), MAT['throw'])

# ---------------- bed ----------------
BX0, BX1, BZ1, BZ0 = AC - 2.15, AC + 2.15, hb_y - .2, hb_y - .2 - 6.0
bw = BX1 - BX0; bl = BZ1 - BZ0; bc = (BX0 + BX1) / 2; bz = (BZ0 + BZ1) / 2
cube('bed_base', (bw * F, bl * F, 1.05 * F), P(bc, bz, .55), MAT['boucle'], bevel=.06, seg=5)
cube('mattress', ((bw - .25) * F, (bl - .3) * F, .75 * F), P(bc, bz + .1, 1.45), MAT['linen'], bevel=.05, seg=4)
duvet = cube('duvet', ((bw + .2) * F, (bl - 1.6) * F, .3 * F), P(bc, bz + .95, 1.9), MAT['linen'], bevel=.04, seg=3, subsurf=2)
tx = bpy.data.textures.new('wrinkle', 'CLOUDS'); tx.noise_scale = .25
dsp = duvet.modifiers.new('disp', 'DISPLACE'); dsp.texture = tx; dsp.strength = .015
# grey throw folded across the foot and hanging over the sides
cube('throw_top', ((bw + .1) * F, 1.7 * F, .12 * F), P(bc, BZ0 + 1.3, 2.08), MAT['throw'], bevel=.03, seg=3, subsurf=1)
for sx in ():
    cube(f'throw_side{sx}', (.1 * F, 1.9 * F, .7 * F), P(bc + sx * (bw / 2 + .2), BZ0 + 1.4, 1.75), MAT['throw'], bevel=.03, seg=3, subsurf=1)
# pillows
for i, sx in enumerate((-1, 1)):
    p = cube(f'pillow{i}', (1.85 * F, .55 * F, 1.25 * F), P(bc + sx * 1.0, BZ1 - .6, 2.45), MAT['linen'], bevel=.08, seg=4, subsurf=2); p.rotation_euler = (math.radians(-12), 0, 0)
lp = cube('lumbar', (1.7 * F, .4 * F, .8 * F), P(bc, BZ1 - 1.05, 2.3), MAT['boucle'], bevel=.07, seg=4, subsurf=2); lp.rotation_euler = (math.radians(-15), 0, 0)

# ---------------- bobbin nightstands ----------------
def bobbin(x, z):
    r_top = .72
    cylinder('ns_top', r_top * F, .14 * F, P(x, z, 2.05), MAT['bluelac'], 64, bevel=.008)
    cylinder('ns_base', r_top * F, .14 * F, P(x, z, .07), MAT['bluelac'], 64, bevel=.008)
    items = []
    for k in range(6):
        a = k * math.pi * 2 / 6
        for j in range(9):
            items.append((P(x + math.cos(a) * .45, z + math.sin(a) * .45, .3 + j * .2), .115 * F))
    spheres('ns_bobbins', items, MAT['bluelac'], 20)
    cylinder('ns_core', .3 * F, 1.8 * F, P(x, z, 1.05), MAT['bluelac'], 32)
bobbin(AC - 3.05, FACE - 1.15); bobbin(AC + 3.05, FACE - 1.15)

# ---------------- beaded pendants (either side) ----------------
def bead_pendant(x, z, bottom=4.4):
    items_b, items_w = [], []
    H_ = 1.7; strands = 28
    for k in range(strands):
        a = k * math.pi * 2 / strands
        for j in range(16):
            t = j / 15
            r = .18 + .55 * math.sin(math.pi * min(1, t * 1.15)) ** .8 * (1 - .25 * t)
            y = bottom + H_ - t * H_
            (items_w if j in (5, 6) else items_b).append((P(x + math.cos(a) * r, z + math.sin(a) * r, y), .05 * F))
    spheres('pend_beads', items_b, MAT['bead'], 10); spheres('pend_beads_w', items_w, MAT['beadwhite'], 10)
    cylinder('pend_ring', .6 * F, .05 * F, P(x, z, bottom + H_ + .02), MAT['brass'], 48)
    cylinder('pend_rod', .02 * F, (HT - bottom - H_) * F, P(x, z, (HT + bottom + H_) / 2), MAT['brass'], 12)
    spheres('pend_bulb', [(P(x, z, bottom + .9), .15 * F)], MAT['bulb'], 16)
    bpy.ops.object.light_add(type='POINT', location=P(x, z, bottom + .9)); L_ = bpy.context.object; L_.data.energy = 12; L_.data.color = srgb('#FFD9A8'); L_.data.shadow_soft_size = .05
bead_pendant(AC - 3.05, FACE - 1.4); bead_pendant(AC + 3.05, FACE - 1.4)

# ---------------- woven dome ceiling light ----------------
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=36, v_segments=18, radius=1.15 * F)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > .02], context='VERTS')
dome = obj_from_bm(bm, 'dome', MAT['net'], P(AC, FACE - 3.2, 8.4), smooth=True)
wf = dome.modifiers.new('wire', 'WIREFRAME'); wf.thickness = .012; wf.use_even_offset = True
sb = dome.modifiers.new('sub', 'SUBSURF'); sb.levels = 1; sb.render_levels = 1
dome.scale = (1, 1, .82)
cylinder('dome_rim', 1.17 * F, .08 * F, P(AC, FACE - 3.2, 8.4), MAT['brass'], 64)
cylinder('dome_rod', .02 * F, 1.6 * F, P(AC, FACE - 3.2, 9.2), MAT['brass'], 12)
spheres('dome_bead', [(P(AC, FACE - 3.2, 7.35), .12 * F)], MAT['bead'], 16)
spheres('dome_bulb', [(P(AC, FACE - 3.2, 7.9), .18 * F)], MAT['bulb'], 16)
bpy.ops.object.light_add(type='POINT', location=P(AC, FACE - 3.2, 7.8)); L_ = bpy.context.object; L_.data.energy = 25; L_.data.color = srgb('#FFDDB0'); L_.data.shadow_soft_size = .1

# ---------------- ceiling LED slots ----------------
for x in (X0 + 1.1, X1 - 1.1):
    cube('slot', (.12 * F, (D_ - .6), .02), P(x, cz, HT - .02), MAT['black'])
    cube('slot_led', (.05 * F, (D_ - .7), .02), P(x, cz, HT - .035), MAT['led'])
cube('slot_back', ((W_ - .6), .12 * F, .02), P(cx, FACE - .9, HT - .02), MAT['black'])
cube('slot_back_led', ((W_ - .7), .05 * F, .02), P(cx, FACE - .9, HT - .035), MAT['led'])

# ---------------- fringed ottoman ----------------
OZ = BZ0 - 1.05
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=96, radius1=.5, radius2=.5, depth=1.0)
bmesh.ops.scale(bm, vec=(3.8 * F, 1.7 * F, .55 * F), verts=bm.verts)
ot = obj_from_bm(bm, 'ottoman', MAT['velvetnavy'], P(AC, OZ, 1.35), smooth=True)
ot.data.materials.append(MAT['ottotop'])
for p in ot.data.polygons:
    if p.normal.z > .9: p.material_index = 1
bv = ot.modifiers.new('bev', 'BEVEL'); bv.width = .03; bv.segments = 4; bv.limit_method = 'ANGLE'
uv = ot.data.uv_layers.new(name='UV')
for poly in ot.data.polygons:
    for li in poly.loop_indices:
        co = ot.data.vertices[ot.data.loops[li].vertex_index].co
        uv.data[li].uv = (co.x / (3.8 * F) + .5, co.y / (1.7 * F) + .5)
cube('ottoman_base', (3.4 * F, 1.4 * F, .9 * F), P(AC, OZ, .55), MAT['velvetnavy'], bevel=.04)
bm = bmesh.new()
for k in range(520):
    a = k * math.pi * 2 / 520
    x = math.cos(a) * 3.8 / 2 * .99; z = math.sin(a) * 1.7 / 2 * .99
    m = Matrix.Translation(P(AC + x, OZ + z, .55)) @ Matrix.Rotation(-a, 4, 'Z')
    bmesh.ops.create_cube(bm, size=1.0, matrix=m @ Matrix.Diagonal((.012, .03, 1.1 * F / 1, 1)))
fr = obj_from_bm(bm, 'fringe', MAT['fringe'])
# teddy + blocks on the ottoman
tb = [(P(AC + 1.1, OZ, 1.95), .38 * F), (P(AC + 1.1, OZ, 2.55), .27 * F), (P(AC + .93, OZ, 2.78), .09 * F), (P(AC + 1.27, OZ, 2.78), .09 * F), (P(AC + 1.1, OZ - .22, 2.5), .1 * F), (P(AC + .8, OZ - .15, 1.8), .12 * F), (P(AC + 1.4, OZ - .15, 1.8), .12 * F)]
tb = [((c - P(AC + 1.1, OZ, 1.6)) * .7 + P(AC + 1.1, OZ, 1.6), r * .7) for c, r in tb]
spheres('teddy', tb, MAT['teddy'], 28)
for i, (dx, dz, m) in enumerate([(-1.2, .1, 'toyblue'), (-.7, -.2, 'toywhite'), (-.3, .15, 'toyblue'), (.2, -.1, 'toywhite')]):
    c = cube(f'block{i}', (.3 * F, .3 * F, .3 * F), P(AC + dx, OZ + dz, 1.8), MAT[m], bevel=.006); c.rotation_euler = (0, 0, i * .4)

# ---------------- rug ----------------
rug = cube('rug', (7.5 * F, 8.5 * F, .04 * F), P(AC, BZ0 + 1.6, .02), MAT['rug'], bevel=.004)
uvl = rug.data.uv_layers.new(name='UV')
for poly in rug.data.polygons:
    for li in poly.loop_indices:
        co = rug.data.vertices[rug.data.loops[li].vertex_index].co
        uvl.data[li].uv = (co.x / (7.5 * F) + .5, co.y / (8.5 * F) + .5)

# ---------------- lighting & world ----------------
world = bpy.data.worlds.new('sky'); scene.world = world; world.use_nodes = True
wn = world.node_tree.nodes; env = wn.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(os.path.join(A, 'sky.hdr'))
world.node_tree.links.new(env.outputs['Color'], wn['Background'].inputs['Color']); wn['Background'].inputs['Strength'].default_value = 0.8
# soft fill like a large window/bounce card behind the camera (invisible to camera)
bpy.ops.object.light_add(type='AREA', location=P(AC, Z0 + .6, 6.5)); fill = bpy.context.object
fill.data.shape = 'RECTANGLE'; fill.data.size = 7 * F; fill.data.size_y = 5 * F; fill.data.energy = 140; fill.data.color = srgb('#FFF3E6')
fill.rotation_euler = (math.radians(80), 0, 0); fill.visible_camera = False
# ceiling bounce
bpy.ops.object.light_add(type='AREA', location=P(cx, cz, HT - .15)); top = bpy.context.object
top.data.size = 7 * F; top.data.size_y = 9 * F; top.data.shape = 'RECTANGLE'; top.data.energy = 70; top.data.color = srgb('#FFEBD2'); top.visible_camera = False

# ---------------- camera ----------------
cam_d = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_d); col.objects.link(cam); scene.camera = cam
cam.location = P(AC, Z0 + .15, 3.9)
target = P(AC, FACE, 3.95)
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam_d.sensor_fit = 'VERTICAL'; cam_d.angle = math.radians(72 if RES_Y > RES_X else 60)
cam_d.clip_start = .05

# ---------------- render settings ----------------
scene.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type = 'METAL'; prefs.get_devices()
    for d in prefs.devices: d.use = True
    scene.cycles.device = 'GPU'
except Exception as e:
    print('GPU unavailable, using CPU:', e)
scene.cycles.samples = SAMPLES; scene.cycles.use_denoising = True
scene.cycles.max_bounces = 10; scene.cycles.caustics_reflective = False; scene.cycles.caustics_refractive = False
scene.cycles.blur_glossy = 1.0
scene.render.resolution_x = RES_X; scene.render.resolution_y = RES_Y; scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'; scene.view_settings.look = 'AgX - Medium High Contrast'; scene.view_settings.exposure = 0.0
scene.render.image_settings.file_format = 'PNG'
out = os.path.join(HERE, 'renders', f'bedroom2_giraffe_{RES_X}x{RES_Y}.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
scene.render.filepath = out
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'bedroom2_giraffe.blend'))
bpy.ops.render.render(write_still=True)
print('RENDERED', out)
