#
# Copyright 2011-2013 Blender Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# <pep8 compliant>

bl_info = {
    "name": "Cycles Render Engine",
    "author": "",
    "blender": (2, 76, 0),
    "location": "Info header, render engine menu",
    "description": "Cycles Render Engine integration",
    "warning": "",
    "wiki_url": "https://www.blender.org/manual/render/cycles/index.html",
    "tracker_url": "",
    "support": 'OFFICIAL',
    "category": "Render"}

import bpy

from . import (
        engine,
        version_update,
        )


class CyclesRender(bpy.types.RenderEngine):
    bl_idname = 'CYCLES'
    bl_label = "Cycles Render"
    bl_use_shading_nodes = True
    bl_use_preview = True
    bl_use_exclude_layers = True
    bl_use_save_buffers = True

    def __init__(self):
        self.session = None

    def __del__(self):
        engine.free(self)

    # final render
    def update(self, data, scene):
        if not self.session:
            if self.is_preview:
                cscene = bpy.context.scene.cycles
                use_osl = cscene.shading_system and cscene.device == 'CPU'

                engine.create(self, data, scene,
                              None, None, None, use_osl)
            else:
                engine.create(self, data, scene)
        else:
            engine.reset(self, data, scene)

    def render(self, scene):
        engine.render(self)

    def bake(self, scene, obj, pass_type, pass_filter, object_id, pixel_array, num_pixels, depth, result):
        engine.bake(self, obj, pass_type, pass_filter, object_id, pixel_array, num_pixels, depth, result)

    # viewport render
    def view_update(self, context):
        if not self.session:
            engine.create(self, context.blend_data, context.scene,
                          context.region, context.space_data, context.region_data)
        engine.update(self, context.blend_data, context.scene)

    def view_draw(self, context):
        engine.draw(self, context.region, context.space_data, context.region_data)

    def update_script_node(self, node):
        if engine.with_osl():
            from . import osl
            osl.update_script_node(node, self.report)
        else:
            self.report({'ERROR'}, "OSL support disabled in this build.")


def engine_exit():
    engine.exit()


def register():
    from . import ui
    from . import properties
    from . import presets
    import atexit

    # Make sure we only registered the callback once.
    atexit.unregister(engine_exit)
    atexit.register(engine_exit)

    engine.init()

    properties.register()
    ui.register()
    presets.register()
    bpy.utils.register_module(__name__)

    bpy.app.handlers.version_update.append(version_update.do_versions)


def unregister():
    from . import ui
    from . import properties
    from . import presets
    import atexit

    bpy.app.handlers.version_update.remove(version_update.do_versions)

    ui.unregister()
    properties.unregister()
    presets.unregister()
    bpy.utils.unregister_module(__name__)
