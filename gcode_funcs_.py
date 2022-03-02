import sys
import os
from dotenv import load_dotenv
load_dotenv()
path = os.getenv('PROJECT_PATH')
if path not in sys.path:
    sys.path.append(path)
from imp import reload
import gcode_api_
reload(gcode_api_)

import bpy
import numpy as np
from glob import glob

class RandomPrint:
    def __init__(self, gcode_dir, out_path="", diffuse_color=[0,1],\
                    num_lights=[1,3], light_energy=[20,50], range_l=[1.0, 2.5],\
                    num_rotation_steps=2, save=False, h_range=[30,80], bckg_transparent=True):
        self.gcode_dir = gcode_dir
        self.diffuse_color = diffuse_color
        self.num_lights = num_lights
        self.light_energy = light_energy
        self.range_l = range_l
        self.num_rotation_steps = num_rotation_steps
        self.save = save
        self.h_range = h_range
        self.bckg_transparent = bckg_transparent
        
    def __call__(self, gcode_file, with_failure=False):
        
        num_lights = gcode_api_.rand_unif_range(self.num_lights, is_real=False)
        gcode_api_.add_lights(num_lights=num_lights, light_energy=self.light_energy, range_l=self.range_l)
    
        gcode_api_.import_gcode(gcode_file)
        gcode_api_.delete_layer_0()
        num_layers = len(bpy.data.collections['Layers'].all_objects)
        
        diffuse_color = gcode_api_.rand_populate_arr(self.diffuse_color, gcode_api_.rand_unif_range, 3)
        diffuse_color.append(1.0)
        failed_layers = 0
        names = ['print_model']
        
        if with_failure:
            min_failed = round(num_layers/6)
            max_failed = round(num_layers/2)
    
            failed_layers = gcode_api_.rand_unif_range([min_failed, max_failed], is_real=False)
            print(f"Number of layers that will fail: {failed_layers}")
            for i in range(failed_layers):
                gcode_api_.rand_vertex_move(bpy.data.objects[str(num_layers-i)])
                print("Done layer " + str(num_layers-i))
            gcode_api_.merge_layers(num_layers, failed_layers, with_failure=True)
            gcode_api_.edit_part_appearance('failed_model', diffuse_color=diffuse_color)  
            names.extend(['failed_model'])
        gcode_api_.merge_layers(num_layers, failed_layers, with_failure=False)
        gcode_api_.edit_part_appearance('print_model', diffuse_color=diffuse_color)
        gcode_api_.transform_model(names, num_layers)
        
        gcode_api_.save_render2(out_path, num_layers=num_layers, h_range=[5,60], bckg_transparent=True)
            

def get_filename(arr, i):
    return arr[i % len(arr)]
  
gcode_dir = os.getenv('GCODE_DIR')
out_path = os.getenv('OUT_PATH')


if __name__ == "__main__":
    print(gcode_dir)
    # Fresh slate
    bpy.ops.object.select_all(action='DESELECT')
    gcode_api_.delete_all_obj(['LIGHT', 'CURVE', 'CAMERA', 'MESH'])
    
    # Add Camera to scene
    camera_data = bpy.data.cameras.new(name='Camera')
    camera_object = bpy.data.objects.new('Camera', camera_data)
    bpy.context.scene.collection.objects.link(camera_object)
    camera_object.location = [1.5,1.5,1.5]
    
    print("-------------------------BLENDER GCODE PRINT MODEL GENERATOR-------------------------")
    print(sys.version)
    
    rand_print = RandomPrint(gcode_dir, out_path=out_path, diffuse_color=[0,1],\
                                num_lights=[1,3], light_energy=[20,50], range_l=[1.0,2.5],\
                                num_rotation_steps=2, save=False, h_range=[20,50], bckg_transparent=True)
    gcode_files = glob(os.path.join(gcode_dir, "*"))
    num_imgs_to_save = 10
    num_gcodes_used = 0
    for i in range(num_imgs_to_save):
        gcode_file = get_filename(gcode_files, num_gcodes_used)
        print("Processing: " + gcode_file)
        rand_print(gcode_file=gcode_file, with_failure=True)
        num_gcodes_used += 1
        gcode_api_.delete_all_obj(['LIGHT', 'CURVE'])
        camera_object.location = [1.5,1.5,1.5]
    


    

    