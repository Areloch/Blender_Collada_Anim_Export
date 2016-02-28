bl_info = {
    "name":         "Collada Animation Export",
    "author":       "Jeff Raab",
    "blender":      (2,7,5),
    "version":      (0,0,1),
    "location":     "File > Import-Export",
    "description":  "Export Collada animation",
    "category":     "Import-Export"
}

import bmesh
import os
import time
import bpy
import mathutils
import math
import random
import operator
import sys
from bpy.props import *
from struct import pack

from bpy_extras.io_utils import ExportHelper

from bpy.props import BoolProperty, IntProperty, EnumProperty

def menu_func(self, context):
    self.layout.operator(ExportColladaAnimation.bl_idname, text="Collada Animation Export(.dae)");

def register():
    bpy.utils.register_module(__name__);
    bpy.types.INFO_MT_file_export.append(menu_func);
    
def unregister():
    bpy.utils.unregister_module(__name__);
    bpy.types.INFO_MT_file_export.remove(menu_func);
    
bpy.types.Scene.Collada_Animation_option_filename_src = EnumProperty(
    name        = "Filename",
    description = "Sets the name for the files",
    items       = [ ('0', "From object",    "Name will be taken from object name"),
                    ('1', "From Blend",     "Name will be taken from .blend file name") ],
    default     = '0')
    
def get_dst_path():
    if bpy.context.scene.Collada_Animation_option_filename_src == '0':
        if bpy.context.active_object:
            path = os.path.split(bpy.data.filepath)[0] + "\\" + bpy.context.active_object.name# + ".dae"
        else:
            #path = os.path.split(bpy.data.filepath)[0] + "\\" + "Unknown";
            path = os.path.splitext(bpy.data.filepath)[0]# + ".dae"
    else:
        path = os.path.splitext(bpy.data.filepath)[0]# + ".dae"
    return path
    
def copyActionToTemp(targetActionName):
    tempAction = bpy.data.actions["Temp"]
    
    if tempAction is None:
        bpy.data.actions.new("Temp")
        tempAction = bpy.data.actions["Temp"]
        
    action = bpy.data.actions[targetActionName]
    
    tempAction.fcurves = action.fcurves
            
#def appendActionToTemp(targetActionName):
#    tempAction = bpy.data.actions["Temp"]
    
#    if(tempAction is null)
 #       bpy.data.actions.new("Temp")
 #       tempAction = bpy.data.actions["Temp"]
        
 #   action = bpy.data.actions[targetActionName]
    
#    for fcu in action.fcurves:
#        print(fcu.data_path + " channel " + str(fcu.array_index))
#        for keyframe in fcu.keyframe_points:
 #           print(keyframe.co) #coordinates x,y

    
class ExportColladaAnimation(bpy.types.Operator, ExportHelper):
    bl_idname       = "animation.dae";
    bl_label        = "Collada Animation Export";
    bl_options      = {'PRESET'};
    
    filename_ext    = ".dae";
    
    #Items are defined as value then presented text
    exportMethod = EnumProperty(name='Export Method',
            description='Export Method --> How the exported actions are saved out)',
            items=(('Current', 'Current Action Only', ''),
                   ('Separate', 'All Actions, Separate Files', ''),
                   ('Single', 'All Actions, One File', ''),
                   ),
            default='Current',
            )
    
    def execute(self, context):
        # prepare a scene
        scn = bpy.context.scene
        count = 0
        
        selectedAction = scn.object.animation_data.action;
        
        if exportMethod == 'Current':
            copyActionToTemp(scn.object.animation_data.action)

        scn.object.animation_data.action = bpy.data.actions["Temp"]
        
        # bake the animation's keyframes
        while count <= bpy.context.scene.frame_end:
            bpy.context.scene.frame_current = count
            
            bpy.ops.wm.redraw_timer(type='ANIM_STEP')
            
            # create keyframe
            bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_VisualLocRot')
            
            # force an update of the scene, and re-key for IK
            bpy.data.scenes[0].update()
            bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_VisualLocRot')
            
            count += 1
        
        print( "Saving out to path:" + get_dst_path() )
        
        # export selected
        bpy.ops.wm.collada_export(filepath=get_dst_path(), selected=True)
        
        # clear the temp action
        scn.object.animation_data.action.user_clear()
        
        scn.object.animation_data.action = selectedAction

        return {'FINISHED'}
        
if __name__ == "__main__":
    register()