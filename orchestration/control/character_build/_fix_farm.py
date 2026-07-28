from pathlib import Path
import hashlib, json, math, sys
import bpy
from mathutils import Euler

JOB = "TOWN_FIDELITY_FARM_FIX"
GAME_MOD = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules")
CATALOG = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()

def mat(name, rgb, rough=0.55):
    m=bpy.data.materials.new(name); m.use_nodes=True
    m.diffuse_color=(*rgb,1)
    bsdf=next((n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED"),None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value=(*rgb,1)
        if "Roughness" in bsdf.inputs: bsdf.inputs["Roughness"].default_value=rough
    return m

def fin(o,m,bevel=0.04):
    o.data.materials.clear(); o.data.materials.append(m)
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    try:
        bpy.ops.object.modifier_add(type="BEVEL")
        md=o.modifiers[-1]; md.width=bevel; md.segments=3
        bpy.ops.object.modifier_apply(modifier=md.name)
    except: pass
    try: bpy.ops.object.shade_smooth()
    except: pass
    o.select_set(False); return o

def cube(name, loc, sc, m, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o=bpy.context.active_object; o.name=name; o.scale=sc
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return fin(o,m,bevel)

def cyl(name, loc, r, d, m):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=10)
    o=bpy.context.active_object; o.name=name
    return fin(o,m,0)

def sph(name, loc, r, m):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=12, ring_count=8)
    o=bpy.context.active_object; o.name=name
    return fin(o,m,0)

bpy.ops.wm.read_factory_settings(use_empty=True)
Msoil=mat("M_soil",(0.45,0.32,0.22),0.8)
Mwood=mat("M_wood",(0.78,0.58,0.40),0.55)
Mg=mat("M_crop",(0.45,0.72,0.42),0.55)
bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0,0,0))
root=bpy.context.active_object; root.name="MOD_cozy_farm_plot_A"
cube("Soil",(0,0,0.06),(1.2,0.9,0.12),Msoil,0.04)
for i,(loc,sc) in enumerate([
    ((0,0.48,0.1),(1.25,0.08,0.12)),
    ((0,-0.48,0.1),(1.25,0.08,0.12)),
    ((0.62,0,0.1),(0.08,0.95,0.12)),
    ((-0.62,0,0.1),(0.08,0.95,0.12)),
]):
    cube(f"Rail{i}",loc,sc,Mwood,0.02)
for i,x in enumerate([-0.35,0,0.35]):
    for j,y in enumerate([-0.25,0.1,0.3]):
        cyl(f"C{i}_{j}",(x,y,0.18),0.03,0.12,Mg)
        sph(f"L{i}_{j}",(x,y,0.28),0.05,Mg)
for o in list(bpy.data.objects):
    if o!=root and o.type=="MESH" and o.parent is None:
        o.parent=root; o.matrix_parent_inverse.identity()
out=GAME_MOD/"cozy_farm_plot_A.glb"
bpy.ops.export_scene.gltf(filepath=str(out),export_format="GLB",use_selection=False,export_apply=True,export_cameras=False,export_lights=False,export_materials="EXPORT")
print("FARM_OK", out.stat().st_size, sha(out)[:16])
data=json.loads(CATALOG.read_text(encoding="utf-8"))
for m in data.get("modules",[]):
    if m.get("module_id")=="cozy_farm_plot_A":
        m["glb_sha256"]=sha(out); m["bytes"]=out.stat().st_size; m["source"]=JOB; m["visual"]="mockup_fidelity_farm_fix"
CATALOG.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
