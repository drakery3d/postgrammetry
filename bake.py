import bpy


class BatchBake(bpy.types.Operator):
    bl_idname = 'bb.bake'
    bl_label = 'batch bake'
    bl_options = {'UNDO'}

    context = None
    bake_material = None
    bake_image = None

    def execute(self, context):
        self.context = context

        self.prepare_bake()
        self.check_setup()
        self.bake_maps()
        self.clean_up()

        return {'FINISHED'}

    def prepare_bake(self):
        bpy.data.scenes[bpy.context.scene.name].render.engine = "CYCLES"

        self.bake_material = bpy.data.materials.new(
            name=self.context.scene.lowpoly_bake_obj + '_bake')

        if bpy.context.active_object.data.materials:
            bpy.data.objects[
                self.context.scene.
                lowpoly_bake_obj].data.materials[0] = self.bake_material
        else:
            bpy.data.objects[
                self.context.scene.lowpoly_bake_obj].data.materials.append(
                    self.bake_material)

        self.bake_material.use_nodes = True
        nodes = self.bake_material.node_tree.nodes
        bake_node = nodes.new('ShaderNodeTexImage')
        bake_node.select = True

        self.bake_image = bpy.data.images.new(
            self.context.scene.lowpoly_bake_obj + '_bake',
            width=1024,
            height=1024)
        bake_node.image = self.bake_image

        # TODO make visible in viewport and for rendering

        bpy.data.objects[self.context.scene.highpoly_bake_obj].select_set(True)
        bpy.data.objects[self.context.scene.lowpoly_bake_obj].select_set(True)

    def check_setup(self):
        print('check if everythin is alright')

    def bake_maps(self):
        if (self.context.scene.bake_diffuse):
            self.bake_diffuse()
        if (self.context.scene.bake_normal):
            self.bake_normal()
        if (self.context.scene.bake_ao):
            self.bake_ao()

    def clean_up(self):
        print('clean up the mess!')

    # TODO dry!
    def bake_diffuse(self):
        bpy.context.scene.cycles.samples = 1
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True
        bpy.ops.object.bake(type='DIFFUSE',
                            use_clear=True,
                            use_selected_to_active=True)

        self.bake_image.filepath_raw = self.context.scene.bake_out_path + self.context.scene.lowpoly_bake_obj + '_diffuse.jpg'
        self.bake_image.file_format = 'JPEG'
        self.bake_image.save()

    def bake_normal(self):
        bpy.context.scene.cycles.samples = 1
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True
        bpy.ops.object.bake(type='NORMAL',
                            use_clear=True,
                            use_selected_to_active=True)

        self.bake_image.filepath_raw = self.context.scene.bake_out_path + self.context.scene.lowpoly_bake_obj + '_normal.jpg'
        self.bake_image.file_format = 'JPEG'
        self.bake_image.save()

    def bake_ao(self):
        bpy.context.scene.cycles.samples = 32
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True
        bpy.ops.object.bake(type='AO',
                            use_clear=True,
                            use_selected_to_active=True)

        self.bake_image.filepath_raw = self.context.scene.bake_out_path + self.context.scene.lowpoly_bake_obj + '_ao.jpg'
        self.bake_image.file_format = 'JPEG'
        self.bake_image.save()