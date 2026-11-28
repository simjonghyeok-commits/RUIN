"""현관문을 안쪽에서 닫는 손 — 시네마틱 스틸 컷 (Blender bpy + Cycles, 외부 생성 AI 미사용).

사용법:
    python3 tools/render_door_scene.py OUT.png [WIDTH HEIGHT SAMPLES]
좌표: 미터, Z 위. 현관문 안쪽 벽면이 y=0, 집 안쪽이 y<0, 복도가 y>0.
한국 아파트 현관문은 바깥으로 열리므로, 안에서 손잡이를 당겨 닫는 동작이다.
"""
import math
import sys

import bpy
from mathutils import Matrix, Vector

OUT = sys.argv[1] if len(sys.argv) > 1 else "door.png"
RES_W = int(sys.argv[2]) if len(sys.argv) > 2 else 1920
RES_H = int(sys.argv[3]) if len(sys.argv) > 3 else 1080
SAMPLES = int(sys.argv[4]) if len(sys.argv) > 4 else 256

DOOR_W, DOOR_H = 0.95, 2.10
DOOR_T = 0.045
FRAME_T = 0.07          # 문틀(벽) 두께
AJAR_DEG = 3.2          # 문이 거의 닫힌 상태
LEVER_Z = 1.00

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


# ---------- 재질 ----------
def mat(name, color, rough=0.6, metal=0.0, sss=0.0, bump=None, spec=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Specular IOR Level"].default_value = spec
    if sss:
        bsdf.inputs["Subsurface Weight"].default_value = sss
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.45, 0.25)
        bsdf.inputs["Subsurface Scale"].default_value = 0.004
    if bump:
        kind, scale, strength = bump
        tex = nt.nodes.new("ShaderNodeTexNoise" if kind == "noise" else "ShaderNodeTexWave")
        tex.inputs["Scale"].default_value = scale
        if kind == "noise":
            tex.inputs["Detail"].default_value = 8
        else:
            tex.wave_type = "BANDS"
            tex.bands_direction = "Z"
        b = nt.nodes.new("ShaderNodeBump")
        b.inputs["Strength"].default_value = strength
        b.inputs["Distance"].default_value = 0.002
        nt.links.new(tex.outputs[0 if kind == "noise" else "Fac"], b.inputs["Height"])
        nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def tile_mat():
    m = bpy.data.materials.new("tile")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.28
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.offset = 0.0
    brick.inputs["Color1"].default_value = (0.42, 0.39, 0.35, 1)
    brick.inputs["Color2"].default_value = (0.45, 0.42, 0.37, 1)
    brick.inputs["Mortar"].default_value = (0.20, 0.19, 0.17, 1)
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = 0.004
    brick.inputs["Brick Width"].default_value = 0.6
    brick.inputs["Row Height"].default_value = 0.6
    coord = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(coord.outputs["Object"], brick.inputs["Vector"])
    nt.links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.4
    nt.links.new(brick.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def wood_mat(name, base, dark, rough):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = rough
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "X"
    wave.inputs["Scale"].default_value = 6
    wave.inputs["Distortion"].default_value = 6
    wave.inputs["Detail"].default_value = 4
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*dark, 1)
    ramp.color_ramp.elements[1].color = (*base, 1)
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return m


