import bpy
from bpy.props import StringProperty
from ... utils import MACHIN3 as m3


class SwitchWorkspace(bpy.types.Operator):
    bl_idname = "machin3.switch_workspace"
    bl_label = "Switch Workspace"
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty()

    def draw(self, context):
        layout = self.layout

        column = layout.column()


    def execute(self, context):
        bpy.context.window.workspace = bpy.data.workspaces[self.name]

        return {'FINISHED'}
