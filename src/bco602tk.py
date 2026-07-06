import bpy
import bmesh
import random
import math
import string
import os

def cleanupSceneAndMemory():
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
        
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    for _ in range(5):
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

def select(objName):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[objName].select_set(True)

def activate(objName):
    bpy.context.view_layer.objects.active = bpy.data.objects[objName]

def mode(mode_name):
    bpy.ops.object.mode_set(mode = mode_name)
    if mode_name == "EDIT":
        bpy.ops.mesh.select_all(action = "DESELECT")

def selection_mode(type):
    bpy.ops.mesh.select_mode(type = type) 
    
def select_all(): 
    bpy.ops.object.select_all(action='SELECT')
    
def coords(objName, space='GLOBAL'):
    obj = bpy.data.objects[objName]
    if obj.mode == 'EDIT':
        v = bmesh.from_edit_mesh(obj.data).verts
    elif obj.mode == 'OBJECT':
        v = obj.data.vertices
    if space == 'GLOBAL':
        return [(obj.matrix_world @ v.co).to_tuple() for v in v]
    elif space == 'LOCAL':
        return [v.co.to_tuple() for v in v]
    
def in_bbox(lbound, ubound, v, buffer=0.0001):
    return lbound[0] - buffer <= v[0] <= ubound[0] + buffer and \
        lbound[1] - buffer <= v[1] <= ubound[1] + buffer and \
        lbound[2] - buffer <= v[2] <= ubound[2] + buffer

def makeMaterial(name, diffuse = (1, 1, 1, 1) , metallic = 0.0, specular = 0.8, roughness = 0.2):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.specular_intensity = specular
    mat.metallic = metallic
    mat.roughness = roughness
    return mat
 
def setMaterial(ob, mat):
    me = ob.data
    me.materials.append(mat)

def setSmooth(obj, level = None, smooth = True):
    if level:
        modifier = obj.modifiers.new('Subsurf', 'SUBSURF')
        modifier.levels = level
        modifier.render_levels = level

    mesh = obj.data
    for p in mesh.polygons:
        p.use_smooth = smooth

class sel:
    """Wrapper class for transformations on SELECTED objects"""
    def translate(v):
        bpy.ops.transform.translate(value=v, constraint_axis=(True, True, True))

    def scale(v):
        bpy.ops.transform.resize(value= v)

    def rotate_x(v):
        bpy.ops.transform.rotate(value=v, orient_axis='X')

    def rotate_y(v):
        bpy.ops.transform.rotate(value=v, orient_axis='Y')

    def rotate_z(v):
        bpy.ops.transform.rotate(value=v, orient_axis='Z')
        
    def transform_apply():
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

class act:
    """Wrapper class for transformations on the ACTIVE object"""
    def location(v):
        bpy.context.object.location = v
        
    def scale(v):
        bpy.context.object.scale = v
        
    def rotation(v):
        bpy.context.object.rotation_euler = v

    def rename(objName):
        bpy.context.object.name = objName
        
    def dimension(v):
        bpy.context.object.dimensions = v
        
    def select_by_loc(lbound=(0, 0, 0), ubound=(0, 0, 0), select_mode='VERT', coords='GLOBAL'):
        selection_mode(select_mode)
        world = bpy.context.object.matrix_world

        bm = bmesh.from_edit_mesh(bpy.context.object.data)
        bm.faces.ensure_lookup_table()

        verts = []
        to_select = []

        if select_mode == 'VERT':
            if coords == 'GLOBAL':
                [verts.append((world @ v.co).to_tuple()) for v in bm.verts]
            elif coords == 'LOCAL':
                [verts.append(v.co.to_tuple()) for v in bm.verts]

            [to_select.append(in_bbox(lbound, ubound, v)) for v in verts]
            for vertObj, select in zip(bm.verts, to_select):
                vertObj.select = select

        if select_mode == 'EDGE':
            if coords == 'GLOBAL':
                [verts.append([(world @ v.co).to_tuple() for v in e.verts]) for e in bm.edges]
            elif coords == 'LOCAL':
                [verts.append([v.co.to_tuple() for v in e.verts]) for e in bm.edges]

            [to_select.append(all(in_bbox(lbound, ubound, v) for v in e)) for e in verts]
            for edgeObj, select in zip(bm.edges, to_select):
                edgeObj.select = select

        if select_mode == 'FACE':
            if coords == 'GLOBAL':
                [verts.append([(world @ v.co).to_tuple() for v in f.verts]) for f in bm.faces]
            elif coords == 'LOCAL':
                [verts.append([v.co.to_tuple() for v in f.verts]) for f in bm.faces]

            [to_select.append(all(in_bbox(lbound, ubound, v) for v in f)) for f in verts]
            for faceObj, select in zip(bm.faces, to_select):
                faceObj.select = select    

