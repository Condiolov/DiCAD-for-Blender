import bpy
from mathutils import Matrix, Vector
import bmesh

#fonte:https://blender.stackexchange.com/questions/138989/align-object-a-to-object-b-to-their-respective-active-faces-with-python

# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
class DiCAD_aling(bpy.types.Operator):
    bl_idname = "dicad.aling"
    bl_label = "DiviCAD > Aling Faces"
    bl_option = {'REGISTER'}
    bl_description = "Selecione a face do objeto 1 e a face destino do outro objeto"

    def execute(self, context):
        try:
            context = bpy.context
            scene = context.scene

            A = context.object
            A.select_set(state=False)
            #bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            try:
                B = bpy.context.selected_objects[0]
            except:
                self.report({'ERROR'}, "Selecione a face do Objeto ou CTRL + Click em um objeto!!")
                return {'CANCELLED'}
            A.select_set(state=True)
            bpy.ops.view3d.snap_cursor_to_active()

            #obj = context.edit_object (!) equal to A
            src_mw = A.matrix_world.copy()
            src_bm = bmesh.from_edit_mesh(A.data)
            src_face = src_bm.select_history.active
            src_o = src_face.calc_center_median()
            src_normal = src_face.normal
            src_tan = src_face.calc_tangent_edge()

            # This is the target, we change the sign of normal to stick face to face
            dst_mw = B.matrix_world.copy()

            if B.mode != 'OBJECT':
                dst_bm = bmesh.from_edit_mesh(B.data)

            else:
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.editmode_toggle()

                B = bpy.context.object
                B.select_set(state=False)
                A = bpy.context.selected_objects[0]
                B.select_set(state=True)

                bpy.ops.view3d.snap_cursor_to_active()

                src_mw = A.matrix_world.copy()
                src_bm = bmesh.from_edit_mesh(A.data)
                src_face = src_bm.select_history.active
                src_o = src_face.calc_center_median()
                src_normal = src_face.normal
                src_tan = src_face.calc_tangent_edge()

                # This is the target, we change the sign of normal to stick face to face
                dst_mw = B.matrix_world.copy()
                dst_bm = bmesh.from_edit_mesh(B.data)

            dst_face = dst_bm.select_history.active
            dst_o = dst_face.calc_center_median()
            dst_normal = -(dst_face.normal)
            dst_tan = (dst_face.calc_tangent_edge())
           
            vec2 = src_normal @ src_mw.inverted()
            matrix_rotate = dst_normal.rotation_difference(vec2).to_matrix().to_4x4()

            vec1 = src_tan @ src_mw.inverted()
            dst_tan = dst_tan @ matrix_rotate.inverted()
            mat_tmp = dst_tan.rotation_difference(vec1).to_matrix().to_4x4()
            matrix_rotate = mat_tmp @ matrix_rotate
            matrix_translation = Matrix.Translation(src_mw @ src_o)

            # This line applied the matrix_translation and matrix_rotate
            B.matrix_world = matrix_translation @ matrix_rotate.to_4x4()

            # We need to recalculate these value since we change the matrix_world
            dst_mw = B.matrix_world.copy()
            dst_bm = bmesh.from_edit_mesh(B.data)
            dst_face = dst_bm.select_history.active
            dst_o = dst_face.calc_center_median()

            # The following is telling blender to find a translation from face center to origin,
            # And than apply it on world matrix 
            # Be Careful, the order of the matrix multiplication change the result,
            # We always put the transform matrix on "Left Hand Side" to perform the task
            dif_mat = Matrix.Translation(B.location - dst_mw @ dst_o)
            B.matrix_world = dif_mat @ B.matrix_world
            
           
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.ed.undo_push()
        except:
            bpy.ops.mesh.select_all(action='DESELECT')
            self.report({'ERROR'}, "Tente Novamente ou deixe no modo de Edição apenas os dois objetos a serem alinhados!!")
            return {'CANCELLED'}

        return {'FINISHED'}

# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
def menu_func(self, context):
    self.layout.operator('dicad.aling', icon='UV_FACESEL')
