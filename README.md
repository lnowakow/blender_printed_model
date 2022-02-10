# blender_printed_model

This repository automatically renders gcode into photorealistic 3d-printed models with randomised lighting conditions and views.

## .env file

In your project directory, define a .env file with the following key:value pairs.

```console
PROJECT_PATH="/home/lukasz/workspace/blender_printed_model"
GCODE_DIR="/home/lukasz/workspace/blender_spag_generation/gcodes/"
OUT_PATH="/home/lukasz/workspace/blender_printed_model/pictures/"
```
Where:
**PROJECT_PATH** is the path to this repository.
**GCODE_DIR** is the path to where your gcode files are stored.
**OUT_PATH** is the path to where you'd like to save the rendered images.

## No Module Errors

To add **dotenv** module to Blender, use the following steps:
<span style="color:red"> **WARNING:** Make sure when you do pip install you use same python version as blender is using!</span>

In my case, Blender is using python3.9:

Step 1: python3.9 -m pip install python-dotenv
Step 2:
```console
lukasz@lukasz:~$ python3.9
>>> import dotenv
>>> dotenv.__file__
/home/lukasz/.local/lib/python3.9/site-packages/dotenv/__init__.py
```
Step 3:
```console
lukasz@lukasz:~$ sudo cp -r ~/.local/lib/python3.9/site-packages/dotenv /PATH-TO-BLENDER/3.0/python/lib/python3.9/site-packages/
```

The **dotenv** module should now be available for your blender scripts to use
