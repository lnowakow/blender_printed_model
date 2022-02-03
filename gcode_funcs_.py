import bpy
import math
import random
from mathutils import Matrix, Vector

gcode_file_path = "/home/lukasz/workspace/blender_spag_generation/gcodes/55.gcode"

def shift_origin(obj):
    me = obj.data
    mw = obj.matrix_world
    origin = sum((v.co for v in me.vertices), Vector()) / len(me.vertices)
    
    T = Matrix.Translation(-origin)
    me.transform(T)
    mw.translation = mw @ origin

def import_gcode(filepath):
    if not bpy.context.scene.my_tool.subdivide:
        bpy.context.scene.my_tool.subdivide = True
    bpy.ops.wm.gcode_import(filepath=filepath)


def transform_model(name):
    #print_model holds all relevant data about Gcode
    print_model = bpy.context.scene.objects[name]

    # Scale the model down to real size
    print_model.scale *= 0.01

    # select Gcode object
    bpy.context.view_layer.objects.active = print_model
    bpy.context.active_object.select_set(state=True)
    
    # change origin of gcode to center of print_model
    shift_origin(print_model)

    # Convert to CURVE
    bpy.ops.object.convert(target='CURVE')
    # Make tool path populated with "filament"
    print_model.data.bevel_depth = 0.4


def save_render2(num_rotation_steps=2, h_range=[30, 80], bckg_transparent=True):
    camera = bpy.data.objects['Camera']  # Make sure your first camera is named 'MainCamera'
    print(camera.type)
    
    # set target
    target = bpy.data.objects['Gcode']
    t_loc_x = target.location.x
    t_loc_y = target.location.y
    bpy.context.view_layer.objects.active = target
    bpy.context.active_object.select_set(state=True)

    # set radius vector in polar coords
    r = Vector((camera.location[0], camera.location[1], camera.location[2])).length

    # Add a new track to constraint and set it to track your object
    bpy.context.view_layer.objects.active = camera
    track_to = bpy.context.object.constraints.new('TRACK_TO')
    track_to.target = target
    track_to.track_axis = 'TRACK_NEGATIVE_Z'
    track_to.up_axis = 'UP_Y'

    h = math.radians(random.uniform(h_range[0],h_range[1]))
    alpha = 2 * math.pi * random.random()
    x = r * math.cos(h) * math.cos(alpha)
    y = r * math.cos(h) * math.sin(alpha)
    z = r * math.sin(h)

    x += t_loc_x
    y += t_loc_y

    camera.location.x = x
    camera.location.y = y
    camera.location.z = z
    
    #camera.constraints.remove(track_to)


if __name__ == "__main__":
    import_gcode(gcode_file_path)
    transform_model('Gcode')
    #save_render2()
    