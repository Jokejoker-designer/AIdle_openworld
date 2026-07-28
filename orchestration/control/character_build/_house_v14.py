import hashlib, json, math
from pathlib import Path
import bpy
from mathutils import Vector

JOB="HOUSE_FIDELITY_V14"
GAME=Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules\cozy_house_small_A.glb")
CAT=Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()

def mat(n,rgb,rough=0.55,emit=0.0):
    m=bpy.data.materials.new(n); m.use_nodes=True; m.diffuse_color=(*rgb,1)
    b=next((x for x in m.node_tree.nodes if x.type=="BSDF_PRINCIPLED"),None)
    if b:
        b.inputs["Base Color"].default_value=(*rgb,1)
        if "Roughness" in b.inputs: b.inputs["Roughness"].default_value=rough
        if emit>0:
            if "Emission Color" in b.inputs: b.inputs["Emission Color"].default_value=(*rgb,1)
            if "Emission Strength" in b.inputs: b.inputs["Emission Strength"].default_value=emit
    return m

def setm(o,m):
    o.data.materials.clear(); o.data.materials.append(m)
    try: bpy.ops.object.shade_smooth()
    except: pass

def cube(n,loc,sc,m):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o=bpy.context.active_object; o.name=n; o.scale=sc
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    setm(o,m)
    try:
        bpy.ops.object.modifier_add(type="BEVEL")
        md=o.modifiers[-1]; md.width=0.04; md.segments=2
        bpy.ops.object.modifier_apply(modifier=md.name)
    except: pass
    return o

def sph(n,loc,r,m,sc=(1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=12, ring_count=8)
    o=bpy.context.active_object; o.name=n; o.scale=sc
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    setm(o,m); return o

def cyl(n,loc,r,d,m):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=12)
    o=bpy.context.active_object; o.name=n
    setm(o,m); return o