M_WALL = mat("wall", (0.70, 0.66, 0.58), 0.85, bump=("noise", 300, 0.05))
M_DOOR = wood_mat("door", (0.20, 0.135, 0.085), (0.185, 0.125, 0.08), 0.45)
M_FRAME = mat("frame", (0.17, 0.12, 0.08), 0.4)
M_METAL = mat("metal", (0.55, 0.53, 0.50), 0.28, metal=1.0)
M_LOCK = mat("lock", (0.015, 0.015, 0.017), 0.15)
M_TILE = tile_mat()
M_WOODFLOOR = wood_mat("woodfloor", (0.36, 0.23, 0.13), (0.27, 0.16, 0.09), 0.35)
M_CAB = mat("cabinet", (0.74, 0.71, 0.65), 0.5)
M_SKIN = mat("skin", (0.60, 0.42, 0.33), 0.48, sss=0.35, bump=("noise", 900, 0.08))
M_SLEEVE = mat("sleeve", (0.44, 0.36, 0.28), 0.95, bump=("noise", 180, 0.35))
M_CUFF = mat("cuff", (0.42, 0.34, 0.26), 0.95)
M_SHOE_BLACK = mat("shoe_black", (0.025, 0.022, 0.02), 0.32)
M_SHOE_TAN = mat("shoe_tan", (0.30, 0.17, 0.09), 0.45)
M_SHOE_IN = mat("shoe_in", (0.05, 0.04, 0.035), 0.9)
M_SOLE = mat("sole", (0.12, 0.10, 0.08), 0.7)
M_SOLE_W = mat("sole_w", (0.62, 0.60, 0.56), 0.7)
M_SNEAK = mat("sneaker", (0.55, 0.55, 0.53), 0.8)

# 커프스 골지
_cnt = M_CUFF.node_tree
_wave = _cnt.nodes.new("ShaderNodeTexWave")
_wave.wave_type = "RINGS"
_wave.rings_direction = "SPHERICAL"
_wave.inputs["Scale"].default_value = 1.0
_wave.wave_profile = "SIN"
_geo = _cnt.nodes.new("ShaderNodeTexCoord")
_sep = _cnt.nodes.new("ShaderNodeSeparateXYZ")
_math = _cnt.nodes.new("ShaderNodeMath")
_math.operation = "SINE"
_mul = _cnt.nodes.new("ShaderNodeMath")
_mul.operation = "MULTIPLY"
_mul.inputs[1].default_value = 260.0
_cnt.links.new(_geo.outputs["Object"], _sep.inputs[0])
# 골지는 소매 둘레 방향(로컬 각도)으로 — 로컬 X,Y의 atan2
_atan = _cnt.nodes.new("ShaderNodeMath")
_atan.operation = "ARCTAN2"
_cnt.links.new(_sep.outputs["Y"], _atan.inputs[0])
_cnt.links.new(_sep.outputs["X"], _atan.inputs[1])
_mul2 = _cnt.nodes.new("ShaderNodeMath")
_mul2.operation = "MULTIPLY"
_mul2.inputs[1].default_value = 28.0
_cnt.links.new(_atan.outputs[0], _mul2.inputs[0])
_cnt.links.new(_mul2.outputs[0], _math.inputs[0])
_bmp = _cnt.nodes.new("ShaderNodeBump")
_bmp.inputs["Strength"].default_value = 0.6
_cnt.links.new(_math.outputs[0], _bmp.inputs["Height"])
_cnt.links.new(_bmp.outputs["Normal"], _cnt.nodes["Principled BSDF"].inputs["Normal"])


