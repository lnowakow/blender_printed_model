import bpy
import math
import random
from mathutils import Matrix, Vector

gcode_file_path = "/home/cstar/workspace/blender_spag_generation/gcodes/55.gcode"

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
    if not bpy.context.scene.my_tool.split_layers:
        bpy.context.scene.my_tool.split_layers = True
    bpy.ops.wm.gcode_import(filepath=filepath)


def transform_model(name, num_layers=100):
    #print_model holds all relevant data about Gcode
    print_model = bpy.context.scene.objects[name]

    # select Gcode object
    bpy.context.view_layer.objects.active = print_model
    bpy.context.active_object.select_set(state=True)

    # change origin of gcode to center of print_model
    shift_origin(print_model)
    
    # Scale the model down to real size
    print_model.scale *= 0.01
    print_model.location = [0,0,0]
    
    bpy.ops.object.modifier_add(type='BULID')
    print_model.modifiers['BUILD'].length = num_layers
    


def save_render2(num_rotation_steps=2, h_range=[30, 80], bckg_transparent=True):
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

def delete_layer_0():
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    # select layer 0
    bpy.data.objects['0'].select_set(state=True)
    bpy.ops.object.delete()
    
def merge_layers():
    for obj in bpy.data.collections['Layers'].all_objects:
        # select layer object
        bpy.context.view_layer.objects.active = obj
        bpy.context.active_object.select_set(state=True)
        # Convert to CURVE
        bpy.ops.object.convert(target='CURVE')
        # Make tool path populated with "filament"
        obj.data.bevel_depth = 0.4
    bpy.context.view_layer.objects.active = bpy.data.objects['1']
    bpy.context.active_object.select_set(state=True)
    bpy.ops.object.join()
    bpy.data.objects['1'].name = 'print_model'

if __name__ == "__main__":
    
    # Fresh slate
    bpy.ops.object.select_all(action='DESELECT')
    
    for obj in list(bpy.context.scene.objects):
        obj.select_set(True)
        bpy.ops.object.delete()
    
    # Add Camera to scene
    camera_data = bpy.data.cameras.new(name='Camera')
    camera_object = bpy.data.objects.new('Camera', camera_data)
    bpy.context.scene.collection.objects.link(camera_object)
    camera_object.location = [2,2,2]
      
    import_gcode(gcode_file_path)
    delete_layer_0()
    num_layers = len(bpy.data.collections['Layers'].all_objects)
    merge_layers()
    #transform_model('print_model')
    
    
    
   # save_render2(h_range=[5,60])
    