import bpy
from bpy.props import StringProperty, BoolProperty
import os
import re
import time
from ... utils import MACHIN3 as m3



class New(bpy.types.Operator):
    bl_idname = "machin3.new"
    bl_label = "Current file is unsaved. Start a new file anyway?"
    bl_options = {'REGISTER'}


    def execute(self, context):
        bpy.ops.wm.read_homefile(app_template="")

        return {'FINISHED'}

    def invoke(self, context, event):
        if bpy.data.is_dirty:
            return context.window_manager.invoke_confirm(self, event)
        else:
            bpy.ops.wm.read_homefile(app_template="")
            return {'FINISHED'}


# TODO: file size output

class Save(bpy.types.Operator):
    bl_idname = "machin3.save"
    bl_label = "Save"
    bl_description = "Save"
    bl_options = {'REGISTER'}

    def execute(self, context):
        currentblend = bpy.data.filepath

        if currentblend:
            bpy.ops.wm.save_mainfile()

            t = time.time()
            localt = time.strftime('%H:%M:%S', time.localtime(t))

            print("%s | Saved blend: %s" % (localt, currentblend))
        else:
            bpy.ops.wm.save_mainfile('INVOKE_DEFAULT')

        return {'FINISHED'}


class SaveIncremental(bpy.types.Operator):
    bl_idname = "machin3.save_incremental"
    bl_label = "Incremental Save"
    bl_description = "Incremental Save"
    bl_options = {'REGISTER'}


    def execute(self, context):
        currentblend = bpy.data.filepath

        if currentblend:
            incrblend = self.get_incremented_path(currentblend)

            if os.path.exists(incrblend):
                self.report({'ERROR'}, "File '%s' exists already!\nBlend has NOT been saved incrementally!" % (incrblend))
            else:
                bpy.ops.wm.save_as_mainfile(filepath=incrblend)
                print("Saved blend incrementally:", incrblend)
        else:
            bpy.ops.wm.save_mainfile('INVOKE_DEFAULT')

        return {'FINISHED'}


    def get_incremented_path(self, currentblend):
        path = os.path.dirname(currentblend)
        filename = os.path.basename(currentblend)

        filenameRegex = re.compile(r"(.+)\.blend\d*$")

        mo = filenameRegex.match(filename)

        if mo:
            name = mo.group(1)
            numberendRegex = re.compile(r"(.*?)(\d+)$")

            mo = numberendRegex.match(name)

            if mo:
                basename = mo.group(1)
                numberstr = mo.group(2)
            else:
                basename = name + "_"
                numberstr = "000"

            number = int(numberstr)

            incr = number + 1
            incrstr = str(incr).zfill(len(numberstr))
            incrname = basename + incrstr + ".blend"

            return os.path.join(path, incrname)


class LoadMostRecent(bpy.types.Operator):
    bl_idname = "machin3.load_most_recent"
    bl_label = "Load Most Recent"
    bl_options = {"REGISTER"}

    def execute(self, context):
        recent_path = bpy.utils.user_resource('CONFIG', "recent-files.txt")

        try:
            with open(recent_path) as file:
                recent_files = file.read().splitlines()
        except (IOError, OSError, FileNotFoundError):
            recent_files = []

        if recent_files:
            most_recent = recent_files[0]

            # load_ui ensures the the viewport location/angle is loaded as well
            bpy.ops.wm.open_mainfile(filepath=most_recent, load_ui=True)

        return {'FINISHED'}


class AppendWorld(bpy.types.Operator):
    bl_idname = "machin3.append_world"
    bl_label = "Append World"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return m3.M3_prefs().appendworldpath and m3.M3_prefs().appendworldname

    def draw(self, context):
        layout = self.layout

        column = layout.column()

    def execute(self, context):
        path = m3.M3_prefs().appendworldpath
        name = m3.M3_prefs().appendworldname

        fullpath = "%s/%s" % (path, "World")

        bpy.ops.wm.append(directory=fullpath, filename=name, autoselect=False)

        world = bpy.data.worlds.get(name)

        if world:
            bpy.context.scene.world = world
        else:
            self.report({'ERROR'}, "World '%s' could not be appended.\nMake sure a world of that name exists in the world source file." % (name))

        return {'FINISHED'}