# ---------- 헬퍼 ----------
def box(name, x0, x1, y0, y1, z0, z1, m, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.object
    o.name = name
    o.scale = (x1 - x0, y1 - y0, z1 - z0)
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        mod = o.modifiers.new("bev", "BEVEL")
        mod.width = bevel
        mod.segments = 3
    o.data.materials.append(m)
    return o


def cyl(name, loc, r, depth, rot, m, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


# ---------- 공간 ----------
HX = DOOR_W / 2
# 현관 벽 (문 개구부 주변)
box("wall_L", -1.2, -HX - 0.06, 0, FRAME_T, -0.2, 2.5, M_WALL)
box("wall_R", HX + 0.06, 1.6, 0, FRAME_T, -0.2, 2.5, M_WALL)
box("wall_T", -HX - 0.06, HX + 0.06, 0, FRAME_T, DOOR_H + 0.05, 2.5, M_WALL)
# 문틀 (문 둘레 몰딩)
box("jamb_L", -HX - 0.06, -HX, -0.015, FRAME_T, 0, DOOR_H + 0.05, M_FRAME, 0.004)
box("jamb_R", HX, HX + 0.06, -0.015, FRAME_T, 0, DOOR_H + 0.05, M_FRAME, 0.004)
box("jamb_T", -HX - 0.06, HX + 0.06, -0.015, FRAME_T, DOOR_H, DOOR_H + 0.05, M_FRAME, 0.004)
# 경첩 쪽 문풍지(빛 차단)
box("hinge_stop", -HX - 0.02, -HX + 0.025, FRAME_T - 0.02, FRAME_T + 0.08, 0, DOOR_H + 0.05, M_FRAME)
# 좌우 벽, 천장
box("side_L", -1.25, -1.2, -3.5, FRAME_T, -0.2, 2.5, M_WALL)
box("side_R", 1.25, 1.3, -3.5, FRAME_T, -0.2, 2.5, M_WALL)
box("ceil", -1.25, 1.3, -3.5, 0.3, 2.4, 2.45, M_WALL)

# 현관 바닥(타일) + 한 단 높은 마루
tile = box("tile", -1.2, 1.25, -1.15, 0.0, -0.02, 0.0, M_TILE)
box("step", -1.2, 1.25, -1.17, -1.15, -0.02, 0.15, M_WOODFLOOR, 0.003)
box("woodfloor", -1.2, 1.25, -3.5, -1.15, 0.13, 0.15, M_WOODFLOOR)

# 신발장 (왼쪽, 붙박이)
box("cab_body", -1.2, -0.80, -1.10, -0.06, 0.12, 2.40, M_CAB)
for i, (y0, y1) in enumerate([(-1.08, -0.585), (-0.575, -0.08)]):
    box(f"cab_door{i}", -0.80, -0.785, y0, y1, 0.14, 2.38, M_CAB, 0.002)
box("cab_kick", -1.2, -0.81, -1.10, -0.06, 0.0, 0.12, M_FRAME)

# ---------- 문 (바깥여닫이, 살짝 열린 상태) ----------
pivot = bpy.data.objects.new("door_pivot", None)
scene.collection.objects.link(pivot)
pivot.location = (-HX, FRAME_T - 0.02 + DOOR_T, 0)
door = box("door", 0.0015, DOOR_W - 0.004, -DOOR_T, 0, 0.003, DOOR_H - 0.003, M_DOOR, 0.002)
door.parent = pivot
# 문 안쪽 면 패널 몰딩
box("door_panel", 0.10, DOOR_W - 0.10, -DOOR_T - 0.006, -DOOR_T, 0.15, DOOR_H - 0.15, M_DOOR, 0.003).parent = pivot

# 손잡이(레버)와 디지털 도어록 (글자 없음)
lx = DOOR_W - 0.11
ly = -DOOR_T
rose = cyl("rose", (lx, ly - 0.008, LEVER_Z), 0.028, 0.016, (math.radians(90), 0, 0), M_METAL)
rose.parent = pivot
neck = cyl("neck", (lx, ly - 0.035, LEVER_Z), 0.011, 0.055, (math.radians(90), 0, 0), M_METAL)
neck.parent = pivot
lever = cyl("lever", (lx - 0.065, ly - 0.058, LEVER_Z), 0.0105, 0.13, (0, math.radians(90), 0), M_METAL)
lever.parent = pivot
tip = cyl("lever_tip", (lx - 0.13, ly - 0.058, LEVER_Z), 0.0105, 0.004, (0, math.radians(90), 0), M_METAL)
tip.parent = pivot
lock = box("lock", lx - 0.035, lx + 0.035, ly - 0.03, ly, LEVER_Z + 0.12, LEVER_Z + 0.36, M_LOCK, 0.008)
lock.parent = pivot

pivot.rotation_euler = (0, 0, math.radians(AJAR_DEG))
bpy.context.view_layer.update()

# 레버 바의 월드 좌표 (손 배치 기준)
lever_mid = lever.matrix_world.translation.copy()
LEVER_DIR = (lever.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()


# ---------- 손 (메타볼) ----------
mb = bpy.data.metaballs.new("hand_mb")
mb.resolution = 0.0024
mb.render_resolution = 0.0011
mb.threshold = 0.6
hand = bpy.data.objects.new("hand", mb)
scene.collection.objects.link(hand)
hand.data.materials.append(M_SKIN)

C = lever_mid
X = LEVER_DIR if LEVER_DIR.x > 0 else -LEVER_DIR          # 레버 축(+x 쪽)
# 손 좌표계: H=손목→손가락 방향, N=손등 법선(위), L=엄지 쪽(오른손 손등이 위일 때 왼쪽)
H = Vector((-0.56, 0.83, 0.0)).normalized()
N = Vector((0, 0, 1))
L = N.cross(H).normalized()
K = 1.28


def Q(h, l, n, base=None):
    return (base if base is not None else C) + H * h + L * l + N * n


def rot_for(xaxis, zhint=N):
    xa = xaxis.normalized()
    ya = zhint.cross(xa).normalized()
    za = xa.cross(ya)
    return Matrix((xa, ya, za)).transposed().to_quaternion()


def capsule(a, b, r, stiff=2.0):
    e = mb.elements.new(type="CAPSULE")
    e.co = (a + b) / 2
    e.radius = r * K
    e.size_x = max((b - a).length / 2, 1e-4)
    e.rotation = rot_for(b - a)
    e.stiffness = stiff


def ellip(p, sx, sy, sz, stiff=2.0, xaxis=None):
    e = mb.elements.new(type="ELLIPSOID")
    e.co = p
    e.radius = 1.0
    e.size_x, e.size_y, e.size_z = sx / 1.1, sy / 1.1, sz / 1.1
    e.rotation = rot_for(xaxis if xaxis is not None else L)
    e.stiffness = stiff


def seg_chain(pts, radii, stiff=2.0):
    for a, b, ra, rb in zip(pts, pts[1:], radii, radii[1:]):
        capsule(a, b, (ra + rb) / 2, stiff)


# 손가락 (엄지쪽 거리 l, 굵기 r, 길이배율 s). 레버를 넘어 뒤로 말려 내려간다.
FINGERS = [(0.026, 0.0083, 1.00), (0.008, 0.0087, 1.06), (-0.010, 0.0082, 1.00), (-0.027, 0.0071, 0.85)]
for l, r, s in FINGERS:
    t = l / X.dot(L)                    # 이 손가락 평면이 레버와 만나는 지점
    cf = C + X * t
    mcp = Q(-0.030 + 0.006 * (s - 1), l, 0.026)
    pip = Q(0.018 * s, 0, 0.014, cf) + L * 0.0
    dip = Q(0.022 * s, 0, -0.011, cf)
    tipp = Q(0.006, 0, -0.021 * s, cf)
    seg_chain([mcp, pip, dip, tipp], [r * 1.08, r * 1.0, r * 0.93, r * 0.86], 1.6)

# 손등·손바닥 몸통
ellip(Q(-0.058, 0.0, 0.022), 0.037, 0.040, 0.012, 2.0)
# 엄지: 검지 쪽 손바닥에서 나와 레버 아래를 받친다 (엄지 위치의 레버 지점 기준)
tb = C + X * (0.040 / X.dot(L))
seg_chain([Q(-0.072, 0.036, 0.010), Q(-0.040, 0.044, -0.006), Q(-0.016, 0.0, -0.020, tb) + L * 0.002,
           Q(0.004, -0.006, -0.018, tb)],
          [0.0128, 0.0108, 0.0096, 0.0088], 1.6)
# 손목 → 팔뚝
wrist = Q(-0.108, 0.0, 0.028)
ARM_DIR = (-H + Vector((0, 0, -0.30))).normalized()
ellip(wrist, 0.027, 0.022, 0.019, 1.6, xaxis=L)
capsule(wrist, wrist + ARM_DIR * 0.12, 0.026, 1.6)

# ---------- 소매 (니트 카디건) ----------
def sleeve_tube(start, direction, length, r0, r1, m, name, thick=0.006, fold=0.0):
    mid = start + direction * (length / 2)
    bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=r0, radius2=r1, depth=length, end_fill_type="NOTHING", location=mid)
    o = bpy.context.object
    o.name = name
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, -1)).rotation_difference(direction)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.subdivide(number_cuts=24)
    bpy.ops.object.mode_set(mode="OBJECT")
    if fold:
        tex = bpy.data.textures.new(name + "_fold", "CLOUDS")
        tex.noise_scale = 0.035
        dis = o.modifiers.new("fold", "DISPLACE")
        dis.texture = tex
        dis.strength = fold
        dis.mid_level = 0.5
    sol = o.modifiers.new("sol", "SOLIDIFY")
    sol.thickness = thick
    sub = o.modifiers.new("sub", "SUBSURF")
    sub.levels = 2
    sub.render_levels = 2
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


