import hashlib, json, math
from pathlib import Path
import bpy
from mathutils import Vector, Euler

JOB="HOUSE_FIDELITY_V13"
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

def cube(n,loc,sc,m):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o=bpy.context.active_object; o.name=n; o.scale=sc
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    setm(o,m)
    try:
        bpy.ops.object.modifier_add(type="BEVEL")
        md=o.modifiers[-1]; md.width=0.05; md.segments=3
        bpy.ops.object.modifier_apply(modifier=md.name)
    except: pass
    bpy.ops.object.shade_smooth()
    return o

def sph(n,loc,r,m,sc=(1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=14, ring_count=10)
    o=bpy.context.active_object; o.name=n; o.scale=sc
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    setm(o,m); bpy.ops.object.shade_smooth(); return o

def cyl(n,loc,r,d,m,rot=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=14)
    o=bpy.context.active_object; o.name=n
    if rot:
        o.rotation_euler=Euler(rot,"XYZ")
        bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
    setm(o,m); bpy.ops.object.shade_smooth(); return o

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

# Build entirely at origin with NO parent until export; use Godot-friendly proportions
# Gable house: body + solid roof as joined mesh with scallops as flat discs in local coords
# Blender Z-up: ground XY, up Z. glTF exporter converts to Y-up.
cube("Base",(0,0,0.06),(2.0,1.8,0.14),Mb)
cube("Body",(0,0,0.65),(1.30,1.15,1.05),Mw)
cube("Front",(0,0.52,0.50),(0.95,0.16,0.75),Mw)

# SOLID roof: use a cone stretched for gable-ish look + two slope boxes WITHOUT leaving open book
# Roof mass - wide wedge via scaled cube rotated 0: just a triangular prism approximation
# Front slope
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,0.28,1.35))
o=bpy.context.active_object; o.name="RoofF"
o.scale=(1.55,0.90,0.18); o.rotation_euler=Euler((math.radians(38),0,0),"XYZ")
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
setm(o,Mr1); bpy.ops.object.shade_smooth()
# Back slope  
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,-0.28,1.35))
o=bpy.context.active_object; o.name="RoofB"
o.scale=(1.55,0.90,0.18); o.rotation_euler=Euler((math.radians(-38),0,0),"XYZ")
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
setm(o,Mr2); bpy.ops.object.shade_smooth()
# Peak
cube("Peak",(0,0,1.65),(1.50,0.25,0.15),Mr)

# Scallops as FLAT discs (scale Z small) WITHOUT rotation — place along roof surface by position only
# Front roof surface approx z = 1.15 + 0.55*(0.55-y)/0.55 for y in [0,0.55]
mats=[Mr1,Mr2,Mr3]
for row in range(6):
    t=row/5.0
    y=0.50 - t*0.48
    z=1.18 + t*0.48
    for col in range(8):
        x=(col-3.5)*0.17
        if row%2: x+=0.08
        if abs(x)>0.72: continue
        m=mats[(row+col)%3]
        # disc flat in XY (horizontal) then we'll accept slight error OR use ico
        bpy.ops.mesh.primitive_cylinder_add(radius=0.11, depth=0.06, location=(x,y,z), vertices=12)
        o=bpy.context.active_object; o.name=f"Sc{row}_{col}"
        # tip disc to follow slope: rotate X so disc is parallel to roof (~38 deg)
        o.rotation_euler=Euler((math.radians(52),0,0),"XYZ")  # 90-38
        bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
        setm(o,m); bpy.ops.object.shade_smooth()

for i,x in enumerate([-0.45,-0.22,0,0.22,0.45]):
    sph(f"Rd{i}",(x,0,1.78),0.08,Mr,(1.15,1.0,0.7))

cube("Chim",(0.38,-0.15,1.90),(0.20,0.20,0.40),Mchim)
cube("ChimC",(0.38,-0.15,2.12),(0.26,0.26,0.07),Mchim)
for i,(dx,dy,dz,s) in enumerate([(0,0,0.1,0.07),(0.06,0.05,0.2,0.09),(0.12,0.1,0.3,0.07),(0.2,0.14,0.38,0.05)]):
    sph(f"Sm{i}",(0.38+dx,-0.15+dy,2.18+dz),s,Msmoke)

cube("DFill",(0,0.50,0.45),(0.50,0.12,0.80),Mw)
cube("DFr",(0,0.58,0.48),(0.46,0.05,0.82),Mf)
cube("Door",(0,0.62,0.46),(0.34,0.05,0.66),Md)
sph("DArch",(0,0.64,0.88),0.20,Mf,(1.0,0.30,0.55))
sph("Knob",(0.11,0.68,0.46),0.04,Mknob)
cube("S1",(0,0.76,0.10),(0.38,0.16,0.07),Mf)
cube("S2",(0,0.90,0.05),(0.30,0.12,0.05),Mf)

for nm,x,z,rr in [("W1",-0.36,0.65,0.095),("W2",0.36,0.45,0.085),("W3",-0.26,0.98,0.09),("W4",0,1.20,0.10)]:
    cyl(f"{nm}f",(x,0.60,z),rr+0.02,0.04,Mf,rot=(math.pi/2,0,0))
    sph(f"{nm}g",(x,0.64,z),rr,Me)

cube("SF",(0.62,0,0.70),(0.12,0.50,0.42),Mdark)
cube("SFr",(0.66,0,0.70),(0.07,0.54,0.46),Mf)
cube("SG",(0.70,0,0.70),(0.04,0.46,0.38),Me)
cube("CL",(0.64,-0.16,0.74),(0.04,0.07,0.34),Mcurt)
cube("CR",(0.64,0.18,0.74),(0.04,0.07,0.34),Mcurt)

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

# Parent all to empty without re-applying location (meshes already world-correct)
bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0,0,0))
root=bpy.context.active_object; root.name="MOD_cozy_house_small_A"
for o in list(bpy.data.objects):
    if o!=root and o.type=="MESH" and o.parent is None:
        mw=o.matrix_world.copy()
        o.parent=root
        o.matrix_world=mw

out=GAME
bpy.ops.export_scene.gltf(filepath=str(out),export_format="GLB",use_selection=False,export_apply=True,export_cameras=False,export_lights=False,export_materials="EXPORT")
print("HOUSE_V13", out.stat().st_size, sha(out)[:16])
data=json.loads(CAT.read_text(encoding="utf-8"))
for m in data.get("modules",[]):
    if m.get("module_id")=="cozy_house_small_A":
        m["glb_sha256"]=sha(out); m["bytes"]=out.stat().st_size; m["source"]=JOB; m["visual"]="mockup_house_v13"
CAT.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("HOUSE_V13_OK")
