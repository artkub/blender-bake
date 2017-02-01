import bpy
import os
import sys

def uv_project(obj):
    obj.select = True
    bpy.context.scene.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')

    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent()

    # This creates a UV map called "UVMap"
    bpy.ops.uv.smart_project()

    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.pack_islands()

def bake_image(obj, output_dir):
    name = obj.name

    bpy.ops.image.new(name=name)

    image = bpy.data.images[name]
    image.file_format = 'JPEG'
    image.filepath = os.path.join(output_dir, name + '.jpeg')

    bpy.ops.object.mode_set(mode='OBJECT')

    for data in obj.data.uv_textures['UVMap'].data:
        data.image = image

    print('baking')
    bpy.ops.object.bake_image()

    print('saving image')
    image.save()
    return image

def prepare_export(obj, image):
    name = obj.name
    obj.data.materials.clear()

    mat = bpy.data.materials.new(name)
    texture_slot = mat.texture_slots.add()
    tex = bpy.data.textures.new(name, 'IMAGE')
    tex.image = image
    texture_slot.texture = tex

    obj.data.materials.append(mat)

def bake_and_export(name, output_dir):
    output_dir = os.path.join(output_dir, 'output', name)
    os.makedirs(output_dir)
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            bpy.ops.object.select_all(action='DESELECT')
            uv_project(obj)
            image = bake_image(obj, output_dir)
            prepare_export(obj, image)

    bpy.ops.export_scene.obj(
        filepath=os.path.join(output_dir, name + '.obj'),
        use_triangles=True, use_normals=False)

def import_bake_and_export(filepath):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    lamp = bpy.data.lamps.new(name='Lamp', type='HEMI')
    lamp_object = bpy.data.objects.new(name='Lamp', object_data=lamp)
    # lamp_object.rotation_euler.x = lamp_object.rotation_euler.z = 3.14 / 2
    bpy.context.scene.objects.link(lamp_object)

    bpy.ops.import_scene.obj(filepath=filepath)

    filename = os.path.basename(filepath)
    bake_and_export(os.path.splitext(filename)[0], os.getcwd())

def swap_skin(skin):
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            prepare_export(obj, bpy.data.images[skin])
            for data in obj.data.uv_textures['UVMap'].data:
                data.image = bpy.data.images[skin]

# exec(open(r'C:\Users\brianpeiris\Code\BakingService\bake_lib.py').read())