cuff_start = Q(-0.094, 0.0, 0.024)
sleeve_tube(cuff_start, ARM_DIR, 0.065, 0.041, 0.043, M_CUFF, "cuff", thick=0.007)
fore_start = cuff_start + ARM_DIR * 0.06
sleeve_tube(fore_start, ARM_DIR, 0.27, 0.047, 0.060, M_SLEEVE, "sleeve", thick=0.006, fold=0.014)
elbow = fore_start + ARM_DIR * 0.27
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=0.062, location=elbow)
bpy.context.object.data.materials.append(M_SLEEVE)
bpy.ops.object.shade_smooth()
UPPER_DIR = Vector((0.80, -0.30, 0.62)).normalized()
sleeve_tube(elbow, UPPER_DIR, 0.70, 0.062, 0.072, M_SLEEVE, "upper", thick=0.006, fold=0.018)



# ---------- 신발 ----------
def shoe(name, x, y, rot, length, width, height, upper, sole_m, sneaker=False):
    root = bpy.data.objects.new(name, None)
    scene.collection.objects.link(root)
    root.location = (x, y, 0)
    root.rotation_euler = (0, 0, rot)
    # 몸체: 위가 열린 유선형
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=1)
    body = bpy.context.object
    body.name = name + "_body"
    body.scale = (width / 2, length / 2, height)
    body.location = (0, 0, 0.012)
    bpy.ops.object.transform_apply(scale=True, location=False)
    me = body.data
    # 바닥 평평하게, 발 넣는 구멍(뒤쪽 위) 비우기
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    for v in bm.verts:
        if v.co.z < 0:
            v.co.z *= 0.15
    # 발 넣는 입구: 뒤쪽 위를 매끈한 타원 경계로 비운다
    cut_z = height * (0.55 if sneaker else 0.40)
    def inside(v):
        ey = (v.co.y + length * 0.16) / (length * 0.27)
        ex = v.co.x / (width * 0.34)
        return v.co.z > cut_z * 0.6 and ex * ex + ey * ey < 1.0
    opening = [f for f in bm.faces if all(inside(v) for v in f.verts)]
    bmesh.ops.delete(bm, geom=opening, context="FACES")
    bm.to_mesh(me)
    bm.free()
    sol = body.modifiers.new("sol", "SOLIDIFY")
    sol.thickness = 0.004
    body.modifiers.new("sub", "SUBSURF").levels = 1
    body.data.materials.append(upper)
    bpy.ops.object.shade_smooth()
    body.parent = root
    # 안창
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=1, depth=0.002)
    ins = bpy.context.object
    ins.scale = (width / 2 * 0.86, length / 2 * 0.9, 1)
    ins.location = (0, 0, 0.016)
    ins.data.materials.append(M_SHOE_IN)
    ins.parent = root
    # 밑창
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=1, depth=0.014 if sneaker else 0.009)
    so = bpy.context.object
    so.scale = (width / 2 * 1.02, length / 2 * 1.01, 1)
    so.location = (0, 0, 0.006)
    so.data.materials.append(sole_m)
    bev = so.modifiers.new("bev", "BEVEL")
    bev.width = 0.003
    bev.segments = 2
    so.parent = root
    return root


