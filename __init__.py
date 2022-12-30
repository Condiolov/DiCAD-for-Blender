from math import radians
import bmesh
from mathutils import Matrix, Vector
import bpy, os, importlib
import webbrowser

from . import uvScale, alingFace
importlib.reload(uvScale)
importlib.reload(alingFace)



from . uvScale import *
from . alingFace import *


bl_info = {
        "name": "DiCAD 1.0",
        "description": "Configura o blender para desenhos CAD",
        "author": "Thiago Condé",
        "version": (1, 0, 0),
        "blender": (3, 4, 1),
        "location": "View3D",
        "warning": "Caso encontre algum erro reporte!!",
        "doc_url": "https://github.com/Condiolov/DiCAD",
        "tracker_url": "https://github.com/Condiolov/DiCAD/issues",
        "support": "TESTING",
        "category": "Generic"}

escala=0.1

# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
class DiCAD_TOOLS(bpy.types.Operator):
    global escala
    bl_idname = "dicad.menu"
    bl_label = "Clique para configurar"
    bl_options = {'REGISTER'}

    action : bpy.props.EnumProperty(items=[
        ("configurar", "configurar", "Configurando camera, pagina"),
        ("convert", "convert", "Configurando camera, pagina"),
        ("girarA", "girarA", "Rotacionar a direita"),
        ("girarB", "girarB", "Rotacionar a esquerda"),
        ("espelhar", "espelhar", "Espelhar em X"),
        ("subir", "subir", "Subir camada"),
        ("descer", "descer", "Descer camada"),
        ("linhas", "linhas", "Configurando camera, pagina"),
        ("top", "top", "Configurando camera, pagina"),
        ("n_cam_v", "n_cam_v", "Nova Camera"),
        ("n_cam_h", "n_cam_h", "Nova Camera"),
        ("new1", "new1", "Nova Pagina A4 Horizontal"),
        ("new2", "new2", "Nova Pagina A4 Vertical"),
        ("render", "render", "Gerar imagem"),
        ("donate", "donate", "Faça uma Doaçao"),
        ])


    def invoke(self, context, event=None):

        if self.action == "convert":
            self.gerar_linhas()

        if self.action == "top":
            DiCAD_TOP.execute(self, context)

        if self.action == "linhas":
            bpy.context.space_data.overlay.show_wireframes = not bpy.context.space_data.overlay.show_wireframes

        if self.action == "configurar":
            self.config_ferramentas(context)
            self.pagina_A4(context, 1)
            bpy.context.space_data.overlay.show_wireframes = True
            self.report({'INFO'}, "Configuração ok!!")

        elif self.action == "new1":
            self.pagina_A4(context, 1)

        elif self.action == "donate":
            webbrowser.open('https://condtec.com.br/doe/1519/')

        elif self.action == "espelhar":
            bpy.ops.transform.mirror(orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False))

        elif self.action == "subir":
            bpy.ops.transform.translate(value=(0, 0, 0.5))

        elif self.action == "descer":
            bpy.ops.transform.translate(value=(0, 0, -0.5))

        elif self.action == "girarA":
            bpy.ops.transform.rotate(value=radians(-90), orient_axis='Z', orient_type='VIEW')
        elif self.action == "girarB":
            bpy.ops.transform.rotate(value=radians(90), orient_axis='Z', orient_type='VIEW')
            #self.calisma_alanini_sifirla(context)
            #self.report({'INFO'}, "Nova Pagina criada")
        elif self.action == "new2":
            self.pagina_A4(context, 2)
            #self.calisma_alanini_sifirla(context)
            #self.report({'INFO'}, "Nova Pagina criada")
        elif self.action == "render":
            self.gera_imagem(context)

        return {"FINISHED"}
####-----------------------------------------------------------------------------------------
    def gerar_linhas(self):
        #Criando a coleção
        nome_original = bpy.context.selected_objects[0].name
        if (bpy.data.collections.find("Imprimir")<0): #bpy.data.collections['Rascunho']
            new_collection = bpy.data.collections.new('Imprimir')
            bpy.context.scene.collection.children.link(new_collection)
        collections = bpy.context.view_layer.layer_collection.children
        for collection in collections:
            if collection.name == "Imprimir":
                bpy.context.view_layer.active_layer_collection = collection

        bpy.ops.object.convert(target='GPENCIL', keep_original=True, merge_customdata=True, angle=0, thickness=5, seams=False, faces=False, offset=0.01)
        bpy.context.selected_objects[0].name='line_'+ nome_original

####-----------------------------------------------------------------------------------------
    def mostrar_linhas(self,active="not"):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        if active == "not":
                            space.overlay.show_wireframes= not space.overlay.show_wireframes
                        else:
                            space.overlay.show_wireframes= True
                        break