class spec:
    """Wrapper class for transformations on SPECIFIED objects by name"""
    def scale(objName, v):
        bpy.data.objects[objName].scale = v

    def location(objName, v):
        bpy.data.objects[objName].location = v

    def rotation(objName, v):
        bpy.data.objects[objName].rotation_euler = v
        
class create:
    """Helper utilities for instantiating basic scene components"""
    def cube(objName):
        bpy.ops.mesh.primitive_cube_add(size=0.5, location=(0, 0, 0))
        act.rename(objName)

    def sphere(objName):
        bpy.ops.mesh.primitive_uv_sphere_add(location=(0, 0, 0))
        act.rename(objName)

    def cone(objName):
        bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2, location=(0, 0, 0))
        act.rename(objName)
              
    def plane(objName):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
        act.rename(objName)

    def sphere2(objName: str, radius: float, location: tuple):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location)
        act.rename(objName)
        
    def light(origin, target=None, lamptype='POINT', energy=1, color=(1,1,1)):
        bpy.ops.object.light_add(type=lamptype, location = origin)
        obj = bpy.context.object
        obj.rotation_euler[0] = 0.174533
        obj.data.type = lamptype
        obj.data.energy = energy
        obj.data.color = color        
        if target:
            trackToConstraint(obj, target)
        return obj
    
    def camera(origin, target=None, lens=35, clip_start=0.1, clip_end=200, type='PERSP', ortho_scale=6):
        bpy.ops.object.camera_add(location=origin)        
        obj = bpy.context.object
        obj.data.lens = lens
        obj.data.clip_start = clip_start
        obj.data.clip_end = clip_end
        obj.data.type = type 
        if type == 'ORTHO':
            obj.data.ortho_scale = ortho_scale            
        if target:
            trackToConstraint(obj, target)        
        return obj 

def delete(objName):
    select(objName)
    bpy.ops.object.delete(use_global=False)

def delete_all():
    if len(bpy.data.objects) != 0:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for mat in bpy.data.materials:
        if mat.users == 0:
            bpy.data.materials.remove(mat)

    for cam in bpy.data.cameras:
        if cam.users == 0:
            bpy.data.cameras.remove(cam)

    for lamp in bpy.data.lights:
        if lamp.users == 0:
            bpy.data.lights.remove(lamp)
        
def random_string(length=5):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))        
        
def createColorList(count: int, alpha: float):
    colorList = []
    for i in range(count):
        randR = random.uniform(0.0, 1.0)
        randG = random.uniform(0.0, 1.0)
        randB = random.uniform(0.0, 1.0)
        nameOfColorRandom = random_string()
        colorList.append(makeMaterial(nameOfColorRandom, (randR, randG, randB, alpha), 0.0, 0.5, 0.2))
    return colorList

def deleteAllObjectInScene():
    try:
        mode("OBJECT") 
        delete_all() 
    except Exception:
        print("No objects found in the viewport layers.")
      
