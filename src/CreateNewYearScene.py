import bpy
import random
import math
import os

# Settings
snowQty = 1000
animationTime = 300

# Get Toolkit
tk = bpy.data.texts["bco602tk.py"].as_module()

tk.createFinalScene(1000,300)

# Render Settings
scene = bpy.context.scene

# Camera
tk.create.camera((0, -22, 2.5), lens=48, type='PERSP')
camera = bpy.context.object
camera.rotation_euler = (math.radians(90), 0, 0)
bpy.context.scene.camera = camera
    
# Light
tk.create.light((0, -5, 15), lamptype='SUN', energy=8, color=(1, 1, 1))

scene.camera = camera

scene.frame_start = 1
scene.frame_end = animationTime
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.fps = 24

scene.render.filepath = "C:/Users/<YOUR_USERNAME>/Desktop/Result.mp4" 
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.eevee.use_raytracing = True
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.ffmpeg.ffmpeg_preset = 'GOOD'

# Cache Cleaning
bpy.ops.ptcache.free_bake_all()
bpy.ops.ptcache.bake_all(bake=True)

# Render
bpy.ops.render.render(animation=True)