####-----------------------------------------------------------------------------------------
    def gera_imagem(self, context):
        # Verifico se a pagina esta na vertical ou na horizontal
        posicao="horizontal"
        camera=""

        try:
            if bpy.context.selected_objects[0].dimensions.x > bpy.context.selected_objects[0].dimensions.y:
                posicao = "vertical"
        except:
            self.report({'ERROR'}, "Selecione uma pagina ou objeto para impressão!!")
            return {'CANCELLED'}

        # Verifico se a camera existe se nao a crio
        for o in bpy.context.scene.objects:
            if o.name == "Camera_A4":
                camera=o

        if camera == "":
            camera = bpy.data.cameras.new(name='Camera_A4')
            camera_object = bpy.data.objects.new('Camera_A4', camera)
            bpy.data.collections['Rascunho'].objects.link(camera_object)
            bpy.data.cameras[camera.name].type="ORTHO"
            bpy.data.cameras[camera.name].ortho_scale = escala*296.9999694824219

        # Verifico se a pagina esta na vertical ou na horizontal
        if posicao == "horizontal":

            bpy.data.objects[camera.name].location[0]=escala*105
            bpy.data.objects[camera.name].location[1]=escala*148.5
            bpy.data.objects[camera.name].location[2]=escala*500.0

            bpy.data.scenes['Scene'].camera = bpy.data.objects[camera.name]
            bpy.context.scene.render.resolution_y=3508
            bpy.context.scene.render.resolution_x=2480
        else:
            bpy.data.objects[camera.name].location=Vector((escala*148.5, escala*105.0, 1.0))
            bpy.context.scene.render.resolution_x=3508
            bpy.context.scene.render.resolution_y=2480

            # focando na pagina A4
        bpy.ops.view3d.view_selected(use_all_regions=False)
        bpy.ops.view3d.camera_to_view()
        #render
        bpy.ops.render.render('INVOKE_DEFAULT', animation=False, write_still=True)

        #habilitando apenas a coleção imprimir para render
        coll = bpy.data.collections
        for c in coll:
            if c.name == "Imprimir":
                c.hide_render=False
            else:
                c.hide_render=True
        #bpy.ops.view3d.view_selected(use_all_regions=False)

####-----------------------------------------------------------------------------------------
    def config_ferramentas(self, context):

        if (bpy.data.objects.find('Cube') == 1) :
            bpy.data.objects.remove(bpy.data.objects['Cube'])
        if (bpy.data.objects.find('Camera')>=0) :
            bpy.data.objects.remove(bpy.data.objects['Camera'])
        if (bpy.ops.object.select_by_type(type='LIGHT')):
            bpy.ops.object.delete(use_global=False)

        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=False)

        bpy.context.scene.unit_settings.length_unit = 'CENTIMETERS'
        bpy.context.scene.unit_settings.scale_length = 0.01
        bpy.context.scene.tool_settings.use_snap_translate = True
        bpy.context.scene.tool_settings.use_snap_rotate = True
        bpy.context.scene.tool_settings.use_snap_scale = True

        bpy.context.space_data.overlay.grid_scale = 0.01
        bpy.context.space_data.clip_end = 10000

        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.view3d.view_axis(type="TOP")

        # Habilitando Snap
        bpy.data.scenes['Scene'].tool_settings.use_snap=True
        bpy.data.scenes['Scene'].tool_settings.snap_elements ={'EDGE_PERPENDICULAR', 'VERTEX', 'EDGE_MIDPOINT'}
        bpy.data.scenes['Scene'].tool_settings.snap_target='ACTIVE'

        # Habilitando o WORKBENCH
        bpy.data.scenes['Scene'].render.engine = 'BLENDER_WORKBENCH'
        bpy.data.scenes['Scene'].display.shading.light = 'FLAT'
        bpy.data.scenes['Scene'].display_settings.display_device = 'None'
        bpy.data.worlds['World'].color = (1.0, 1.0, 1.0)

        # Fundo e Material Branco
        bpy.data.materials.new(name="Branco") #set new material to variable
        bpy.data.materials['Branco'].diffuse_color=(1.0, 1.0, 1.0, 1.0)
        #bpy.data.objects['A4_retrato'].active_material = bpy.data.materials['Material']

        #Criando a coleção
        if (bpy.data.collections.find("Rascunho")<0): #bpy.data.collections['Rascunho']
            new_collection = bpy.data.collections.new('Rascunho')
            bpy.context.scene.collection.children.link(new_collection)
        collections = bpy.context.view_layer.layer_collection.children

        for collection in collections:
            if collection.name == "Rascunho":
                bpy.context.view_layer.active_layer_collection = collection