def checkIntersection(pos, radius, spheres):
    radiusSquare = radius * radius
    for otherPos, otherRadius in spheres:
        minDistanceSquare = (radius + otherRadius) ** 2
        dx = pos[0] - otherPos[0]
        dy = pos[1] - otherPos[1]
        dz = pos[2] - otherPos[2]
        distanceSqaure = dx*dx + dy*dy + dz*dz
        
        if distanceSqaure < (minDistanceSquare):
            return False
    return True

def generateSpheres(min_radius, max_radius, volume_size, spheres, colors, attempts, segments):
    radius = random.uniform(min_radius, max_radius)
    x = random.uniform(-volume_size/2 + radius, volume_size/2 - radius)
    y = random.uniform(-volume_size/2 + radius, volume_size/2 - radius)
    z = random.uniform(radius, volume_size - radius)
    pos = (x, y, z)
    
    if checkIntersection(pos, radius, spheres):
        create.sphere2(f"Sphere{attempts}", radius, pos)
        bpy.ops.rigidbody.object_add()
        bpy.context.object.rigid_body.type = 'ACTIVE'
        bpy.context.object.rigid_body.collision_shape = 'SPHERE'
        bpy.context.object.rigid_body.mass = 1
        bpy.context.object.rigid_body.restitution = 0.5
        bpy.context.object.rigid_body.friction = 0.5
        
        spheres.append((pos, radius))

        ob = bpy.context.object
        me = ob.data
        
        for mat in colors:
            me.materials.append(mat)
            
        stepAngle = 2 * math.pi / segments
        for i in range(segments):
            mode("EDIT")
            act.select_by_loc((0,-radius,-radius), (radius,-radius/2+0.02,radius), "FACE", "LOCAL")
            ob.active_material_index = i
            bpy.ops.object.material_slot_assign()
            mode("OBJECT")
            sel.rotate_z(stepAngle)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
     
        rx = math.radians(random.randrange(0, 360))
        ry = math.radians(random.randrange(0, 360))
        rz = math.radians(random.randrange(0, 360))
        
        sel.rotate_x(rx)
        sel.rotate_y(ry)  
        sel.rotate_z(rz)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                