class AppendMaterial(bpy.types.Operator):
    bl_idname = "machin3.append_material"
    bl_label = "Append Material"
    bl_options = {'REGISTER', 'UNDO'}

    name: StringProperty(name="Append Name")

    applymaterial: BoolProperty(name="Apply Material to Selection", default=True)


    @classmethod
    def poll(cls, context):
        return m3.M3_prefs().appendmatspath

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, "applymaterial")

    def execute(self, context):
        path = m3.M3_prefs().appendmatspath
        name = self.name

        fullpath = "%s/%s" % (path, "Material")


        if name == "ALL":
            all_names = [mat.name for mat in m3.M3_prefs().appendmats]

            for name in all_names:
                n = name.replace("-", "")
                bpy.ops.wm.append(directory=fullpath, filename=n)
        else:
            bpy.ops.wm.append(directory=fullpath, filename=name, autoselect=False)

            mat = bpy.data.materials.get(name)

            if mat:
                if self.applymaterial:
                    for obj in context.selected_objects:
                        if not obj.material_slots:
                            obj.data.materials.append(mat)

                        obj.material_slots[0].material = mat
            else:
                self.report({'ERROR'}, "Material '%s' could not be appended.\nMake sure a material of that name exists in the material source file." % (name))

        return {'FINISHED'}


class LoadWorldSource(bpy.types.Operator):
    bl_idname = "machin3.load_world_source"
    bl_label = "Load World Source"
    bl_description = "Load World Source File"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return m3.M3_prefs().appendworldpath


    def execute(self, context):
        appendworldpath = m3.M3_prefs().appendworldpath

        if os.path.exists(appendworldpath):
            bpy.ops.wm.open_mainfile(filepath=appendworldpath, load_ui=True)

        return {'FINISHED'}


class LoadMaterialsSource(bpy.types.Operator):
    bl_idname = "machin3.load_materials_source"
    bl_label = "Load Materials Source"
    bl_description = "Load Materials Source File"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return m3.M3_prefs().appendmatspath

    def execute(self, context):
        appendmatspath = m3.M3_prefs().appendmatspath

        if os.path.exists(appendmatspath):
            bpy.ops.wm.open_mainfile(filepath=appendmatspath, load_ui=True)

        return {'FINISHED'}


class LoadPrevious(bpy.types.Operator):
    bl_idname = "machin3.load_previous"
    bl_label = "Load Previous"
    bl_description = "Load Previous Blend File in Current Folder"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return bpy.data.filepath

    def execute(self, context):
        filepath = bpy.data.filepath


        # """

        if filepath:
            currentpath = os.path.dirname(filepath)
            currentblend = os.path.basename(filepath)

            blendfiles = [f for f in sorted(os.listdir(currentpath)) if f.endswith(".blend")]

            index = blendfiles.index(currentblend)

            previousidx = index - 1

            if previousidx >= 0:
                previousblend = blendfiles[previousidx]


                loadpath = os.path.join(currentpath, previousblend)

                # add the path to the recent files list, for some reason it's not done automatically
                try:
                    recent_path = bpy.utils.user_resource('CONFIG', "recent-files.txt")
                    with open(recent_path, "r+") as f:
                        content = f.read()
                        f.seek(0, 0)
                        f.write(loadpath.rstrip('\r\n') + '\n' + content)

                except (IOError, OSError, FileNotFoundError):
                    pass

                print("Loading blend file %d/%d: %s" % (previousidx + 1, len(blendfiles), previousblend))
                bpy.ops.wm.open_mainfile(filepath=loadpath, load_ui=True)
            else:
                self.report({'ERROR'}, "You've reached the first file in the current foler: %s." % (currentpath))



        return {'FINISHED'}


class LoadNext(bpy.types.Operator):
    bl_idname = "machin3.load_next"
    bl_label = "Load Next"
    bl_description = "Load Next Blend File in Current Folder"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return bpy.data.filepath

    def execute(self, context):
        filepath = bpy.data.filepath

        if filepath:
            currentpath = os.path.dirname(filepath)
            currentblend = os.path.basename(filepath)

            blendfiles = [f for f in sorted(os.listdir(currentpath)) if f.endswith(".blend")]

            index = blendfiles.index(currentblend)

            nextidx = index + 1

            if nextidx < len(blendfiles):
                nextblend = blendfiles[nextidx]

                loadpath = os.path.join(currentpath, nextblend)

                # add the path to the recent files list, for some reason it's not done automatically
                try:
                    recent_path = bpy.utils.user_resource('CONFIG', "recent-files.txt")
                    with open(recent_path, "r+") as f:
                        content = f.read()
                        f.seek(0, 0)
                        f.write(loadpath.rstrip('\r\n') + '\n' + content)

                except (IOError, OSError, FileNotFoundError):
                    pass

                print("Loading blend file %d/%d: %s" % (nextidx + 1, len(blendfiles), nextblend))
                bpy.ops.wm.open_mainfile(filepath=loadpath, load_ui=True)
            else:
                self.report({'ERROR'}, "You've reached the last file in the current foler: %s." % (currentpath))

        return {'FINISHED'}
