import bpy
from glob import glob
import numpy as np
import os
import random
import math
from mathutils import Matrix, Vector

def shift_origin(obj):
    # select Gcode object
    bpy.context.view_layer.objects.active = obj
    bpy.context.active_object.select_set(state=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')


def import_gcode(filepath):
    if not bpy.context.scene.my_tool.subdivide:
        bpy.context.scene.my_tool.subdivide = True
    if not bpy.context.scene.my_tool.split_layers:
        bpy.context.scene.my_tool.split_layers = True
    bpy.ops.wm.gcode_import(filepath=filepath)


def transform_model(name, num_layers=100):
    # print_model holds all relevant data about Gcode
    print_model = bpy.context.scene.objects[name]

    # select Gcode object
    bpy.context.view_layer.objects.active = print_model
    bpy.context.active_object.select_set(state=True)

    # change origin of gcode to center of print_model
    shift_origin(print_model)

    # Scale the model down to real size
    print_model.scale *= 0.01
    print_model.location = [0, 0, 0]

    #bpy.ops.object.modifier_add(type='BUILD')
    #print_model.modifiers['Build'].frame_duration = num_layers


def save_render2(path_out, num_layers, num_rotation_steps=2, h_range=[30, 80], bckg_transparent=True):
    camera = bpy.data.objects['Camera']  # Make sure your first camera is named 'MainCamera'
    print(camera.type)
    # set radius vector in polar coords
    r = Vector((camera.location[0], camera.location[1], camera.location[2])).length
    # set target
    target = bpy.data.objects['print_model']
    t_loc_x = target.location.x
    t_loc_y = target.location.y
    bpy.context.view_layer.objects.active = target
    bpy.context.active_object.select_set(state=True)
    
    # Add a new track to constraint and set it to track your object
    bpy.context.view_layer.objects.active = camera
    track_to = bpy.context.object.constraints.new('TRACK_TO')
    track_to.target = target
    track_to.track_axis = 'TRACK_NEGATIVE_Z'
    track_to.up_axis = 'UP_Y'
    bpy.context.scene.camera = bpy.context.object

    files_num = len(glob(os.path.join(path_out, "*")))
    for step_num in range(files_num, files_num + num_rotation_steps):
        h = math.radians(random.uniform(h_range[0], h_range[1]))
        alpha = 2 * math.pi * random.random()
        x = r * math.cos(h) * math.cos(alpha)
        y = r * math.cos(h) * math.sin(alpha)
        z = r * math.sin(h)

        x += t_loc_x
        y += t_loc_y

        camera.location.x = x
        camera.location.y = y
        camera.location.z = z

        #bpy.context.scene.frame_set(random.randint(2, num_layers))
        #bpy.context.scene.frame_set(num_layers)
        
        file = os.path.join(path_out, str(step_num))
        if bckg_transparent:
            bpy.context.scene.render.film_transparent = True
        else:
            bpy.context.scene.render.film_transparent = False
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'
        # bpy.ops.view3d.camera_to_view_selected()
        bpy.context.scene.render.filepath = file
        bpy.context.scene.render.resolution_x = 5000  # 3840 #1920
        bpy.context.scene.render.resolution_y = 5000  # 3840 #1080
        bpy.ops.render.render(write_still=True)


def delete_layer_0():
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    # select layer 0
    bpy.data.objects['0'].select_set(state=True)
    bpy.ops.object.delete()


def merge_layers(num_layers, failed_layers=0, with_failure=False):
    for obj in bpy.data.collections['Layers'].all_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects['1']
    bpy.context.active_object.select_set(state=True)
    # Convert to CURVE
    bpy.ops.object.convert(target='CURVE')
    
    # Deselect failed layers
    for i in range(failed_layers):
        bpy.data.objects[str(num_layers-i)].select_set(False)
        print(f'failed layer {num_layers-i} deselected')
    
    # Make tool path populated with "filament"
    bpy.ops.object.join()
    print_model = bpy.data.objects['1']
    print_model.name = 'print_model'
    print_model.data.bevel_depth = 0.1
    print_model.data.extrude = 0.2
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.tilt(value=1.5707)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = bpy.data.objects[str(num_layers)]
    bpy.context.active_object.select_set(state=True)
    print_model.select_set(False)

    # Failed Layers
    for i in range(failed_layers):
        bpy.data.objects[str(num_layers-i)].select_set(True)
        print(f'selected failed layer {num_layers-i}')   

    
    bpy.ops.object.join()

    failed_model = bpy.data.objects[str(num_layers)]
    failed_model.name = 'failed_model'
    failed_model.data.bevel_depth = 0.1
    

def add_lights(num_lights, light_energy=[10, 50], range_l=[1.0, 2.5]):
    # Inserts lights
    # Set number of lights; set to 3 for debug, but line directly below can be removed
    bpy.ops.object.select_by_type(type='LIGHT')
    bpy.ops.object.delete()
    # Finds the amount of lights that are going to be used
    lights = random.randint(1, num_lights)
    # Makes new lights the randomized amount of time
    for num in range(0, num_lights):
        light_data = bpy.data.lights.new(name="light_" + str(num), type='POINT')
        light_data.energy = rand_unif_range(light_energy, is_real=False)
        light_object = bpy.data.objects.new(name="light_" + str(num), object_data=light_data)
        bpy.context.collection.objects.link(light_object)
        bpy.context.view_layer.objects.active = light_object
        light_object.location = (rand_in_range2(range_l), rand_in_range2(range_l), abs(rand_in_range2(range_l)))
        dg = bpy.context.evaluated_depsgraph_get()
        dg.update()


def rand_in_range2(range):
    sign = [-1, 1][random.randrange(2)]
    res = sign * random.uniform(range[0], range[1])
    return res


def delete_all_obj(types):
    for type in types:
        bpy.ops.object.select_by_type(type=type)
        bpy.ops.object.delete()


def edit_part_appearance(diffuse_color=[0.8, 0.2, 0.2, 1.0]):
    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    print = bpy.data.objects['print_model']
    print.data.resolution_u = 20
    print.data.render_resolution_u = 32

    bpy.context.view_layer.objects.active = print
    mat = bpy.data.materials.new('color')
    mat.diffuse_color = diffuse_color
    mat.specular_intensity = 1.0
    mat.roughness = 0.4
    print.data.materials.append(mat)


def rand_unif_range(range, is_real=True):
    if is_real:
        return random.uniform(range[0], range[1])
    else:
        return random.randint(range[0], range[1])


def rand_populate_arr(range_arr, func, size):
    res = [func(range_arr) for i in range(size)]
    return res

def rand_normal(scale=1):
    return np.random.normal(scale=scale)

def rand_vertex_move(obj):
    
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.context.active_object.select_set(state=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    mesh = obj.data
    mat_world = obj.matrix_world
    for i in range(len(mesh.vertices)):
        vert = mesh.vertices[i]
        vec = Vector((rand_normal(1), rand_normal(1), rand_normal(0.2)))
        mat_edit = mat_world.inverted() @ Matrix.Translation(vec) @ mat_world
        vert.co = mat_edit @ vert.co

        