# 앞코가 문을 향하도록 가지런히 (한국 현관 정리 습관)
for i, sx in enumerate((-0.40, -0.31)):
    shoe(f"loafer{i}", sx, -0.30, 0.0, 0.245, 0.085, 0.055, M_SHOE_BLACK, M_SOLE)
for i, sx in enumerate((-0.17, -0.065)):
    shoe(f"sneaker{i}", sx, -0.32, 0.0, 0.27, 0.095, 0.07, M_SNEAK, M_SOLE_W, sneaker=True)
for i, sx in enumerate((0.07, 0.155)):
    shoe(f"flat{i}", sx, -0.29, 0.0, 0.23, 0.078, 0.045, M_SHOE_TAN, M_SOLE)


# ---------- 조명 ----------
def area(name, loc, target, size, energy, color, shape="RECTANGLE", size_y=None):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = energy
    ld.color = color
    ld.shape = shape
    ld.size = size
    if size_y:
        ld.size_y = size_y
    o = bpy.data.objects.new(name, ld)
    scene.collection.objects.link(o)
    o.location = loc
    d = Vector(target) - Vector(loc)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, -1)).rotation_difference(d)
    return o


WARM = (1.0, 0.62, 0.30)
# 복도 조명 (문 바깥, 오른쪽 위) — 문틈으로만 새어 들어온다
area("corridor_key", (1.4, 1.1, 2.3), (0.3, 0.0, 0.6), 0.6, 1400, WARM)
area("corridor_fill", (0.2, 1.6, 2.35), (0.0, 0.0, 1.0), 1.2, 700, (1.0, 0.70, 0.42), size_y=0.6)
# 바깥 복도 벽/바닥 (빛 반사용)
box("corr_floor", -2, 3, 0.07, 3, -0.03, -0.02, M_TILE)
box("corr_wall", -2, 3, 2.0, 2.05, -0.03, 2.6, M_WALL)
box("corr_ceil", -2, 3, 0.07, 2.0, 2.5, 2.55, M_WALL)
# 실내: 거실 창으로 들어오는 저녁의 푸른 잔광 (카메라 뒤 왼쪽)
area("dusk_fill", (-0.6, -3.2, 1.6), (0.0, -0.3, 0.8), 2.0, 14, (0.45, 0.72, 0.78), size_y=1.2)
# 손에 닿는 약한 따뜻한 바운스 (문틈 빛의 반사 보강)
hb = area("hand_bounce", (0.75, -0.25, 0.55), (0.30, -0.10, 1.0), 0.25, 4.0, WARM)
hb.data.use_shadow = False
hb.visible_shadow = False