####-----------------------------------------------------------------------------------------
    def pagina_A4(self, context,x=0):

        if x == 2:
            verts = [( 0,  0,  -1),( 0 , escala*210.0,  -1),( escala*297.0, escala*210.0,  -1),( escala*297.0,  0,  -1)]
            faces = [[0, 1, 2, 3]]
            bpy.ops.object.select_all(action='DESELECT')
            self.add_mesh("A4_horizontal", verts, faces)
            bpy.ops.view3d.view_selected(use_all_regions=False)
        else:
            verts = [( 0,  0, -1),( 0 , escala*297.0,  -1),( escala*210.0, escala*297.0,  -1),( escala*210.0,  0,  -1)]
            faces = [[0, 1, 2, 3]]
            bpy.ops.object.select_all(action='DESELECT')
            self.add_mesh('A4_vertical', verts, faces)

            bpy.ops.view3d.view_selected(use_all_regions=False)

####-----------------------------------------------------------------------------------------
#Função de adicionar a folha
    def add_mesh(self,name, verts, faces, edges=None):
        if edges is None:
            edges = []
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(mesh.name, mesh)


        for collection in bpy.context.view_layer.layer_collection.children:
            if collection.name == "Rascunho":
                bpy.context.view_layer.active_layer_collection = collection

        bpy.context.collection.objects.link(obj)
        #bpy.data.collections[col_name].objects.link(obj)

        bpy.context.view_layer.objects.active = obj
        obj.select_set(1)
        mesh.from_pydata(verts, edges, faces)

        obj =  bpy.data.materials.get("Branco")
        if obj is not None:
            bpy.context.active_object.data.materials.append(bpy.data.materials['Branco'])

        mesh.update()

# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
class DiCAD_MENU(bpy.types.Panel):

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "DiCAD"
    bl_label = "DiCAD 1.0"
    bl_idname = "DiCAD_MENU"
    status:  bpy.props.BoolProperty(
            name="enable", default=True)
    smoothValue: bpy.props.FloatProperty(
            name="smooth", default=30, min=0.0, max=180, soft_min=0.0,
            soft_max=180, step=1
            )

####-----------------------------------------------------------------------------------------
    def draw(self, context):

        layout = self.layout
        scn = context.scene

        layout.label(text="Configurar:")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("dicad.menu", text="Configurar Blender", icon="SETTINGS").action = "configurar"

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("dicad.menu", text="A4 vertical", icon="FILE").action = "new1"
        row.operator("dicad.menu", text="A4 horizontal", icon="WORKSPACE").action = "new2"

        layout.label(text="Options:")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("dicad.menu", text="Mostrar Linhas", icon="MOD_WIREFRAME").action = "linhas"
        row.operator("dicad.menu", text="Visão TOP", icon="NODE_CORNER").action = "top"
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("dicad.menu", text="Rotacionar direita", icon="LOOP_BACK").action = "girarA"
        row.operator("dicad.menu", text="Rotacionar esquerda", icon="LOOP_FORWARDS").action = "girarB"
        row.operator("dicad.menu", text="Espelhar", icon="MOD_MIRROR").action = "espelhar"
        row.operator("dicad.menu", text="Subir", icon="SORT_DESC").action = "subir"
        row.operator("dicad.menu", text="Descer", icon="SORT_ASC").action = "descer"

        layout.label(text="Gerar Linhas:")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("dicad.menu", text="Gerar Linhas", icon="MOD_SOLIDIFY").action = "convert"

        layout.label(text="GERAR Imagem:")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("dicad.menu", text="GERAR IMAGEM", icon="MOD_MESHDEFORM").action = "render"
        row.operator("dicad.menu", text="", icon="FUND").action = "donate"


# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
class DiCAD_TOP(bpy.types.Operator):
    bl_idname = "dicad.top"
    bl_label = "Top View"

    def execute(self, context):
        bpy.ops.view3d.view_axis(type="TOP")
        if (not bpy.context.selected_objects):
            bpy.ops.object.select_all(action='SELECT')

        bpy.ops.view3d.view_selected(use_all_regions=False)
        bpy.ops.object.select_all(action='DESELECT')
        return {"FINISHED"}

# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
classes = [
        DiCAD_TOP,
        DiCAD_MENU,
        DiCAD_TOOLS,
        DiCAD_origami,
        DiCAD_aling,
        ]

# functions = [menu_func]
addon_keymaps = []
# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
def register():
    for i in classes:
        bpy.utils.register_class(i)

    # for fn in functions:
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(menu_func)
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_orygami)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("dicad.top", type='NUMPAD_7', value='PRESS')
        #bpy.data.window_managers["WinMan"].(null) = 'NUMPAD_7'

        addon_keymaps.append((km, kmi))
# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
    # for fn in functions:
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(menu_func)
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_orygami)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    #del bpy.types.Object.ncnc_objayar

if __name__ == "__main__":
    register()