def checkIntersectionJelly(pos, radius, spheres, margin=0.2):
    for otherPos, otherRadius in spheres:
        minDistance = radius + otherRadius + margin
        dx = pos[0] - otherPos[0]
        dy = pos[1] - otherPos[1]
        dz = pos[2] - otherPos[2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < minDistance:
            return False
    return True

def generateSpheresJelly(min_radius, max_radius, volume_size, spheres, attempts):
    radius = random.uniform(min_radius, max_radius)
    safe_border = volume_size/2 - radius - 0.5 
    
    x = random.uniform(-safe_border, safe_border)
    y = random.uniform(-safe_border, safe_border)
    z = 5
    pos = (x, y, z)
    
    if checkIntersectionJelly(pos, radius, spheres, margin=0.15):
        create.sphere2(f"JellySphere_{attempts}", radius, pos)
        spheres.append((pos, radius))

        obj = bpy.context.object
        
        sb_mod = obj.modifiers.new(name='Softbody', type='SOFT_BODY')
        sb = sb_mod.settings
        
        sb.use_goal = False
        sb.use_self_collision = True
        sb.use_stiff_quads = True
        sb.friction = 1
        sb.pull = 0.85
        sb.push = 0.85
        sb.damping = 0.1
        sb.shear = 0.9
        sb.bend = 0.9
        sb.mass = 1.0
        
        ss_mod = obj.modifiers.new(name='Subsurf', type='SUBSURF')
        ss_mod.levels = 2
        ss_mod.render_levels = 4

        r, g, b = [random.random() for _ in range(3)]
        alpha = random.uniform(0.1, 0.7)
        mat_name = f"JellyMat_{attempts}"
        mat = makeMaterial(mat_name, (r, g, b, alpha), 0.3, 0.9, 0.05)
        mat.blend_method = 'BLEND'
        mat.use_screen_refraction = True
        
        setMaterial(obj, mat)
        setSmooth(obj, smooth=True)
      
def generateGroundForScene():
    black = makeMaterial('Black', (0, 0, 0, 1.0), 0, 0.8, 0.2)
    white = makeMaterial('White', (1, 1, 1, 1.0), 0, 0.8, 0.2)

    create.plane('Ground')
    obj = bpy.context.object
    
    bpy.ops.object.modifier_add(type='COLLISION')
    obj.collision.damping = 0.03

    mode("EDIT")
    act.select_by_loc((-1, -1, 0), (1, 1, 0), 'EDGE', 'GLOBAL')
    bpy.ops.mesh.subdivide(number_cuts=9)
    
    ob = bpy.context.object
    me = ob.data
    
    if len(me.materials) == 0:
        me.materials.append(white)
        me.materials.append(black)
    for _ in range(2):
        for _ in range(5):
            for _ in range(5):
                mode("EDIT")    
                act.select_by_loc((-0.5, -0.5, -10), (-0.4, -0.4, 0), 'FACE', 'GLOBAL')
                ob.active_material_index = 1
                bpy.ops.object.material_slot_assign()
                mode("OBJECT")
                sel.translate((-0.2, 0, 0))
            sel.translate((1.0, -0.2, 0))
        sel.translate((-0.1, 0.9, 0))
    obj.location = (0, 0, 0)
    sel.scale((10, 10, 1))
    
def createPastelMaterial():
    mat = bpy.data.materials.new(name="PastelMat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    
    if principled:
        r = random.uniform(0.4, 1.0)
        g = random.uniform(0.4, 1.0)
        b = random.uniform(0.4, 1.0)
        
        principled.inputs['Base Color'].default_value = (r, g, b, 1)
        principled.inputs['Roughness'].default_value = 0.9
        principled.inputs['Specular IOR Level'].default_value = 0.5
        
    return mat

def createFinalScene(snowQty, animationTime):
    # NOTE: Set the absolute path to your environment workspace root directory
    BASE_PATH = "/home/user/workspace/assets"
    OBJ_NAME = "snowFlakeXobj.obj"
    IMAGE_NAME = "snowy.png" 

    OBJ_FULL_PATH = os.path.join(BASE_PATH, OBJ_NAME)
    BG_IMAGE_PATH = os.path.join(BASE_PATH, IMAGE_NAME)
    
    cleanupSceneAndMemory()
    
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
    bpy.context.scene.frame_end = animationTime
    
    if bpy.context.scene.rigidbody_world:
        bpy.context.scene.rigidbody_world.point_cache.frame_end = animationTime

    create.plane("BackgroundPlane")
    bg_plane = bpy.context.object
    bg_plane.location = (0, 10, 2) 
    bg_plane.rotation_euler = (math.radians(90), 0, 0)
    sel.scale((24, 1, 16))
    
    bg_mat = bpy.data.materials.new(name="BgMat")
    bg_mat.use_nodes = True
    nodes = bg_mat.node_tree.nodes
    links = bg_mat.node_tree.links
    nodes.clear()
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_tex = nodes.new(type='ShaderNodeTexImage')
    
    try:
        if os.path.exists(BG_IMAGE_PATH):
            img = bpy.data.images.load(BG_IMAGE_PATH)
            node_tex.image = img
        else:
            print(f"Background texture target resource missing.")
    except Exception:
        pass

    links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    links.new(node_tex.outputs['Color'], node_bsdf.inputs['Base Color'])
    links.new(node_tex.outputs['Color'], node_bsdf.inputs['Emission Color'])
    node_bsdf.inputs['Emission Strength'].default_value = 1.0
    
    if bg_plane.data.materials: 
        bg_plane.data.materials[0] = bg_mat
    else: 
        bg_plane.data.materials.append(bg_mat)

    bpy.ops.object.text_add(location=(-4, 0, 7)) 
    text_obj = bpy.context.object
    text_obj.data.body = "2026"
    text_obj.data.extrude = 0.2
    text_obj.data.size = 4
    text_obj.rotation_euler[0] = 1.5708
    text_obj.name = "Text_2026"
    
    red_mat = makeMaterial("RedText", (0.8, 0.05, 0.05, 1.0), metallic=0.5, roughness=0.4)
    text_obj.data.materials.append(red_mat)
    
    bpy.ops.object.convert(target='MESH')
    bpy.ops.rigidbody.object_add()
    text_obj.rigid_body.type = 'PASSIVE'
    text_obj.rigid_body.kinematic = True 
    text_obj.rigid_body.collision_shape = 'MESH'
    
    text_obj.location.z = 7
    text_obj.keyframe_insert(data_path="location", frame=1)
    text_obj.location.z = 0
    text_obj.keyframe_insert(data_path="location", frame=animationTime)
    
    if text_obj.animation_data and text_obj.animation_data.action:
        for fcurve in text_obj.animation_data.action.fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'LINEAR'
    
    snowflake_ref = None
    if os.path.exists(OBJ_FULL_PATH):
        try:
            if bpy.app.version >= (4, 0, 0):
                bpy.ops.wm.obj_import(filepath=OBJ_FULL_PATH)
            else:
                bpy.ops.import_scene.obj(filepath=OBJ_FULL_PATH)
            snowflake_ref = bpy.context.selected_objects[0]
            snowflake_ref.name = "Snowflake_Ref"
            snowflake_ref.scale = (0.8, 0.8, 0.8)
            
            if snowflake_ref.rigid_body:
                bpy.ops.rigidbody.object_remove()
        except Exception:
            pass

    if snowflake_ref is None:
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.4, subdivisions=1)
        snowflake_ref = bpy.context.object
        snowflake_ref.name = "Snowflake_Dummy"
    
    snow_mat = makeMaterial("Snow", (1.0, 1.0, 1.0, 1.0), metallic=0.0, roughness=0.1)
    if snowflake_ref.data.materials: 
        snowflake_ref.data.materials[0] = snow_mat
    else: 
        snowflake_ref.data.materials.append(snow_mat)
        
    snowflake_ref.location = (0, 0, 100) 
    snowflake_ref.hide_render = True
    
    for i in range(snowQty):
        new_flake = snowflake_ref.copy()
        if snowflake_ref.data:
            new_flake.data = snowflake_ref.data.copy()
        bpy.context.collection.objects.link(new_flake)
        
        s = random.uniform(0.6, 1.2)
        new_flake.scale = (s, s, s)

        new_flake.location = (
            random.uniform(-25, 10),      # Offset bounds slightly westward to handle drag bias
            random.uniform(-18, 5),       
            random.uniform(-5, 45)        
        )
        
        new_flake.rotation_euler = (random.uniform(0, 3.14), random.uniform(0, 3.14), random.uniform(0, 3.14))
        new_flake.hide_render = False
        
        bpy.context.view_layer.objects.active = new_flake
        bpy.ops.rigidbody.object_add()
        new_flake.rigid_body.type = 'ACTIVE'
        new_flake.rigid_body.mass = 0.01 
        new_flake.rigid_body.linear_damping = 0.1
        new_flake.rigid_body.angular_damping = 0.1
        new_flake.rigid_body.collision_shape = 'CONVEX_HULL'

    bpy.ops.object.effector_add(type='WIND', location=(-25, 0, 10))
    wind = bpy.context.object
    wind.rotation_euler = (0, math.radians(120), 0)
    wind.field.strength = 50.0 
    
    bpy.ops.object.effector_add(type='TURBULENCE', location=(0, -5, 2))
    turb = bpy.context.object
    turb.field.strength = 20.0 
    turb.field.flow = 0.5
    turb.field.size = 5.0
    
    bpy.context.scene.rigidbody_world.point_cache.frame_end = animationTime

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'