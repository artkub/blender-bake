import bpy
import os
import sys
from math import ceil, log, pow

def uv_project(obj):
    bpy.ops.mesh.uv_texture_add()
    uv_map_name = obj.data.uv_layers[-1].name

    bpy.ops.object.mode_set(mode='EDIT')

    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent()

    bpy.ops.uv.smart_project()

    bpy.ops.uv.select_all(action='SELECT')

    return uv_map_name

def determine_texture_size(obj):
    # approximate calculation using the cube root of the volume
    dim = obj.dimensions
    volume = dim[0] * dim[1] *  dim[2]
    res = pow(volume, 1.0/3.0) * 256.0
    npot = int(pow(2.0, ceil(log(res) / log(2.0))))
    return max(128, min(4096, npot))

def bake_image(obj, uv_map_name, output_dir, dry_run):
    name = obj.name
    size = determine_texture_size(obj)
    image = bpy.data.images.new(name=name, width=size, height=size)

    image.file_format = 'JPEG'
    image.filepath = os.path.join(output_dir, name + '.jpeg')

    bpy.ops.object.mode_set(mode='OBJECT')

    for data in obj.data.uv_textures[uv_map_name].data:
        data.image = image

    world = bpy.context.scene.world
    world.light_settings.use_ambient_occlusion = False
    world.light_settings.samples = 5

    print('baking')
    bpy.ops.object.bake_image()

    if not dry_run:
        print('saving image')
        image.save()
    return image

def replace_materials_with_baked_texture(obj, image):
    name = obj.name
    obj.data.materials.clear()

    mat = bpy.data.materials.new(name)
    texture_slot = mat.texture_slots.add()
    tex = bpy.data.textures.new(name, 'IMAGE')
    tex.image = image
    texture_slot.texture = tex

    obj.data.materials.append(mat)

def bake_and_export(name, output_dir, dry_run=False):
    output_dir = os.path.join(output_dir, 'output', name)
    if not dry_run:
        os.makedirs(output_dir)

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.context.scene.objects.active = obj
            uv_map_name = uv_project(obj)
            image = bake_image(obj, uv_map_name, output_dir, dry_run)
            replace_materials_with_baked_texture(obj, image)

    if not dry_run:
        print('exporting')
        bpy.ops.export_scene.obj(
            filepath=os.path.join(output_dir, name + '.obj'),
            use_triangles=True, use_normals=False)

def add_lamp(type):
    lamp = bpy.data.lamps.new(name='Lamp', type=type)
    lamp.energy = 0.5
    lamp_object = bpy.data.objects.new(name='Lamp', object_data=lamp)
    bpy.context.scene.objects.link(lamp_object)

def import_bake_and_export(filepath, dry_run=False):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    add_lamp('HEMI')
    add_lamp('POINT')

    bpy.ops.import_scene.obj(filepath=filepath)

    filename = os.path.basename(filepath)
    bake_and_export(os.path.splitext(filename)[0], os.getcwd(), dry_run)

# exec(open(r'C:\Users\brianpeiris\Code\BakingService\bake_lib.py').read())
# exec(open(r'C:\Users\AltspaceVR\Code\brian\blender-bake\bake_lib.py').read())
# exec(open(r'C:\Users\AltspaceVR\Code\brian\blender-bake\bake_lib.py').read()); import_bake_and_export(r'C:\Users\AltspaceVR\Code\phil\altspace\jeopardy2.obj', dry_run=True)