def roof_prism(name, m):
    """Wedge roof: NO object rotation. Verts in Blender Z-up.
    Cross-section: front eave y=+0.7 z=1.15, peak y=0 z=1.85, back eave y=-0.7 z=1.15
    X from -0.8 to 0.8
    """
    mesh = bpy.data.meshes.new(name)
    # 6 verts of triangular prism
    verts = [
        (-0.85,  0.72, 1.12),  # 0 front-left eave
        ( 0.85,  0.72, 1.12),  # 1 front-right eave
        (-0.85, -0.72, 1.12),  # 2 back-left eave
        ( 0.85, -0.72, 1.12),  # 3 back-right eave
        (-0.85,  0.00, 1.88),  # 4 peak-left
        ( 0.85,  0.00, 1.88),  # 5 peak-right
    ]
    faces = [
        (0,1,5,4),  # front slope
        (2,4,5,3),  # back slope
        (0,4,2),    # left gable
        (1,3,5),    # right gable
        (0,2,3,1),  # bottom
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    setm(o, m)
    return o

def scallop_on_front(name, u, t, m):
    """Place flat-ish sphere on front roof face without rotation.
    Front face: lerp eave (y=0.72,z=1.12) to peak (y=0,z=1.88)
    u in [-1,1] along X, t in [0,1] eave->peak
    """
    y = 0.72 * (1-t) + 0.0 * t
    z = 1.12 * (1-t) + 1.88 * t + 0.06  # sit above surface
    x = u * 0.75
    # use small cube flattened as scallop (no rotation needed if we shape it)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.10, location=(x,y,z), segments=10, ring_count=8)
    o=bpy.context.active_object; o.name=name
    # Flatten slightly in local Z only (vertical squash) — reads as tile from above
    o.scale=(1.4, 1.15, 0.35)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    setm(o,m)
    return o

bpy.ops.wm.read_factory_settings(use_empty=True)
Mw=mat("M_wall",(0.98,0.88,0.72),0.72)
Mb=mat("M_base",(0.68,0.50,0.90),0.62)
Mr1=mat("M_roof_a",(1.0,0.58,0.18),0.45)
Mr2=mat("M_roof_b",(1.0,0.80,0.22),0.45)
Mr3=mat("M_roof_c",(0.98,0.68,0.32),0.48)
Mr=mat("M_ridge",(0.99,0.92,0.78),0.55)
Md=mat("M_door",(0.70,0.38,0.16),0.5)
Mf=mat("M_frame",(0.90,0.62,0.40),0.5)
Me=mat("M_emit",(1.0,0.72,0.22),0.3,emit=4.5)
Mp=mat("M_pot",(0.88,0.50,0.28),0.55)
Ml=mat("M_lav",(0.66,0.38,0.88),0.55)
Mleaf=mat("M_leaf",(0.32,0.68,0.30),0.55)
Mstem=mat("M_stem",(0.30,0.48,0.26),0.6)
Mmail=mat("M_mail",(0.62,0.38,0.88),0.4)
Ms=mat("M_stone",(0.82,0.76,0.68),0.7)
Msmoke=mat("M_smoke",(0.76,0.52,0.90),1.0,emit=0.2)
Mchim=mat("M_chim",(0.97,0.90,0.82),0.65)
Mdark=mat("M_dark",(0.32,0.16,0.10),0.8)
Mcurt=mat("M_curt",(0.74,0.38,0.84),0.6)
Mknob=mat("M_knob",(1.0,0.86,0.32),0.25,emit=0.5)

cube("Base",(0,0,0.06),(2.0,1.8,0.14),Mb)
cube("Body",(0,0,0.62),(1.30,1.12,1.00),Mw)
cube("Front",(0,0.52,0.48),(0.95,0.16,0.72),Mw)
roof_prism("RoofSolid", Mr1)

mats=[Mr1,Mr2,Mr3]
for row in range(6):
    t=(row+0.5)/6.0
    for col in range(8):
        u=((col-3.5)/3.5)
        if row%2: u += 0.08/0.75
        if abs(u)>1.0: continue
        scallop_on_front(f"Sc{row}_{col}", u, t, mats[(row+col)%3])

for i,x in enumerate([-0.45,-0.22,0,0.22,0.45]):
    sph(f"Rd{i}",(x,0,1.95),0.08,Mr,(1.15,1.0,0.7))

cube("Chim",(0.38,-0.12,1.95),(0.20,0.20,0.38),Mchim)
cube("ChimC",(0.38,-0.12,2.16),(0.26,0.26,0.07),Mchim)
for i,(dx,dy,dz,s) in enumerate([(0,0,0.08,0.07),(0.06,0.04,0.18,0.09),(0.12,0.08,0.28,0.07),(0.18,0.12,0.36,0.05)]):
    sph(f"Sm{i}",(0.38+dx,-0.12+dy,2.22+dz),s,Msmoke)

cube("DFill",(0,0.50,0.42),(0.50,0.12,0.75),Mw)
cube("DFr",(0,0.58,0.45),(0.46,0.05,0.78),Mf)
cube("Door",(0,0.62,0.43),(0.34,0.05,0.62),Md)
sph("DArch",(0,0.64,0.82),0.20,Mf,(1.0,0.30,0.55))
sph("Knob",(0.11,0.68,0.43),0.04,Mknob)
cube("S1",(0,0.76,0.10),(0.38,0.16,0.07),Mf)
cube("S2",(0,0.90,0.05),(0.30,0.12,0.05),Mf)

for nm,x,z,rr in [("W1",-0.36,0.62,0.09),("W2",0.36,0.42,0.08),("W3",-0.26,0.92,0.085),("W4",0,1.12,0.095)]:
    # window as sphere flush on front (y=0.58)
    sph(f"{nm}g",(x,0.62,z),rr,Me)
    cyl(f"{nm}f",(x,0.58,z),rr+0.02,0.04,Mf)  # thin disc approx via short cyl default Z

cube("SF",(0.62,0,0.65),(0.12,0.50,0.40),Mdark)
cube("SFr",(0.66,0,0.65),(0.07,0.54,0.44),Mf)
cube("SG",(0.70,0,0.65),(0.04,0.46,0.36),Me)
cube("CL",(0.64,-0.16,0.68),(0.04,0.07,0.32),Mcurt)
cube("CR",(0.64,0.18,0.68),(0.04,0.07,0.32),Mcurt)

cyl("MP",(0.28,0.76,0.15),0.022,0.18,Mmail)
cube("MB",(0.28,0.76,0.28),(0.14,0.10,0.11),Mmail)
cube("MF",(0.36,0.76,0.32),(0.03,0.02,0.07),Ml)
cyl("PB",(-0.68,0.68,0.15),0.10,0.15,Mp)
for i,a in enumerate([0,1.25,2.5,3.8,5.0]):
    x=-0.68+0.04*math.cos(a); y=0.68+0.04*math.sin(a)
    cyl(f"St{i}",(x,y,0.30),0.011,0.20,Mstem)
    sph(f"Bl{i}",(x,y,0.44),0.045,Ml,(0.7,0.7,1.3))
cyl("PS1",(0.48,0.76,0.12),0.05,0.09,Mp); sph("PL1",(0.48,0.76,0.22),0.055,Mleaf)
cyl("PS2",(0.60,0.68,0.11),0.045,0.08,Mp); sph("PL2",(0.60,0.68,0.20),0.045,Ml)
for i,(x,y,s) in enumerate([(-0.1,1.1,0.12),(0.08,1.28,0.1),(-0.02,1.45,0.09)]):
    sph(f"Sn{i}",(x,y,0.03),s,Ms,(1.3,1.0,0.22))

bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0,0,0))
root=bpy.context.active_object; root.name="MOD_cozy_house_small_A"
for o in list(bpy.data.objects):
    if o!=root and o.type=="MESH" and o.parent is None:
        mw=o.matrix_world.copy(); o.parent=root; o.matrix_world=mw

bpy.ops.export_scene.gltf(filepath=str(GAME),export_format="GLB",use_selection=False,export_apply=True,export_cameras=False,export_lights=False,export_materials="EXPORT")
print("HOUSE_V14", GAME.stat().st_size, sha(GAME)[:16])
data=json.loads(CAT.read_text(encoding="utf-8"))
for m in data.get("modules",[]):
    if m.get("module_id")=="cozy_house_small_A":
        m["glb_sha256"]=sha(GAME); m["bytes"]=GAME.stat().st_size; m["source"]=JOB; m["visual"]="mockup_house_v14_prism"
CAT.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("HOUSE_V14_OK")