world = bpy.data.worlds.new("w")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.020, 0.055, 0.060, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.10

# ---------- 카메라 ----------
cam_d = bpy.data.cameras.new("cam")
cam_d.lens = 26
cam_d.sensor_width = 36
cam = bpy.data.objects.new("cam", cam_d)
scene.collection.objects.link(cam)
cam.location = (0.40, -1.70, 1.40)
look = Vector((0.12, -0.30, 0.74))
cam.rotation_mode = "QUATERNION"
cam.rotation_quaternion = Vector((0, 0, -1)).rotation_difference(look - cam.location)
# 롤 보정: 카메라 위쪽을 월드 Z에 맞춤
cam.rotation_mode = "XYZ"
eul = (look - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.rotation_euler = eul
scene.camera = cam
import os
if os.environ.get("HANDCAM"):
    cam.location = C + (Vector((0.02, -1.12, 1.38)) - C).normalized() * 0.32
    cam.rotation_euler = (C - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_d.lens = 50
    cam_d.dof.use_dof = False
    if os.environ.get("HANDCAM") == "2":
        cam.location = C + Vector((-0.05, -0.28, 0.22))
        cam.rotation_euler = (C - cam.location).to_track_quat("-Z", "Y").to_euler()
cam_d.dof.use_dof = not os.environ.get("HANDCAM")
cam_d.dof.focus_distance = (C - cam.location).length
cam_d.dof.aperture_fstop = 2.0

# ---------- 렌더 설정 ----------
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 8
scene.cycles.caustics_reflective = False
scene.cycles.caustics_refractive = False
scene.render.threads_mode = "FIXED"
scene.render.threads = 4
scene.render.resolution_x = RES_W
scene.render.resolution_y = RES_H
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = 0.0
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_depth = "16"
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("saved", OUT)
