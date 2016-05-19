'''
AmasawaTools

Copyright (c) 2016 Amasawa Rasen

This software is released under the MIT License.
http://opensource.org/licenses/mit-license.php
'''
import bpy
import math 
import bmesh
import numpy as np
import random
import copy
from math import radians

bl_info = {
    "name": "AmasawaTools",
    "description": "",
    "author": "AmasawaRasen",
    "version": (1, 0, 5),
    "blender": (2, 7, 7),
    "location": "View3D > Toolbar",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"}

#パスを作る関数
def make_Path(verts):
    bpy.ops.curve.primitive_nurbs_path_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False))
    for i,point in enumerate(bpy.context.scene.objects.active.data.splines[0].points):
        point.co = verts[i]
        
#NURBS円を作る関数
def make_circle(verts):
    bpy.ops.curve.primitive_nurbs_circle_add(radius=0.1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False))
    for i,point in enumerate(bpy.context.scene.objects.active.data.splines[0].points):
        point.co = verts[i]
        
#Bevel用のカーブを作成する
#verts : 頂点配列
#loopFlag : ループするかしないか
#order_uValue : 次数
#resulution_uValue : 解像度
#splineType : NURBS・ベジエ・多角形などのスプラインのタイプ
def make_bevelCurve(verts, loopFlag, order_uValue, resolution_uValue,splineType='NURBS'):
    bpy.ops.curve.primitive_nurbs_circle_add(radius=0.1, view_align=False,
    enter_editmode=False, location=(0, 0, 0), layers=(False, False, False,
    False, False, False, False, False, False, False, False, False, False,
    False, False, False, False, False, True, False))
    curve = bpy.context.scene.objects.active
    #頂点をすべて消す
    curve.data.splines.clear()
    newSpline = curve.data.splines.new(type='NURBS')
    #頂点を追加していく
    newSpline.points.add(len(verts)-1)
    for vert,newPoint in zip(verts,newSpline.points):
        newPoint.co = vert
    #ループにする
    newSpline.use_cyclic_u = loopFlag
    #次数を2にする
    newSpline.order_u = order_uValue
    #解像度を1にする
    newSpline.resolution_u = resolution_uValue
    newSpline.use_endpoint_u = True
    #スプラインのタイプを設定
    newSpline.type = splineType

#オペレータークラス
#オブジェクトの辺をアニメ風の髪に変換
#カーブの再変換もできる
class AnimeHairOperator(bpy.types.Operator):
    bl_idname = "object.animehair"
    bl_label = "AnimeHair"
    bl_options = {'REGISTER','UNDO'}
    bl_description = "メッシュの辺をアニメ風の髪の毛に変換"

    my_int_bevelType = bpy.props.IntProperty(name="BevelType",min=0,max=13)
    my_int_taparType = bpy.props.IntProperty(name="TaperType",min=0,max=7)
    my_float_x = bpy.props.FloatProperty(name="X",default=1.0,min=0.0)
    my_float_y = bpy.props.FloatProperty(name="Y",default=1.0,min=0.0)
    my_float_weight = bpy.props.FloatProperty(name="SoftBody Goal",default=0.3,min=0.0,max=1.0)
    my_float_mass = bpy.props.FloatProperty(name="SoftBody Mass",default=0.3,min=0.0,)
    my_float_goal_friction = bpy.props.FloatProperty(name="SoftBody Friction",default=5.0,min=0.0)
    
    my_simple_flag = bpy.props.BoolProperty(name="simplify Curve")
    my_simple_err = bpy.props.FloatProperty(name="Simple_err",default=0.015,description="値を上げるほどカーブがシンプルになる",min=0.0,step=1)
    my_digout = bpy.props.IntProperty(default=0,name="digout",min=0) #次数
    my_reso = bpy.props.IntProperty(default=3,name="resolusion",min=0) #カーブの解像度

    def execute(self, context):
        #選択オブジェクトを保存
        active = bpy.context.scene.objects.active
        #選択オブジェクトのタイプを保存
        actype = active.type
        #選択オブジェクトがガーブ＆メッシュ以外だったらReturn
        if not (actype=='MESH' or actype=='CURVE'):
            return {'FINISHED'}
        #選択オブジェクトのメッシュがメッシュだったらカーブに変換
        if actype == 'MESH':
        	#カーブに変換
        	bpy.ops.object.convert(target='CURVE')
        
        #Nurbsに変換
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.spline_type_set(type='NURBS') 
        bpy.ops.object.mode_set(mode='OBJECT')
        
        #指定された場合カーブをシンプル化
        if self.my_simple_flag:
            pre_curve = bpy.context.active_object
            bpy.ops.curve.simplify(output='NURBS', error=self.my_simple_err, degreeOut=self.my_digout, keepShort=True)
            #シンプルカーブの設定を変更
            simp_Curve = bpy.context.scene.objects.active
            simp_Curve.data.dimensions = '3D'
            simp_Curve.data.resolution_u = self.my_reso
            #元のカーブを削除
            bpy.ops.object.select_pattern(pattern=pre_curve.name, case_sensitive=False, extend=False)
            bpy.ops.object.delete()
            bpy.ops.object.select_pattern(pattern=simp_Curve.name, case_sensitive=False, extend=False)
            
        #終点とスムーズを設定
        for spline in bpy.context.scene.objects.active.data.splines:
            spline.use_endpoint_u = True #終点を設定
            spline.use_smooth = True #スムーズを設定
            
        #元々設定されているベベルとテーパーを削除
        taperobj = bpy.context.scene.objects.active.data.taper_object
        bevelobj = bpy.context.scene.objects.active.data.bevel_object
        for scene in bpy.data.scenes:
            for obj in scene.objects:
                if obj == taperobj:
                    scene.objects.unlink(taperobj)
                if obj == bevelobj:
                    scene.objects.unlink(bevelobj)
        if taperobj != None:
            bpy.data.objects.remove(taperobj)
        if bevelobj != None:
            bpy.data.objects.remove(bevelobj)
    
        #テイパーを設定
        target = bpy.context.scene.objects.active
        if self.my_int_taparType == 0:
            for spline in bpy.context.active_object.data.splines:
                spline.points[len(spline.points)-1].radius = 0.0
        elif self.my_int_taparType == 1:
            for spline in bpy.context.active_object.data.splines:
                for point in spline.points:
                    point.radius = 1.0
        elif self.my_int_taparType == 2:
            verts = [(-2.0, 1.29005, 0.0, 1.0), (-1.0, 0.97704, 0.0, 1.0), (0.0, 0.67615, 0.0, 1.0), (1.0, 0.33936, 0.0, 1.0), (2.0, 0.0, 0.0, 1.0)]
            make_Path(verts)
        elif self.my_int_taparType == 3:
            verts = [(-2.0, 0.82815, 0.0, 1.0), (-1.0, 1.08073, 0.0, 1.0), (0.0, 1.12222, 0.0, 1.0), (1.0, 0.14653, 0.0, 1.0), (2.0, 0.0, 0.0, 1.0)]
            make_Path(verts)
        elif self.my_int_taparType == 4:
            verts = [(-2.0, 1.74503, 0.0, 1.0), (-1.0, 1.74503, 0.0, 1.0), (0.0, 1.74503, 0.0, 1.0), (1.0, 1.74503, 0.0, 1.0), (2.0, 0.0, 0.0, 1.0)]
            make_Path(verts)
        elif self.my_int_taparType == 5:
            verts = [(-2.0, 0.0, 0.0, 1.0), (-1.0, 1.517, 0.0, 1.0), (0.0, 1.9242, 0.0, 1.0), (1.0, 1.81018, 0.0, 1.0), (2.0, 0.0, 0.0, 1.0)]
            make_Path(verts)
        elif self.my_int_taparType == 6:
            verts = [(-2.0, 1.6929, 0.0, 1.0), (-1.0, 0.79381, 0.0, 1.0), (0.0, 0.3801, 0.0, 1.0), (1.0, 0.12926, 0.0, 1.0), (2.0, 0.0, 0.0, 1.0)]
            make_Path(verts)
        elif self.my_int_taparType == 7:
            verts = [(-2.0, 1.17495, 0.0, 1.0), (-1.0, 1.27268, 0.0, 1.0), (0.0, 0.9632, 0.0, 1.0), (1.0, -1.26827, 0.0, 1.0), (2.0, 0.0, 0.0, 1.0)]
            make_Path(verts)
        else:
            print("errer 01")
        target.data.taper_object = bpy.context.scene.objects.active
        bpy.context.scene.objects.active = target
        
        #ベベルを設定
        target = bpy.context.scene.objects.active
        if self.my_int_bevelType == 0:
            verts = [(0.0, -0.1, 0.0, 1.0), (-0.1, -0.1, 0.0, 0.354), (-0.1, 0.0, 0.0, 1.0), (-0.1, 0.1, 0.0, 0.354), (0.0, 0.1, 0.0, 1.0), (0.1, 0.1, 0.0, 0.354), (0.1, 0.0, 0.0, 1.0), (0.1, -0.1, 0.0, 0.354)]
            make_bevelCurve(verts,True,4,3)
        elif self.my_int_bevelType == 1:
            verts = [(0.0, -0.1, 0.0, 1.0), (-0.01341, -0.01341, 0.0, 0.354), (-0.1, 0.0, 0.0, 1.0), (-0.01341, 0.01341, 0.0, 0.354), (0.0, 0.1, 0.0, 1.0), (0.01341, 0.01341, 0.0, 0.354), (0.1, 0.0, 0.0, 1.0), (0.01341, -0.01341, 0.0, 0.354)]
            make_bevelCurve(verts,True,4,3)
        elif self.my_int_bevelType == 2:
            verts = [(0.0, -0.05443, 0.0, 1.0), (-0.10876, -0.05093, 0.0, 0.354), (-0.15258, 0.05083, 0.0, 1.0), (-0.04917, 0.01237, 0.0, 0.354), (0.0, 0.08072, 0.0, 1.0), (0.04216, 0.00711, 0.0, 0.354), (0.17186, 0.05083, 0.0, 1.0), (0.10351, -0.04917, 0.0, 0.354)]
            make_bevelCurve(verts,True,4,3)
        elif self.my_int_bevelType == 3:
            verts = [(0.0, -0.1, 0.0, 1.0), (-0.1, -0.1, 0.0, 0.354), (-0.15173, -0.07836, 0.0, 1.0), (-0.11293, 0.07718, 0.0, 0.354), (0.0, 0.1, 0.0, 1.0), (0.12282, 0.0749, 0.0, 0.354), (0.1601, -0.07608, 0.0, 1.0), (0.1, -0.1, 0.0, 0.354)]
            make_bevelCurve(verts,True,4,3)
        elif self.my_int_bevelType == 4:
            verts = [(0.0, -0.1, 0.0, 1.0), (-0.1, -0.1, 0.0, 0.354), (-0.15173, -0.07836, 0.0, 1.0), (-0.02207, -0.02882, 0.0, 0.354), (0.0, 0.1, 0.0, 1.0), (0.03385, -0.02542, 0.0, 0.354), (0.1601, -0.07608, 0.0, 1.0), (0.1, -0.1, 0.0, 0.354)]
            make_bevelCurve(verts,True,4,3)
        elif self.my_int_bevelType == 5:
            verts = [(0.0,-0.10737,0.0,1.0),(-0.02482,-0.05971,0.0,1.0),(-0.07637,-0.07637,0.0,1.0)\
            ,(-0.05971,-0.02482,0.0,1.0),(-0.10737,0.0,0.0,1.0),(-0.05971,0.02482,0.0,1.0)\
            ,(-0.07637,0.07637,0.0,1.0),(-0.02482,0.05971,0.0,1.0),(0.0,0.10737,0.0,1.0)\
            ,(0.02482,0.05971,0.0,1.0),(0.07637,0.07637,0.0,1.0),(0.05971,0.02482,0.0,1.0)\
            ,(0.10737,0.0,0.0,1.0),(0.05971,-0.02482,0.0,1.0),(0.07637,-0.07637,0.0,1.0)\
            ,(0.02482,-0.05971,0.0,1.0)]
            make_bevelCurve(verts,True,2,1)
        elif self.my_int_bevelType == 6:
            verts = [(-0.10737,0.0,0.0,1.0),(-0.05971,0.02482,0.0,1.0)\
            ,(-0.07637,0.07637,0.0,1.0),(-0.02482,0.05971,0.0,1.0),(0.0,0.10737,0.0,1.0)\
            ,(0.02482,0.05971,0.0,1.0),(0.07637,0.07637,0.0,1.0),(0.05971,0.02482,0.0,1.0)\
            ,(0.10737,0.0,0.0,1.0)]
            make_bevelCurve(verts,False,2,1,'POLY')
        elif self.my_int_bevelType == 7:
            verts = [(-0.21377,-0.01224,0.0,1.0),(-0.21369,0.01544,0.0,1.0),(-0.05366,0.01465,0.0,1.0),\
            (0.0,0.08072,0.0,1.0),(0.04366,0.01472,0.0,1.0),(0.23172,0.01658,0.0,1.0),\
            (0.23112,-0.00807,0.0,1.0)]
            make_bevelCurve(verts,False,4,3)
        elif self.my_int_bevelType == 8:
            verts = [(-0.21369,-0.00024,0.0,1.0),(0.0,0.06504,0.0,1.0),\
            (0.23172,0.0009,0.0,1.0)]
            make_bevelCurve(verts,False,3,3)
        elif self.my_int_bevelType == 9:
            verts = [(-0.21369,-0.00024,0.0,1.0),(0.0,-0.06517,0.0,1.0),\
            (0.23172,0.0009,0.0,1.0)]
            make_bevelCurve(verts,False,3,3)
        elif self.my_int_bevelType == 10:
            verts = [(-0.21369,-0.00024,0.0,1.0),(0.23172,0.0009,0.0,1.0)]
            make_bevelCurve(verts,False,2,2)
        elif self.my_int_bevelType == 11:
            verts = [(0.0,-0.00981,0.0,1.0),(-0.160276,-0.012221,0.0,1.0),(-0.179911,-0.052557,0.0,1.0),
            (-0.208451,0.0,0.0,1.0),(-0.17869,0.051167,0.0,1.0),(-0.159358,0.00654,0.0,1.0),
            (0.0,-0.00414,0.0,1.0),(0.169297,0.008569,0.0,1.0),(0.186631,0.039629,0.0,1.0),
            (0.215239,0.0,0.0,1.0),(0.186103,-0.035806,0.0,1.0),(0.151654,-0.014581,0.0,1.0)]
            make_bevelCurve(verts,True,6,2)
        elif self.my_int_bevelType == 12:
            verts = [(-0.179911,-0.029543,0.0,1.0),
            (-0.208451,0.0,0.0,1.0),(-0.17869,0.051167,0.0,1.0),(-0.159358,0.00654,0.0,1.0),
            (0.0,-0.00414,0.0,1.0),(0.169297,0.008569,0.0,1.0),(0.186631,0.039629,0.0,1.0),
            (0.215239,0.0,0.0,1.0),(0.186103,-0.035806,0.0,1.0)]
            make_bevelCurve(verts,False,6,2)
        elif self.my_int_bevelType == 13:
            verts = [(-0.21369,0.0,0.0,1.0),(-0.185852,0.016927,0.0,1.0),(-0.158014,0.0,0.0,1.0),
            (-0.130176,0.017069,0.0,1.0),(-0.102337,0.0,0.0,1.0),(-0.074499,0.017212,0.0,1.0),
            (-0.046661,0.0,0.0,1.0),(-0.018823,0.017354,0.0,1.0),(0.009015,0.0,0.0,1.0),
            (0.036853,0.017497,0.0,1.0),(0.064691,0.0,0.0,1.0),(0.092529,0.017639,0.0,1.0),
            (0.120367,0.0,0.0,1.0),(0.148206,0.017782,0.0,1.0),(0.176044,0.0,0.0,1.0),
            (0.203882,0.017924,0.0,1.0),(0.23172,0.0,0.0,1.0)]
            make_bevelCurve(verts,False,2,1,'POLY')
        else:
            print("errer 02")
        bpy.context.object.scale[0] = self.my_float_x
        bpy.context.object.scale[1] = self.my_float_y
        target.data.bevel_object = bpy.context.scene.objects.active
        bpy.context.scene.objects.active = target
        
        #UVを設定
        bpy.context.object.data.use_uv_as_generated = True
        bpy.context.object.data.use_fill_caps = False

        #選択オブジェクトの名前を取得
        objname = bpy.context.scene.objects.active.data.name
        
        #元々がメッシュだったらゴールウェイトを設定
        if actype == 'MESH':
	        #すべてのpointsのゴールウェイトに0を設定
	        for spline in bpy.data.curves[objname].splines:
	            for point in spline.points:
	                point.weight_softbody = self.my_float_weight
	        #根本とその次のゴールウェイトに1を設定
	        for spline in bpy.data.curves[objname].splines:
	            spline.points[0].weight_softbody = 1
	            spline.points[1].weight_softbody = 1
            
        #ソフトボディを設定
        bpy.ops.object.modifier_add(type='SOFT_BODY')
        bpy.context.scene.objects.active.soft_body.mass = self.my_float_mass
        bpy.context.scene.objects.active.soft_body.goal_friction = self.my_float_goal_friction
        bpy.context.scene.objects.active.soft_body.goal_default = 1.0
        softbody = bpy.context.scene.objects.active.modifiers[0]
        for m in bpy.context.scene.objects.active.modifiers:
        	if m.type == 'SOFT_BODY':
        		softbody = m
        softbody.point_cache.frame_step = 1
        return {'FINISHED'}
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
#カーブの全制御点の半径の値をソフトボディウェイトにコピー
class Radius2weight(bpy.types.Operator):
    bl_idname = "object.radiustoweight"
    bl_label = "Radius -> SoftBody_Weight"
    bl_options = {'REGISTER','UNDO'}
    bl_description = "カーブの全制御点の半径の値をソフトボディウェイトにコピー"

    my_float_max_radius = bpy.props.FloatProperty(name="Threshold",default=1.0,min=0.0)

    def execute(self, context):
        active = bpy.context.scene.objects.active
        for spline in active.data.splines:
            for point in spline.points:
                #しきい値以下だったらコピー
                if self.my_float_max_radius >= point.radius:
                    point.weight_softbody = point.radius
        return {'FINISHED'}

#Curveをアーマチュア付きメッシュに変換
class Hair2MeshOperator(bpy.types.Operator):
    bl_idname = "object.hair2mesh"
    bl_label = "Hair -> Mesh"
    bl_options = {'REGISTER','UNDO'}
    bl_description = "Curveをアーマチュア付きメッシュに変換"

    my_boneName = bpy.props.StringProperty(name="BoneName",default="Untitled")
    my_ystretch = bpy.props.BoolProperty(name="Y stretch")
    my_radius = bpy.props.BoolProperty(name="Radius",default = False)
    my_hide_select = bpy.props.BoolProperty(name="hide select", default=False)

    def execute(self, context):
        active = bpy.context.scene.objects.active
        curveList = []
        amaList = []
        meshList = []
        defaultrot = active.rotation_euler
        for i,spline in enumerate(active.data.splines):
            #スプラインの頂点が一つしか無かったら処理を中止して次に行く
            if len(spline.points) <= 1:
                continue
            #スプライン一つ一つにカーブオブジェクトを作る
            pos = active.location
            bpy.ops.curve.primitive_nurbs_path_add(radius=1, view_align=False,
                enter_editmode=False, location=pos)
            #Curveの設定からコピーできるものをコピーする
            curve = bpy.context.scene.objects.active
            oldCurve = active
            #splineを全て消し、既存のものからコピーする
            curve.data.splines.clear()
            newSpline = curve.data.splines.new(type='NURBS')
            newSpline.points.add(len(spline.points)-1)
            for point,newPoint in zip(spline.points,newSpline.points):
                newPoint.co = point.co
                newPoint.radius = point.radius
                newPoint.tilt = point.tilt
                newPoint.weight_softbody = point.weight_softbody
            newSpline.use_smooth = spline.use_smooth
            newSpline.use_endpoint_u = spline.use_endpoint_u
            newSpline.use_bezier_u = spline.use_bezier_u
            newSpline.id_data.bevel_object = spline.id_data.bevel_object
            newSpline.id_data.taper_object = spline.id_data.taper_object
            newSpline.id_data.use_fill_caps = False
            newSpline.id_data.resolution_u = spline.id_data.resolution_u
            newSpline.id_data.render_resolution_u = spline.id_data.render_resolution_u
            newSpline.order_u = spline.order_u
            newSpline.resolution_u = spline.resolution_u
            curve.data.twist_mode = oldCurve.data.twist_mode
            curve.data.use_auto_texspace = oldCurve.data.use_auto_texspace
            curve.data.use_uv_as_generated = oldCurve.data.use_uv_as_generated
            if newSpline.id_data.bevel_object == None:
                newSpline.id_data.bevel_depth = spline.id_data.bevel_depth
                newSpline.id_data.bevel_resolution = spline.id_data.bevel_resolution
                curve.data.fill_mode = oldCurve.data.fill_mode
                curve.data.offset = oldCurve.data.offset
                curve.data.extrude = oldCurve.data.extrude
                curve.data.bevel_depth = oldCurve.data.bevel_depth
                curve.data.bevel_resolution = oldCurve.data.bevel_resolution
            #ソフトボディを設定
            if oldCurve.soft_body != None:
        	    bpy.ops.object.modifier_add(type='SOFT_BODY')
        	    curve.soft_body.mass = oldCurve.soft_body.mass
        	    curve.soft_body.goal_friction = oldCurve.soft_body.goal_friction 
        	    curve.soft_body.friction = oldCurve.soft_body.friction
        	    curve.soft_body.speed = oldCurve.soft_body.speed
        	    curve.soft_body.goal_default = oldCurve.soft_body.goal_default
        	    curve.soft_body.goal_max = oldCurve.soft_body.goal_max
        	    curve.soft_body.goal_min = oldCurve.soft_body.goal_min
        	    curve.soft_body.goal_spring = oldCurve.soft_body.goal_spring
            #アーマチュアを作る
            bpy.ops.object.armature_add(location=pos,enter_editmode=False)
            activeAma = bpy.context.scene.objects.active
            bpy.ops.object.editmode_toggle()
            bpy.ops.armature.select_all(action='SELECT')
            bpy.ops.armature.delete()
            bpy.ops.armature.bone_primitive_add()
            activeAma.data.edit_bones[0].head = [newSpline.points[0].co[0],
                                                    newSpline.points[0].co[1],
                                                    newSpline.points[0].co[2]]
            activeAma.data.edit_bones[0].name = self.my_boneName + str(i)
            if len(newSpline.points) >= 3:
                for i,newPoint in enumerate(newSpline.points[1:-1]):
                    rootBoneName = activeAma.data.edit_bones[0].name
                    newBone = activeAma.data.edit_bones.new(rootBoneName)
                    newBone.parent = activeAma.data.edit_bones[i]
                    newBone.use_connect = True
                    newBone.head = [newPoint.co[0],
                                    newPoint.co[1],
                                    newPoint.co[2]]
            else:
                newBone = activeAma.data.edit_bones[0]
            lastBone = newBone
            lastBone.tail = [newSpline.points[-1].co[0],
                            newSpline.points[-1].co[1],
                            newSpline.points[-1].co[2]]
            activeAma.data.draw_type = "STICK"
            #ボーンのセグメントを設定（設定しない方が綺麗に動くので終了）
            #for bone in activeAma.data.edit_bones:
            #    bone.bbone_segments = newSpline.order_u
            #カーブを実体化する
            #物理に使うので元のカーブは残す
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = curve
            bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
            bpy.ops.object.convert(target='MESH', keep_original=True)
            meshobj = bpy.context.scene.objects.active
            #マテリアルをコピーする
            if len(oldCurve.data.materials) >= 1:
                material = oldCurve.data.materials[spline.material_index]
                meshobj.data.materials.append(material) 
            #元のカーブは多角形にしてBevelやテイパーやメッシュを外してを設定して、物理として使う
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = curve
            bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
            bebelObj = curve.data.bevel_object
            curve.data.bevel_object = None
            curve.data.taper_object = None
            curve.data.bevel_depth = 0
            curve.data.bevel_resolution = 0
            curve.data.extrude = 0
            newSpline.type = 'POLY'
            #アーマチュアにスプラインIKをセット
            if len(activeAma.pose.bones) >= 1:
                spIK = activeAma.pose.bones[-1].constraints.new("SPLINE_IK")
                spIK.target = curve
                spIK.chain_count = len(activeAma.data.bones)
                spIK.use_chain_offset = False
                spIK.use_y_stretch = self.my_ystretch
                if self.my_radius:
                    spIK.use_curve_radius = True
                else:
                    spIK.use_curve_radius = False
            activeAma.pose.bones[-1]["spIKName"] = curve.name
            curve.data.resolution_u = 64
            #重複した頂点を削除
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_pattern(pattern=meshobj.name, case_sensitive=False, extend=False)
            bpy.context.scene.objects.active = meshobj
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='TOGGLE')
            bpy.ops.mesh.remove_doubles(threshold=0.0001)
            bpy.ops.object.editmode_toggle()
            #自動のウェイトでアーマチュアを設定
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_pattern(pattern=meshobj.name, case_sensitive=False, extend=False)
            bpy.ops.object.select_pattern(pattern=activeAma.name, case_sensitive=False, extend=True)
            bpy.context.scene.objects.active = activeAma
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            #シェイプキーを２つ追加し、一つをBasis、一つをKey1にする
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = curve
            bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
            bpy.ops.object.shape_key_add(from_mix=False)
            bpy.ops.object.shape_key_add(from_mix=False)
            curve.data.shape_keys.key_blocks[1].value = 1
            bpy.context.object.active_shape_key_index = 1
            #Curveをレントゲンにして透けて見えるように
            curve.show_x_ray = True
            #Curveとアーマチュアとメッシュは後でまとめるのでリストにする
            curveList.append(curve)
            amaList.append(activeAma)
            meshList.append(meshobj)
        #Curveの親用のEmptyを作る
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=active.location)
        emptyobj = bpy.context.scene.objects.active
        emptyobj.name = self.my_boneName + "Emp"
        #アーマチュアの親オブジェクトを作る
        bpy.ops.object.armature_add(location=active.location,enter_editmode=False)
        pama = bpy.context.scene.objects.active
        pama.data.bones[0].use_deform = False
        #Curveの親を設定
        for c in curveList:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_pattern(pattern=c.name, case_sensitive=False, extend=False)
            bpy.ops.object.select_pattern(pattern=emptyobj.name, case_sensitive=False, extend=True)
            bpy.context.scene.objects.active = emptyobj
            bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=True)
        #アーマチュアを合成
        bpy.ops.object.select_all(action='DESELECT')
        for ama in amaList:
            bpy.ops.object.select_pattern(pattern=ama.name, case_sensitive=False, extend=True)
        bpy.ops.object.select_pattern(pattern=pama.name, case_sensitive=False, extend=True)
        bpy.context.scene.objects.active = pama
        pama.data.draw_type = "STICK"
        bpy.ops.object.join()
        pama = bpy.context.scene.objects.active
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern=pama.name, case_sensitive=False, extend=False)
        bpy.ops.object.select_pattern(pattern=emptyobj.name, case_sensitive=False, extend=True)
        bpy.context.scene.objects.active = emptyobj
        bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=True)
        pama.name = self.my_boneName
        #メッシュを合成
        bpy.ops.object.select_all(action='DESELECT')
        for m in meshList:
            bpy.ops.object.select_pattern(pattern=m.name, case_sensitive=False, extend=True)
        if len(meshList) >= 1:
            bpy.context.scene.objects.active = meshList[0]
            bpy.ops.object.join()
            activeMesh = bpy.context.scene.objects.active
            activeMesh.modifiers["Armature"].object = pama
            #メッシュを選択不可能オブジェクトにする
            activeMesh.hide_select = self.my_hide_select
        #親エンプティの回転を元のCurveと同じにする
        emptyobj.rotation_euler = defaultrot
        #アーマチュアのデータを随時更新に変更
        pama.use_extra_recalc_data = True
        #このアーマチュアの名前のボーングループをセット
        boneGroups = pama.pose.bone_groups.new(self.my_boneName)
        for bone in pama.pose.bones:
            bone.bone_group = boneGroups
        layers=(False, False,
             False, False, False, False, False, False,
             False, False, False, False, False, False,
             False, False, False, False, False, False,
             False, False, False, True, False, False,
             False, False, False, False, False, False)
        for i,bone in enumerate(pama.data.bones):
            if i != 0:
                bone.layers = layers
        #選択をEmptyに
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern=emptyobj.name, case_sensitive=False, extend=False)
        return {'FINISHED'}
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

#Curveをアーマチュアに変換
class Curve2AmaOperator(bpy.types.Operator):
    bl_idname = "object.curve2ama"
    bl_label = "Curve -> Ama"
    bl_options = {'REGISTER','UNDO'}
    bl_description = "Curveをアーマチュアに変換"

    my_boneName = bpy.props.StringProperty(name="BoneName",default="Untitled")
    my_ystretch = bpy.props.BoolProperty(name="Y stretch")
    my_radius = bpy.props.BoolProperty(name="Radius",default = False)

    def execute(self, context):
        active = bpy.context.scene.objects.active
        curveList = []
        amaList = []
        #meshList = []
        for i,spline in enumerate(active.data.splines):
            #スプラインの頂点が一つしか無かったら処理を中止して次に行く
            if len(spline.points) <= 1:
                continue
            #スプライン一つ一つにカーブオブジェクトを作る
            pos = active.location
            defaultrot = active.rotation_euler
            bpy.ops.curve.primitive_nurbs_path_add(radius=1, view_align=False,
                enter_editmode=False, location=pos)
            #Curveの設定からコピーできるものをコピーする
            curve = bpy.context.scene.objects.active
            oldCurve = active
            #splineを全て消し、既存のものからコピーする
            curve.data.splines.clear()
            newSpline = curve.data.splines.new(type='NURBS')
            newSpline.points.add(len(spline.points)-1)
            for point,newPoint in zip(spline.points,newSpline.points):
                newPoint.co = point.co
                newPoint.radius = point.radius
                newPoint.tilt = point.tilt
                newPoint.weight_softbody = point.weight_softbody
            newSpline.use_smooth = spline.use_smooth
            newSpline.use_endpoint_u = spline.use_endpoint_u
            newSpline.use_bezier_u = spline.use_bezier_u
            newSpline.id_data.bevel_object = spline.id_data.bevel_object
            newSpline.id_data.taper_object = spline.id_data.taper_object
            newSpline.id_data.use_fill_caps = False
            newSpline.id_data.resolution_u = spline.id_data.resolution_u
            newSpline.id_data.render_resolution_u = spline.id_data.render_resolution_u
            newSpline.order_u = spline.order_u
            newSpline.resolution_u = spline.resolution_u
            curve.data.twist_mode = oldCurve.data.twist_mode
            if newSpline.id_data.bevel_object == None:
                newSpline.id_data.bevel_depth = spline.id_data.bevel_depth
                newSpline.id_data.bevel_resolution = spline.id_data.bevel_resolution
            #ソフトボディを設定
            if oldCurve.soft_body != None:
                bpy.ops.object.modifier_add(type='SOFT_BODY')
                curve.soft_body.mass = oldCurve.soft_body.mass
                curve.soft_body.goal_friction = oldCurve.soft_body.goal_friction
                curve.soft_body.friction = oldCurve.soft_body.friction
                curve.soft_body.speed = oldCurve.soft_body.speed
                curve.soft_body.goal_default = oldCurve.soft_body.goal_default
                curve.soft_body.goal_max = oldCurve.soft_body.goal_max
                curve.soft_body.goal_min = oldCurve.soft_body.goal_min
                curve.soft_body.goal_spring = oldCurve.soft_body.goal_spring
            #アーマチュアを作る
            bpy.ops.object.armature_add(location=pos,enter_editmode=False)
            activeAma = bpy.context.scene.objects.active
            bpy.ops.object.editmode_toggle()
            bpy.ops.armature.select_all(action='SELECT')
            bpy.ops.armature.delete()
            bpy.ops.armature.bone_primitive_add()
            activeAma.data.edit_bones[0].head = [newSpline.points[0].co[0],
                                                    newSpline.points[0].co[1],
                                                    newSpline.points[0].co[2]]
            activeAma.data.edit_bones[0].name = self.my_boneName + str(i)
            if len(newSpline.points) >= 3:
                for i,newPoint in enumerate(newSpline.points[1:-1]):
                    rootBoneName = activeAma.data.edit_bones[0].name
                    newBone = activeAma.data.edit_bones.new(rootBoneName)
                    newBone.parent = activeAma.data.edit_bones[i]
                    newBone.use_connect = True
                    newBone.head = [newPoint.co[0],
                                    newPoint.co[1],
                                    newPoint.co[2]]
            else:
                newBone = activeAma.data.edit_bones[0]
            lastBone = newBone
            lastBone.tail = [newSpline.points[-1].co[0],
                            newSpline.points[-1].co[1],
                            newSpline.points[-1].co[2]]
            activeAma.data.draw_type = "STICK"
            #元のカーブは多角形にしてBevelやテイパーやメッシュを外してを設定して、物理として使う
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = curve
            bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
            bebelObj = curve.data.bevel_object
            curve.data.bevel_object = None
            curve.data.taper_object = None
            curve.data.bevel_depth = 0
            curve.data.bevel_resolution = 0
            newSpline.type = 'POLY'
            #アーマチュアにスプラインIKをセット
            if len(activeAma.pose.bones) >= 1:
                spIK = activeAma.pose.bones[-1].constraints.new("SPLINE_IK")
                spIK.target = curve
                spIK.chain_count = len(activeAma.data.bones)
                spIK.use_chain_offset = False
                spIK.use_y_stretch = self.my_ystretch
                if self.my_radius:
                    spIK.use_curve_radius = True
                else:
                    spIK.use_curve_radius = False
                activeAma.pose.bones[-1]["spIKName"] = curve.name
            curve.data.resolution_u = 64
            #シェイプキーを２つ追加し、一つをBasis、一つをKey1にする
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = curve
            bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
            bpy.ops.object.shape_key_add(from_mix=False)
            bpy.ops.object.shape_key_add(from_mix=False)
            curve.data.shape_keys.key_blocks[1].value = 1
            bpy.context.object.active_shape_key_index = 1
            #Curveをレントゲンにして透けて見えるように
            curve.show_x_ray = True
            #Curveとアーマチュアとメッシュは後でまとめるのでリストにする
            curveList.append(curve)
            amaList.append(activeAma)
        #Curveの親用のEmptyを作る
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=active.location)
        emptyobj = bpy.context.scene.objects.active
        emptyobj.name = self.my_boneName + "Emp"
        #アーマチュアの親オブジェクトを作る
        bpy.ops.object.armature_add(location=active.location,enter_editmode=False)
        pama = bpy.context.scene.objects.active
        pama.data.bones[0].use_deform = False
        #Curveの親を設定
        for c in curveList:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_pattern(pattern=c.name, case_sensitive=False, extend=False)
            bpy.ops.object.select_pattern(pattern=emptyobj.name, case_sensitive=False, extend=True)
            bpy.context.scene.objects.active = emptyobj
            bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=True)
        #アーマチュアを合成
        bpy.ops.object.select_all(action='DESELECT')
        for ama in amaList:
            bpy.ops.object.select_pattern(pattern=ama.name, case_sensitive=False, extend=True)
        bpy.ops.object.select_pattern(pattern=pama.name, case_sensitive=False, extend=True)
        bpy.context.scene.objects.active = pama
        pama.data.draw_type = "STICK"
        bpy.ops.object.join()
        pama = bpy.context.scene.objects.active
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern=pama.name, case_sensitive=False, extend=False)
        bpy.ops.object.select_pattern(pattern=emptyobj.name, case_sensitive=False, extend=True)
        bpy.context.scene.objects.active = emptyobj
        bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=True)
        pama.name = self.my_boneName
        #親エンプティの回転を元のCurveと同じにする
        emptyobj.rotation_euler = defaultrot
        #アーマチュアのデータを随時更新に変更
        pama.use_extra_recalc_data = True
        #このアーマチュアの名前のボーングループをセット
        boneGroups = pama.pose.bone_groups.new(self.my_boneName)
        for bone in pama.pose.bones:
            bone.bone_group = boneGroups
        layers=(False, False,
             False, False, False, False, False, False,
             False, False, False, False, False, False,
             False, False, False, False, False, False,
             False, False, False, True, False, False,
             False, False, False, False, False, False)
        for i,bone in enumerate(pama.data.bones):
            if i != 0:
                bone.layers = layers
        #選択をEmptyに
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern=emptyobj.name, case_sensitive=False, extend=False)
        return {'FINISHED'}
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

#Curveを正確なアーマチュア付きメッシュに変換
class Hair2MeshFullOperator(bpy.types.Operator):
    bl_idname = "object.hair2meshfull"
    bl_label = "Hair -> Mesh_Full"
    bl_options = {'REGISTER','UNDO'}
    bl_description = "Curveを正確なアーマチュア付きメッシュに変換"

    my_boneName = bpy.props.StringProperty(name="BoneName",default="Untitled")
    my_ystretch = bpy.props.BoolProperty(name="Y stretch")
    my_radius = bpy.props.BoolProperty(name="Radius",default = False)
    my_hide_select = bpy.props.BoolProperty(name="hide select", default=False)

    def execute(self, context):
        active = bpy.context.scene.objects.active
        curveList = []
        amaList = []
        meshList = []
        for i,spline in enumerate(active.data.splines):
            #スプラインの頂点が一つしか無かったら処理を中止して次に行く
            if len(spline.points) <= 1:
                continue
            #スプライン一つ一つにカーブオブジェクトを作る
            pos = active.location
            defaultrot = active.rotation_euler
            bpy.ops.curve.primitive_nurbs_path_add(radius=1, view_align=False,
                enter_editmode=False, location=pos)
            #Curveの設定からコピーできるものをコピーする
            curve = bpy.context.scene.objects.active
            oldCurve = active
            #splineを全て消し、既存のものからコピーする
            curve.data.splines.clear()
            newSpline = curve.data.splines.new(type='NURBS')
            newSpline.points.add(len(spline.points)-1)
            for point,newPoint in zip(spline.points,newSpline.points):
                newPoint.co = point.co
                newPoint.radius = point.radius
                newPoint.tilt = point.tilt
                newPoint.weight_softbody = point.weight_softbody
            newSpline.use_smooth = spline.use_smooth
            newSpline.use_endpoint_u = spline.use_endpoint_u
            newSpline.use_bezier_u = spline.use_bezier_u
            newSpline.id_data.bevel_object = spline.id_data.bevel_object
            newSpline.id_data.taper_object = spline.id_data.taper_object
            newSpline.id_data.use_fill_caps = False
            newSpline.id_data.resolution_u = spline.id_data.resolution_u
            newSpline.id_data.render_resolution_u = spline.id_data.render_resolution_u
            newSpline.order_u = spline.order_u
            newSpline.resolution_u = spline.resolution_u
            curve.data.twist_mode = oldCurve.data.twist_mode
            curve.data.use_auto_texspace = oldCurve.data.use_auto_texspace
            curve.data.use_uv_as_generated = oldCurve.data.use_uv_as_generated
            if newSpline.id_data.bevel_object == None:
                newSpline.id_data.bevel_depth = spline.id_data.bevel_depth
                newSpline.id_data.bevel_resolution = spline.id_data.bevel_resolution
                curve.data.fill_mode = oldCurve.data.fill_mode
                curve.data.offset = oldCurve.data.offset
                curve.data.extrude = oldCurve.data.extrude
                curve.data.bevel_depth = oldCurve.data.bevel_depth
                curve.data.bevel_resolution = oldCurve.data.bevel_resolution
            #ソフトボディを設定
            if oldCurve.soft_body != None:
                bpy.ops.object.modifier_add(type='SOFT_BODY')
                curve.soft_body.mass = oldCurve.soft_body.mass
                curve.soft_body.goal_friction = oldCurve.soft_body.goal_friction
                curve.soft_body.friction = oldCurve.soft_body.friction
                curve.soft_body.speed = oldCurve.soft_body.speed
                curve.soft_body.goal_default = oldCurve.soft_body.goal_default
                curve.soft_body.goal_max = oldCurve.soft_body.goal_max
                curve.soft_body.goal_min = oldCurve.soft_body.goal_min
                curve.soft_body.goal_spring = oldCurve.soft_body.goal_spring
            #アーマチュア制作用の基準カーブを作る
            bpy.context.scene.objects.active = curve
            bpy.ops.object.duplicate()
            stdCurve = bpy.context.scene.objects.active
            stdCurve.name = "stdCurve"
            stdCurve.data.bevel_depth = 0
            stdCurve.data.extrude = 0
            stdCurve.data.bevel_object = None
            bpy.ops.object.convert(target='MESH', keep_original=False)
            stdCurveObj = bpy.context.scene.objects.active
            #アーマチュアを作る
            bpy.ops.object.armature_add(location=pos,enter_editmode=False)
            activeAma = bpy.context.scene.objects.active
            bpy.ops.object.editmode_toggle()
            bpy.ops.armature.select_all(action='SELECT')
            bpy.ops.armature.delete()
            bpy.ops.armature.bone_primitive_add()
            activeAma.data.edit_bones[0].head = [stdCurveObj.data.vertices[0].co[0],
                                                    stdCurveObj.data.vertices[0].co[1],
                                                    stdCurveObj.data.vertices[0].co[2]]
            activeAma.data.edit_bones[0].name = self.my_boneName + str(i)
            if len(stdCurveObj.data.vertices) >= 3:
                for i,newPoint in enumerate(stdCurveObj.data.vertices[1:-1]):
                    rootBoneName = activeAma.data.edit_bones[0].name
                    newBone = activeAma.data.edit_bones.new(rootBoneName)
                    newBone.parent = activeAma.data.edit_bones[i]
                    newBone.use_connect = True
                    newBone.head = [newPoint.co[0],
                                    newPoint.co[1],
                                    newPoint.co[2]]
            else:
                newBone = activeAma.data.edit_bones[0]
            lastBone = newBone
            lastBone.tail = [stdCurveObj.data.vertices[-1].co[0],
                            stdCurveObj.data.vertices[-1].co[1],
                            stdCurveObj.data.vertices[-1].co[2]]
            activeAma.data.draw_type = "STICK"
            #カーブを実体化する
            #物理に使うので元のカーブは残す
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = curve
            bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
            bpy.ops.object.convert(target='MESH', keep_original=True)
            meshobj = bpy.context.scene.objects.active
            #マテリアルをコピーする
            if len(oldCurve.data.materials) >= 1:
                material = oldCurve.data.materials[spline.material_index]
                meshobj.data.materials.append(material)
            #元のカーブは多角形にしてBevelやテイパーやメッシュを外してを設定して、物理として使う
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = curve
            bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
            bebelObj = curve.data.bevel_object
            curve.data.bevel_object = None
            curve.data.taper_object = None
            curve.data.bevel_depth = 0
            curve.data.bevel_resolution = 0
            #newSpline.type = curve.data.spline[0].type
            #アーマチュアにスプラインIKをセット
            if len(activeAma.pose.bones) >= 1:
                spIK = activeAma.pose.bones[-1].constraints.new("SPLINE_IK")
                spIK.target = curve
                spIK.chain_count = len(activeAma.data.bones)
                spIK.use_chain_offset = False
                spIK.use_y_stretch = self.my_ystretch
                if self.my_radius:
                    spIK.use_curve_radius = True
                else:
                    spIK.use_curve_radius = False
                activeAma.pose.bones[-1]["spIKName"] = curve.name
            curve.data.resolution_u = 64
            #重複した頂点を削除
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_pattern(pattern=meshobj.name, case_sensitive=False, extend=False)
            bpy.context.scene.objects.active = meshobj
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='TOGGLE')
            bpy.ops.mesh.remove_doubles(threshold=0.0001)
            bpy.ops.object.editmode_toggle()
            #自動のウェイトでアーマチュアを設定
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_pattern(pattern=meshobj.name, case_sensitive=False, extend=False)
            bpy.ops.object.select_pattern(pattern=activeAma.name, case_sensitive=False, extend=True)
            bpy.context.scene.objects.active = activeAma
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            #シェイプキーを２つ追加し、一つをBasis、一つをKey1にする
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = curve
            bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
            bpy.ops.object.shape_key_add(from_mix=False)
            bpy.ops.object.shape_key_add(from_mix=False)
            curve.data.shape_keys.key_blocks[1].value = 1
            bpy.context.object.active_shape_key_index = 1
            #Curveをレントゲンにして透けて見えるように
            curve.show_x_ray = True
            #Curveとアーマチュアとメッシュは後でまとめるのでリストにする
            curveList.append(curve)
            amaList.append(activeAma)
            meshList.append(meshobj)
            #基準カーブ消去
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = stdCurveObj
            bpy.ops.object.select_pattern(pattern=stdCurveObj.name, case_sensitive=False, extend=False)
            bpy.ops.object.delete(use_global=False)
        #Curveの親用のEmptyを作る
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=active.location)
        emptyobj = bpy.context.scene.objects.active
        emptyobj.name = self.my_boneName + "Emp"
        #アーマチュアの親オブジェクトを作る
        bpy.ops.object.armature_add(location=active.location,enter_editmode=False)
        pama = bpy.context.scene.objects.active
        pama.data.bones[0].use_deform = False
        #Curveの親を設定
        for c in curveList:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_pattern(pattern=c.name, case_sensitive=False, extend=False)
            bpy.ops.object.select_pattern(pattern=emptyobj.name, case_sensitive=False, extend=True)
            bpy.context.scene.objects.active = emptyobj
            bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=True)
        #アーマチュアを合成
        bpy.ops.object.select_all(action='DESELECT')
        for ama in amaList:
            bpy.ops.object.select_pattern(pattern=ama.name, case_sensitive=False, extend=True)
        bpy.ops.object.select_pattern(pattern=pama.name, case_sensitive=False, extend=True)
        bpy.context.scene.objects.active = pama
        pama.data.draw_type = "STICK"
        bpy.ops.object.join()
        pama = bpy.context.scene.objects.active
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern=pama.name, case_sensitive=False, extend=False)
        bpy.ops.object.select_pattern(pattern=emptyobj.name, case_sensitive=False, extend=True)
        bpy.context.scene.objects.active = emptyobj
        bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=True)
        pama.name = self.my_boneName
        #メッシュを合成
        bpy.ops.object.select_all(action='DESELECT')
        for m in meshList:
            bpy.ops.object.select_pattern(pattern=m.name, case_sensitive=False, extend=True)
        if len(meshList) >= 1:
            bpy.context.scene.objects.active = meshList[0]
            bpy.ops.object.join()
            activeMesh = bpy.context.scene.objects.active
            activeMesh.modifiers["Armature"].object = pama
            #メッシュを選択不可能オブジェクトにする
            activeMesh.hide_select = self.my_hide_select
        #親エンプティの回転を元のCurveと同じにする
        emptyobj.rotation_euler = defaultrot
        #アーマチュアのデータを随時更新に変更
        pama.use_extra_recalc_data = True
        #このアーマチュアの名前のボーングループをセット
        boneGroups = pama.pose.bone_groups.new(self.my_boneName)
        for bone in pama.pose.bones:
            bone.bone_group = boneGroups
        layers=(False, False,
             False, False, False, False, False, False,
             False, False, False, False, False, False,
             False, False, False, False, False, False,
             False, False, False, True, False, False,
             False, False, False, False, False, False)
        for i,bone in enumerate(pama.data.bones):
            if i != 0:
                bone.layers = layers
        #選択をEmptyに
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern=emptyobj.name, case_sensitive=False, extend=False)
        return {'FINISHED'}
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

#Curveを正確なアーマチュアに変換
class Curve2AmaFullOperator(bpy.types.Operator):
    bl_idname = "object.curve2amafull"
    bl_label = "Curve -> Ama_Full"
    bl_options = {'REGISTER','UNDO'}
    bl_description = "Curveを正確なアーマチュアに変換"

    my_boneName = bpy.props.StringProperty(name="BoneName",default="Untitled")
    my_ystretch = bpy.props.BoolProperty(name="Y stretch")
    my_radius = bpy.props.BoolProperty(name="Radius",default = False)

    def execute(self, context):
        active = bpy.context.scene.objects.active
        curveList = []
        amaList = []
        #meshList = []
        for i,spline in enumerate(active.data.splines):
            #スプラインの頂点が一つしか無かったら処理を中止して次に行く
            if len(spline.points) <= 1:
                continue
            #スプライン一つ一つにカーブオブジェクトを作る
            pos = active.location
            defaultrot = active.rotation_euler
            bpy.ops.curve.primitive_nurbs_path_add(radius=1, view_align=False,
                enter_editmode=False, location=pos)
            #Curveの設定からコピーできるものをコピーする
            curve = bpy.context.scene.objects.active
            oldCurve = active
            #splineを全て消し、既存のものからコピーする
            curve.data.splines.clear()
            newSpline = curve.data.splines.new(type='NURBS')
            newSpline.points.add(len(spline.points)-1)
            for point,newPoint in zip(spline.points,newSpline.points):
                newPoint.co = point.co
                newPoint.radius = point.radius
                newPoint.tilt = point.tilt
                newPoint.weight_softbody = point.weight_softbody
            newSpline.use_smooth = spline.use_smooth
            newSpline.use_endpoint_u = spline.use_endpoint_u
            newSpline.use_bezier_u = spline.use_bezier_u
            newSpline.id_data.bevel_object = spline.id_data.bevel_object
            newSpline.id_data.taper_object = spline.id_data.taper_object
            newSpline.id_data.use_fill_caps = False
            newSpline.id_data.resolution_u = spline.id_data.resolution_u
            newSpline.id_data.render_resolution_u = spline.id_data.render_resolution_u
            newSpline.order_u = spline.order_u
            newSpline.resolution_u = spline.resolution_u
            curve.data.twist_mode = oldCurve.data.twist_mode
            if newSpline.id_data.bevel_object == None:
                newSpline.id_data.bevel_depth = spline.id_data.bevel_depth
                newSpline.id_data.bevel_resolution = spline.id_data.bevel_resolution
            #ソフトボディを設定
            if oldCurve.soft_body != None:
                bpy.ops.object.modifier_add(type='SOFT_BODY')
                curve.soft_body.mass = oldCurve.soft_body.mass
                curve.soft_body.goal_friction = oldCurve.soft_body.goal_friction
                curve.soft_body.friction = oldCurve.soft_body.friction
                curve.soft_body.speed = oldCurve.soft_body.speed
                curve.soft_body.goal_default = oldCurve.soft_body.goal_default
                curve.soft_body.goal_max = oldCurve.soft_body.goal_max
                curve.soft_body.goal_min = oldCurve.soft_body.goal_min
                curve.soft_body.goal_spring = oldCurve.soft_body.goal_spring
            #アーマチュア制作用の基準カーブを作る
            bpy.context.scene.objects.active = curve
            bpy.ops.object.duplicate()
            stdCurve = bpy.context.scene.objects.active
            stdCurve.name = "stdCurve"
            stdCurve.data.bevel_depth = 0
            stdCurve.data.extrude = 0
            stdCurve.data.bevel_object = None
            bpy.ops.object.convert(target='MESH', keep_original=False)
            stdCurveObj = bpy.context.scene.objects.active
            #アーマチュアを作る
            bpy.ops.object.armature_add(location=pos,enter_editmode=False)
            activeAma = bpy.context.scene.objects.active
            bpy.ops.object.editmode_toggle()
            bpy.ops.armature.select_all(action='SELECT')
            bpy.ops.armature.delete()
            bpy.ops.armature.bone_primitive_add()
            
            activeAma.data.edit_bones[0].head = [stdCurveObj.data.vertices[0].co[0],
                                                    stdCurveObj.data.vertices[0].co[1],
                                                    stdCurveObj.data.vertices[0].co[2]]
            activeAma.data.edit_bones[0].name = self.my_boneName + str(i)
            if len(stdCurveObj.data.vertices) >= 3:
                for i,newPoint in enumerate(stdCurveObj.data.vertices[1:-1]):
                    rootBoneName = activeAma.data.edit_bones[0].name
                    newBone = activeAma.data.edit_bones.new(rootBoneName)
                    newBone.parent = activeAma.data.edit_bones[i]
                    newBone.use_connect = True
                    newBone.head = [newPoint.co[0],
                                    newPoint.co[1],
                                    newPoint.co[2]]
            else:
                newBone = activeAma.data.edit_bones[0]
            lastBone = newBone
            lastBone.tail = [stdCurveObj.data.vertices[-1].co[0],
                            stdCurveObj.data.vertices[-1].co[1],
                            stdCurveObj.data.vertices[-1].co[2]]
            activeAma.data.draw_type = "STICK"
            #元のカーブは多角形にしてBevelやテイパーやメッシュを外してを設定して、物理として使う
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = curve
            bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
            bebelObj = curve.data.bevel_object
            curve.data.bevel_object = None
            curve.data.taper_object = None
            curve.data.bevel_depth = 0
            curve.data.bevel_resolution = 0
            #newSpline.type = curve.data.spline[0].type
            #アーマチュアにスプラインIKをセット
            if len(activeAma.pose.bones) >= 1:
                spIK = activeAma.pose.bones[-1].constraints.new("SPLINE_IK")
                spIK.target = curve
                spIK.chain_count = len(activeAma.data.bones)
                spIK.use_chain_offset = False
                spIK.use_y_stretch = self.my_ystretch
                if self.my_radius:
                    spIK.use_curve_radius = True
                else:
                    spIK.use_curve_radius = False
                activeAma.pose.bones[-1]["spIKName"] = curve.name
            curve.data.resolution_u = 64
            #シェイプキーを２つ追加し、一つをBasis、一つをKey1にする
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = curve
            bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
            bpy.ops.object.shape_key_add(from_mix=False)
            bpy.ops.object.shape_key_add(from_mix=False)
            curve.data.shape_keys.key_blocks[1].value = 1
            bpy.context.object.active_shape_key_index = 1
            #Curveをレントゲンにして透けて見えるように
            curve.show_x_ray = True
            #Curveとアーマチュアとメッシュは後でまとめるのでリストにする
            curveList.append(curve)
            amaList.append(activeAma)
            #基準カーブ消去
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = stdCurveObj
            bpy.ops.object.select_pattern(pattern=stdCurveObj.name, case_sensitive=False, extend=False)
            bpy.ops.object.delete(use_global=False)
        #Curveの親用のEmptyを作る
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=active.location)
        emptyobj = bpy.context.scene.objects.active
        emptyobj.name = self.my_boneName + "Emp"
        #アーマチュアの親オブジェクトを作る
        bpy.ops.object.armature_add(location=active.location,enter_editmode=False)
        pama = bpy.context.scene.objects.active
        pama.data.bones[0].use_deform = False
        #Curveの親を設定
        for c in curveList:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_pattern(pattern=c.name, case_sensitive=False, extend=False)
            bpy.ops.object.select_pattern(pattern=emptyobj.name, case_sensitive=False, extend=True)
            bpy.context.scene.objects.active = emptyobj
            bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=True)
        #アーマチュアを合成
        bpy.ops.object.select_all(action='DESELECT')
        for ama in amaList:
            bpy.ops.object.select_pattern(pattern=ama.name, case_sensitive=False, extend=True)
        bpy.ops.object.select_pattern(pattern=pama.name, case_sensitive=False, extend=True)
        bpy.context.scene.objects.active = pama
        pama.data.draw_type = "STICK"
        bpy.ops.object.join()
        pama = bpy.context.scene.objects.active
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern=pama.name, case_sensitive=False, extend=False)
        bpy.ops.object.select_pattern(pattern=emptyobj.name, case_sensitive=False, extend=True)
        bpy.context.scene.objects.active = emptyobj
        bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=True)
        pama.name = self.my_boneName
        #親エンプティの回転を元のCurveと同じにする
        emptyobj.rotation_euler = defaultrot
        #アーマチュアのデータを随時更新に変更
        pama.use_extra_recalc_data = True
        #このアーマチュアの名前のボーングループをセット
        boneGroups = pama.pose.bone_groups.new(self.my_boneName)
        for bone in pama.pose.bones:
            bone.bone_group = boneGroups
        layers=(False, False,
             False, False, False, False, False, False,
             False, False, False, False, False, False,
             False, False, False, False, False, False,
             False, False, False, True, False, False,
             False, False, False, False, False, False)
        for i,bone in enumerate(pama.data.bones):
            if i != 0:
                bone.layers = layers
        #選択をEmptyに
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern=emptyobj.name, case_sensitive=False, extend=False)
        return {'FINISHED'}
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

#全てのボーンのスプラインIKのミュートを外す
class ViewSpIKOperator(bpy.types.Operator):
	bl_idname = "object.viewspik"
	bl_label = "ViewSPIK"
	bl_options = {'REGISTER','UNDO'}
	bl_description = "全てのボーンに付いているスプラインIKからミュートを外す"
	def execute(self, context):
		ama = bpy.context.scene.objects.active
		for bone in ama.pose.bones:
		    if len(bone.constraints) >= 1:
		        for con in bone.constraints:
		            if con.type == "SPLINE_IK":
		                con.mute = False
		bpy.ops.object.editmode_toggle()
		bpy.ops.object.editmode_toggle()
		return {'FINISHED'}

#全てのボーンのスプラインIKをミュート
class HiddenSpIKOperator(bpy.types.Operator):
	bl_idname = "object.hiddenspik"
	bl_label = "MuteSPIK"
	bl_options = {'REGISTER','UNDO'}
	bl_description = "全てのボーンに付いているスプラインIKをミュート"
	def execute(self, context):
		ama = bpy.context.scene.objects.active
		for bone in ama.pose.bones:
		    if len(bone.constraints) >= 1:
		        for con in bone.constraints:
		            if con.type == "SPLINE_IK":
		                con.mute = True
		bpy.ops.object.editmode_toggle()
		bpy.ops.object.editmode_toggle()
		return {'FINISHED'}

#すべてのボーンのコンストレントのミュートを外す
class ViewBoneConstOperator(bpy.types.Operator):
    bl_idname = "object.viewboneconst"
    bl_label = "ViewSPIK"
    bl_options = {'REGISTER','UNDO'}
    bl_description = "全てのボーンコンストレイントに付いているミュートを外す"
    def execute(self, context):
        ama = bpy.context.scene.objects.active
        for bone in ama.pose.bones:
            if len(bone.constraints) >= 1:
                for con in bone.constraints:
                    con.mute = False
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}
#すべてのボーンのコンストレントのミュートをミュート
class HiddenBoneConstOperator(bpy.types.Operator):
    bl_idname = "object.hidenboneconst"
    bl_label = "ViewSPIK"
    bl_options = {'REGISTER','UNDO'}
    bl_description = "全てのボーンコンストレイントをミュート"
    def execute(self, context):
        ama = bpy.context.scene.objects.active
        for bone in ama.pose.bones:
            if len(bone.constraints) >= 1:
                for con in bone.constraints:
                    con.mute = True
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'} 
       
#おっぱい作成機能
class MakePIOperator(bpy.types.Operator):
    bl_idname = "object.make_pi"
    bl_label = "Make PI"
    #bl_options = {'REGISTER','UNDO'}
    bl_description = "選択中の頂点を膨らませる"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    
    my_float_emp_normal_value = bpy.props.FloatProperty(name="normal Value",default=0.0,step=0.01)
    my_float_normal_mix = bpy.props.FloatProperty(name="mix Value",default=1.0,max=1.0,min=0.0,step=0.01)
    my_float_normal_disp = bpy.props.FloatProperty(name="Disp Value",default=0.0,max=1.0,min=0.0,step=0.01)
    
    def execute(self, context):
        emp_normal_value = self.my_float_emp_normal_value
        normal_mix = self.my_float_normal_mix
        normal_disp = self.my_float_normal_disp
        
        obj = bpy.context.edit_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        
        obj.data.use_auto_smooth = True
        
        #select vertex list
        sel_verts = [v for v in bm.verts if v.select]
        
        # average normal and vector
        ave_normal = [0,0,0]
        ave_co = [0,0,0]
        for v in sel_verts :
            normal_local = v.normal.to_4d()
            normal_local.w = 0
            world_n = (obj.matrix_world * normal_local).to_3d()
            ave_normal[0] += world_n[0]
            ave_normal[1] += world_n[1]
            ave_normal[2] += world_n[2]
            
            world_v = obj.matrix_world * v.co
            ave_co[0] += world_v[0]
            ave_co[1] += world_v[1]
            ave_co[2] += world_v[2]
            
        for i,a in enumerate(ave_normal):
            ave_normal[i] /= len(sel_verts)
        for i,a in enumerate(ave_co):
            ave_co[i] /= len(sel_verts)
        
        #make average empty
        a = np.array(ave_co)# ベクトルaの生成
        b = np.array(ave_normal)# ベクトルbの生成
        c = np.array(obj.location)
        an_co = a +(b * emp_normal_value) # ベクトルa,b,cの和
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1, view_align=False, location=an_co, layers=obj.layers)
        empty_obj = bpy.context.active_object
        
        #make vertex group
        bpy.context.scene.objects.active = obj
        bpy.ops.object.vertex_group_add()
        vg = bpy.context.active_object.vertex_groups[-1]
        vg.name = "PI"
        bpy.ops.object.editmode_toggle()
        bpy.context.scene.tool_settings.vertex_group_weight = 1.0
        bpy.ops.object.vertex_group_assign()
        
        #make NormalEdit
        bpy.context.scene.objects.active = obj
        bpy.ops.object.modifier_add(type='NORMAL_EDIT')
        normal_edit = obj.modifiers[-1]
        normal_edit.mix_factor = normal_mix
        normal_edit.target = empty_obj
        normal_edit.vertex_group = vg.name
        
        #make disp
        if normal_disp > 0.0:
            bpy.ops.object.modifier_add(type='DISPLACE')
            disp = obj.modifiers[-1]
            bpy.context.object.modifiers[disp.name].direction = 'CUSTOM_NORMAL'
            bpy.context.object.modifiers[disp.name].vertex_group = vg.name
            bpy.context.object.modifiers[disp.name].strength = normal_disp
            bpy.ops.object.modifier_move_up(modifier=disp.name)
            
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
#グリースペンシルをラインに変換
class Gp2LineOperator(bpy.types.Operator):
    bl_idname = "object.gp2line"
    bl_label = "greasePencil -> Line"
    bl_options = {'REGISTER','UNDO'}
    bl_description = "選択中のグリースペンシルをカーブを使ったラインに変換(要:Simplify curvesアドオン)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    
    #設定
    my_thick = bpy.props.FloatProperty(name="line thick",default=0.02,min=0.00)
    my_irinuki = bpy.props.BoolProperty(default=True,name="IritoNuki")
    my_loop = bpy.props.BoolProperty(default=False,name="loop")
    my_strokeLink = bpy.props.BoolProperty(default=False,name="Stroke Link")
    my_pivot_center = bpy.props.BoolProperty(default=False,name="Pivot Center")
    my_simple_err = bpy.props.FloatProperty(name="Simple_err",default=0.015,description="値を上げるほどカーブがシンプルになる",min=0.0,step=1)
    my_digout = bpy.props.IntProperty(default=0,name="digout",min=0) #次数
    my_reso = bpy.props.IntProperty(default=3,name="resolusion",min=0) #カーブの解像度
    
    def execute(self, context):
        active_obj = bpy.context.scene.objects.active

        #グリースペンシルの頂点位置を取得
        #選択されたグリースペンシルがシーンかオブジェクトかを判断
        gp_source = bpy.context.scene.tool_settings.grease_pencil_source
        if gp_source == "SCENE":
            active_gp = bpy.context.scene.grease_pencil.layers.active
        else:
            active_gp = bpy.context.object.grease_pencil.layers.active

        if active_gp.active_frame != None:
            #空のカーブを作成
            bpy.ops.curve.primitive_nurbs_path_add()
            curve = bpy.context.active_object
            bpy.ops.object.location_clear()
            #頂点をすべて消す
            curve.data.splines.clear()
            bpy.context.scene.objects.active = active_obj
            #空のカーブにStrokeの位置を入れる    
            for i, stroke in enumerate(active_gp.active_frame.strokes):
                #新しいスプラインを追加
                if self.my_simple_err > 0.0:
                    newSpline = curve.data.splines.new(type='NURBS')
                else:
                    newSpline = curve.data.splines.new(type='POLY')
                newSpline.points.add(len(stroke.points)-1)
                for sPoint,newPoint in zip(stroke.points,newSpline.points):
                    newPoint.co = [sPoint.co[0],sPoint.co[1],sPoint.co[2],1.0]
            
            #カーブの各スプラインを接続する
            if self.my_strokeLink:
                #空のカーブを作成
                bpy.ops.curve.primitive_nurbs_path_add()
                curve3 = bpy.context.active_object
                bpy.ops.object.location_clear()
                #頂点をすべて消す
                curve3.data.splines.clear()
                #スプラインを一つ作る
                curvetype = curve.data.splines[0].type
                newSpline3 = curve3.data.splines.new(type=curvetype)
                #全頂点数を数える
                spline_len = 0
                for spline in curve.data.splines:
                    spline_len += len(spline.points)
                for i,c2spline in enumerate(curve.data.splines):
                    for j,c2point in enumerate(c2spline.points):
                        #最初の1個だけはaddせずもう出来ているものにコピー
                        if i==0 and j==0:
                            newSpline3.points[0].co = c2point.co
                        else:
                            newSpline3.points.add(1)
                            newSpline3.points[-1].co = c2point.co
                #本のカーブを消して3を入れる
                bpy.context.scene.objects.active = curve
                bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
                bpy.ops.object.delete()
                curve = curve3
                
            #原点を中心に移動
            bpy.context.scene.objects.active = curve
            bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
            if self.my_pivot_center == False:
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
            curve2 = curve
            if self.my_simple_err > 0.0:
                #Curvesをシンプル化
                bpy.context.scene.objects.active = curve
                bpy.ops.curve.simplify(output='NURBS', error=self.my_simple_err, degreeOut=self.my_digout, keepShort=True)
                curve2 = bpy.context.scene.objects.active
                #元のカーブを削除
                bpy.context.scene.objects.active = curve
                bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
                bpy.ops.object.delete()
                if self.my_strokeLink:
                    bpy.context.scene.objects.active = curve3
                    bpy.ops.object.select_pattern(pattern=curve3.name, case_sensitive=False, extend=False)
                    bpy.ops.object.delete()
            #カーブの設定を変更
            curve2.data.dimensions = '3D'
            curve2.data.fill_mode = 'FULL'
            curve2.data.bevel_depth = self.my_thick
            for spline in curve2.data.splines:
                spline.use_endpoint_u = True
                #ループ設定
                if self.my_loop:
                    spline.use_cyclic_u = True
            curve2.data.resolution_u = self.my_reso
            curve2.data.bevel_resolution = 1
            #irinuki
            if self.my_irinuki:
                for spline in curve2.data.splines:
                    if len(spline.points) > 2:
                        spline.points[0].radius = 0.0
                        spline.points[-1].radius = 0.0
            
            bpy.context.scene.objects.active = curve2
            bpy.ops.object.select_pattern(pattern=curve2.name, case_sensitive=False, extend=False)
            
            return {'FINISHED'} 
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
      
#グリースペンシルをメッシュに変換
class Gp2MeshOperator(bpy.types.Operator):
    bl_idname = "object.gp2mesh"
    bl_label = "greasePencil -> Mesh"
    bl_options = {'REGISTER','UNDO'}
    bl_description = "選択中のグリースペンシルをメッシュに変換(要:Simplify curvesアドオン)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    
    #設定
    my_addface = bpy.props.BoolProperty(default=True,description="面を貼る",name="Add Face")
    my_loop = bpy.props.BoolProperty(default=True,description="ループ",name="Loop")
    my_strokeLink = bpy.props.BoolProperty(default=False,description="すべての辺を繋いだメッシュにするか",name="Stroke Link")
    my_simple_err = bpy.props.FloatProperty(name="Simple_err",default=0.015,description="値を上げるほどカーブがシンプルになる",min=0.0,step=1)
    my_removedoubles = bpy.props.FloatProperty(name="remove doubles",default=0.0,description="値の距離以下の頂点は結合(0で無効)",min=0.0,step=1)
    my_digout = bpy.props.IntProperty(default=0,name="digout",min=0) #次数
    my_reso = bpy.props.IntProperty(default=3,name="resolusion",min=0) #カーブの解像度
    my_thickness = bpy.props.FloatProperty(name="thicknss",default=0.0,description="厚み付け",step=1)
    my_solioffset = bpy.props.FloatProperty(name="Soli Offset",default=0.0,description="厚み付けのオフセット",min=-1.0,max=1.0,step=1)
    my_isskin = bpy.props.BoolProperty(default=False,description="スキンモディファイアを設定",name="Add Skin")
    my_skinvalueX = bpy.props.FloatProperty(name="skin X",default=0.25,description="",min=0.0,step=1)
    my_skinvalueY = bpy.props.FloatProperty(name="skin Y",default=0.25,description="",min=0.0,step=1)
    
    def execute(self, context):
        #グリースペンシルをカーブに変換
        bpy.ops.object.gp2line(my_thick=0.0,my_irinuki=False,my_loop=self.my_loop,my_simple_err=self.my_simple_err,my_digout=self.my_digout,my_reso=self.my_reso,my_strokeLink=self.my_strokeLink)
        #メッシュに変換
        curve = bpy.context.scene.objects.active
        bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
        bpy.ops.object.convert(target='MESH')
        obj = bpy.context.scene.objects.active
        #頂点を結合
        if self.my_removedoubles > 0.0:
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=self.my_removedoubles,\
             use_unselected=False)
            bpy.ops.object.editmode_toggle()
        if self.my_addface:
            #編集モードに移行
            bpy.ops.object.editmode_toggle()
            #メッシュごとに全選択しメッシュを貼る
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.edge_face_add()
            bpy.ops.object.editmode_toggle()
        #厚み付け
        if self.my_thickness != 0.0:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.select_pattern(pattern=obj.name, case_sensitive=False, extend=False)
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            obj.modifiers[-1].thickness = self.my_thickness
            obj.modifiers[-1].offset = self.my_solioffset
        #スキンモディファイアを設定
        if self.my_isskin:
            bpy.ops.object.modifier_add(type='SKIN')
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.transform.skin_resize(value=(self.my_skinvalueX, self.my_skinvalueY, 0.25),\
             constraint_axis=(False, False, False), constraint_orientation='LOCAL',\
             mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
            bpy.ops.object.skin_root_mark()
            bpy.ops.object.editmode_toggle()

            
            

        return {'FINISHED'}
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
#グリースペンシルを髪の毛に変換
class Gp2AnimehairOperator(bpy.types.Operator):
    bl_idname = "object.gp2animehair"
    bl_label = "greasePencil -> AnimeHair"
    bl_options = {'REGISTER','UNDO'}
    bl_description = "選択中のグリースペンシルを髪の毛に変換(要:Simplify curvesアドオン)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    #グリースペンシル用の設定
    my_irinuki_2 = bpy.props.BoolProperty(default=False,name="IritoNuki")
    my_simple_err_2 = bpy.props.FloatProperty(name="Simple_err",default=0.015,description="値を上げるほどカーブがシンプルになる",min=0.0,step=1)
    my_digout_2 = bpy.props.IntProperty(default=0,name="digout",min=0) #次数
    my_reso_2 = bpy.props.IntProperty(default=3,name="resolusion",min=0) #カーブの解像度
    #アニメヘアー用の設定
    my_int_bevelType_2 = bpy.props.IntProperty(name="BevelType",min=0,max=13)
    my_int_taparType_2 = bpy.props.IntProperty(name="TaperType",min=0,max=7)
    my_float_x_2 = bpy.props.FloatProperty(name="X",default=1.0,min=0.0)
    my_float_y_2 = bpy.props.FloatProperty(name="Y",default=1.0,min=0.0)
    my_float_weight_2 = bpy.props.FloatProperty(name="SoftBody Goal",default=0.3,min=0.0,max=1.0)
    my_float_mass_2 = bpy.props.FloatProperty(name="SoftBody Mass",default=0.3,min=0.0,)
    my_float_goal_friction_2 = bpy.props.FloatProperty(name="SoftBody Friction",default=5.0,min=0.0)
    
    my_simple_flag = bpy.props.BoolProperty(name="simplify Curve")
    my_simple_err = bpy.props.FloatProperty(name="Simple_err",default=0.015,description="値を上げるほどカーブがシンプルになる",min=0.0,step=1)
    my_digout = bpy.props.IntProperty(default=0,name="digout",min=0) #次数
    my_reso = bpy.props.IntProperty(default=3,name="resolusion",min=0) #カーブの解像度
    
    
    def execute(self, context):
        bpy.ops.object.gp2line(my_irinuki=self.my_irinuki_2, my_simple_err=self.my_simple_err_2, my_digout=self.my_digout_2, my_reso=self.my_reso_2)
        bpy.ops.object.animehair(my_int_bevelType=self.my_int_bevelType_2, my_int_taparType=self.my_int_taparType_2,\
         my_float_x=self.my_float_x_2, my_float_y=self.my_float_y_2, my_float_weight=self.my_float_weight_2, my_float_mass=self.my_float_mass_2, my_float_goal_friction=self.my_float_goal_friction_2,\
         my_simple_flag=self.my_simple_flag, my_simple_err=self.my_simple_err, my_digout=self.my_digout, my_reso=self.my_reso)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
def menu_draw( self, context ): 
    self.layout.operator_context = 'INVOKE_REGION_WIN' 
    self.layout.operator( MakePIOperator.bl_idname, "make PI" ) 

#指定された角度以上に曲がっている辺にラインを描画
class Crease2LineOperator(bpy.types.Operator):
    bl_idname = "object.crease2line"
    bl_label = "Crease -> Line"
    bl_options = {'REGISTER','UNDO'}
    bl_description = "指定された角度以上の折り目をラインに変換(要:Simplify curvesアドオン)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    
    #my_defaultFlag = bpy.props.BoolProperty(default=False,name="Default Select edge",description="デフォルトで選択されている辺を使う")
    my_defaultFlag = False
    my_irinuki = bpy.props.BoolProperty(default=True,name="IritoNuki")
    my_sharp = bpy.props.FloatProperty(name="angle",default=60.0,description="折り目角度",min=0.0,max=180.0)
    my_simple_err = bpy.props.FloatProperty(name="Simple_err",default=0.0,description="値を上げるほどカーブがシンプルに(0で無効)",min=0.0,step=1)
    my_digout = bpy.props.IntProperty(default=0,name="digout",min=0) #次数
    my_thick=bpy.props.FloatProperty(name="line thick",default=0.005,min=0.00)
    my_reso = bpy.props.IntProperty(default=3,name="resolusion",min=0) #カーブの解像度
    
    def execute(self, context):
        #編集モードに以降
        bpy.ops.object.editmode_toggle()
        #デフォルトで選択されている辺を使うか使わないか
        if self.my_defaultFlag == False:
            #クリースを選択
            bpy.ops.mesh.select_all(action='DESELECT')
            sharp = radians(self.my_sharp)
            bpy.ops.mesh.edges_select_sharp(sharpness=sharp)
            
        #何も選択していない場合はエラーなので終わり
        try:
            bpy.ops.mesh.separate(type='SELECTED')
        except:
            bpy.ops.object.editmode_toggle()
            return {'FINISHED'}
            
        #選択した辺を複製
        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False),\
         "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1,\
          "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False,\
           "texture_space":False, "remove_on_cancel":False, "release_confirm":False})

        
        #面を選択している場合は除去
        bpy.ops.mesh.delete(type='ONLY_FACE')
        
        #Objectモードへ移行
        bpy.ops.object.editmode_toggle()
        #辺をカーブに変換
        curve = bpy.context.selected_objects[0]
        bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
        bpy.context.scene.objects.active = curve
        bpy.ops.object.convert(target='CURVE')

        if self.my_simple_err > 0.0:
            #Curvesをシンプル化
            bpy.context.scene.objects.active = curve
            bpy.ops.curve.simplify(output='NURBS', error=self.my_simple_err, degreeOut=self.my_digout, keepShort=True)
            #元のカーブを削除
            bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
            bpy.ops.object.delete()
        curve2 = bpy.context.scene.objects.active

        #シンプルカーブの設定を変更
        curve2.data.dimensions = '3D'
        curve2.data.fill_mode = 'FULL'
        curve2.data.bevel_depth = self.my_thick
        for spline in curve2.data.splines:
            spline.use_endpoint_u = True
        curve2.data.resolution_u = self.my_reso
        curve2.data.bevel_resolution = 1
        #irinuki
        if self.my_irinuki:
            for spline in curve2.data.splines:
                if len(spline.points) > 2:
                    spline.points[0].radius = 0.0
                    spline.points[-1].radius = 0.0
        #原点を中心に移動
        bpy.context.scene.objects.active = curve2
        bpy.ops.object.select_pattern(pattern=curve2.name, case_sensitive=False, extend=False)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        
        bpy.ops.object.select_pattern(pattern=curve2.name, case_sensitive=False, extend=False)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
#カメラティスを設定
class SetCamelattice(bpy.types.Operator):
    bl_idname = "object.setcamelattice"
    bl_label = "set Camelattice"
    bl_description = "カメラの面にラティスを設定"
    bl_options = {'REGISTER','UNDO'}
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    
    my_depth = bpy.props.FloatProperty(name="depth",default=1.0,description="ラティスとカメラの距離",min=0.0,\
        subtype='DISTANCE',unit='LENGTH')
    my_latu = bpy.props.IntProperty(name="Lattice_u",default=2,description="ラティスの縦",min=2)
    my_latv = bpy.props.IntProperty(name="Lattice_v",default=2,description="ラティスの横",min=2)
    my_latw = bpy.props.IntProperty(name="Lattice_v",default=1,description="ラティスの奥ゆき",min=1)
    my_setLattice = bpy.props.BoolProperty(name="set Lattice",default=False,\
        description="選択したオブジェクトにラティスを設定")
    
    def execute(self, context):
        #選択オブジェクトはラティスを設定するときに使う
        selectObjList = bpy.context.selected_objects
        #ラティスを作る
        bpy.ops.object.add(type='LATTICE', view_align=False, enter_editmode=False, location=(0, 0, 0),\
         layers=bpy.data.scenes['Scene'].layers)
        lat = bpy.context.active_object
        #ラティスの大きさの調整
        lat.data.points_u = self.my_latu
        lat.data.points_v = self.my_latv
        lat.data.points_w = self.my_latw
        lat.data.interpolation_type_u = 'KEY_BSPLINE'
        lat.data.interpolation_type_v = 'KEY_BSPLINE'
        lat.data.interpolation_type_w = 'KEY_BSPLINE'
        bpy.ops.object.editmode_toggle()
        bpy.ops.transform.resize( value=(0.5,0.5,0.5))
        bpy.ops.object.editmode_toggle()
        #ラティスをカメラの子にして位置・回転を合わせる
        lat.location = (0,0,-self.my_depth)
        camera = bpy.context.scene.camera
        lat.parent = camera
        lat.lock_rotation[0] = True
        lat.lock_rotation[1] = True
        lat.lock_rotation[2] = True
        lat.lock_location[0] = True
        lat.lock_location[1] = True 
        bpy.ops.object.shape_key_add(from_mix=False)
        bpy.ops.object.shape_key_add(from_mix=False)
        lat.data.shape_keys.key_blocks[1].value = 1.0
        #X,Y拡縮にドライバを設定
        driver = lat.driver_add('scale',1).driver
        driver.type = 'SCRIPTED'
        self.setdrivevalue( driver, lat) 
        driver.expression ="-depth*tan(camAngle/2)*bpy.context.scene.render.resolution_y * bpy.context.scene.render.pixel_aspect_y/(bpy.context.scene.render.resolution_x * bpy.context.scene.render.pixel_aspect_x)*2"
        driver = lat.driver_add('scale',0).driver
        driver.type= 'SCRIPTED'
        self.setdrivevalue( driver, lat)
        driver.expression ="-depth*tan(camAngle/2)*2"
        
        #オブジェクトを選択していた場合ラティスを設定
        objlistlotadd = [0,0,0]
        if len(selectObjList) > 0 and self.my_setLattice:
            for obj in selectObjList:
                print(obj)
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.scene.objects.active = obj
                bpy.ops.object.select_pattern(pattern=obj.name, case_sensitive=False, extend=False)
                bpy.ops.object.modifier_add(type='LATTICE')
                obj.modifiers[-1].object = lat

        bpy.context.scene.objects.active = lat
        bpy.ops.object.select_pattern(pattern=lat.name, case_sensitive=False, extend=False)
        return {'FINISHED'}
    
    def setdrivevalue(self, driver, lattice):
        angle = driver.variables.new()
        angle.name = 'camAngle'
        angle.type = 'SINGLE_PROP'
        angle.targets[0].id = lattice.parent
        angle.targets[0].data_path="data.angle"
        dep = driver.variables.new()
        dep.name = 'depth'
        dep.type = 'TRANSFORMS'
        dep.targets[0].id = lattice
        dep.targets[0].data_path = 'location'
        dep.targets[0].transform_type = 'LOC_Z'
        dep.targets[0].transform_space = 'LOCAL_SPACE'
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
#ランダム値が乗算された配列複製
class RandArray(bpy.types.Operator):
    bl_idname = "object.randarray"
    bl_label = "Rand Array"
    bl_description = "選択オブジェクトをランダムやグリースペンシルを使って配列複製"
    bl_options = {'REGISTER','UNDO'}
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    
    my_count = bpy.props.IntProperty(name="count",default=2,description="数",min=1)
    my_objlink = bpy.props.BoolProperty(name="Object Link",default=True)

    my_offset = bpy.props.FloatVectorProperty(name="offset Lot",default=[0,0,0])
    my_offsetrot = bpy.props.FloatVectorProperty(name="offset rot",default=[0,0,0])
    my_offsetsca = bpy.props.FloatVectorProperty(name="offset Scale",default=[0,0,0])
    
    my_rand = bpy.props.FloatVectorProperty(name="rand Lot",default=[0,0,0],min=0)
    my_randrot = bpy.props.FloatVectorProperty(name="rand rot",default=[0,0,0],min=0)
    my_randsca = bpy.props.FloatVectorProperty(name="rand Scale",default=[0,0,0],min=0)
    
    my_useGP = bpy.props.BoolProperty(name="use GP",default=False)
    my_onGP = bpy.props.BoolProperty(name="on GP",default=True)
    my_simple_err = bpy.props.FloatProperty(name="Simple_err",default=0.02,\
        description="値を上げるほどカーブがシンプルに(0で無効)",min=0.0,step=1)
    my_digout = bpy.props.IntProperty(default=3,name="digout",min=0\
        ,description="カーブ度合い")
    my_reso = bpy.props.IntProperty(default=1,name="resolusion",min=0\
        ,description="解像度")
    
    def execute(self, context):
        fobj = bpy.context.active_object
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.scene.objects.active = fobj
        bpy.ops.object.select_pattern(pattern=fobj.name, case_sensitive=False, extend=False)
        #選択されたオブジェクトをコピー
        if self.my_useGP:
            #カーブを作る
            bpy.ops.object.gp2line(my_irinuki=False, my_simple_err=self.my_simple_err,\
             my_digout=self.my_digout, my_reso=self.my_reso, my_thick=0)
            #カーブをメッシュに変換
            curve = bpy.context.scene.objects.active
            bpy.ops.object.select_pattern(pattern=curve.name, case_sensitive=False, extend=False)
            bpy.ops.object.convert(target='MESH',keep_original=False)
            curveobj = bpy.context.scene.objects.active
            #グリースペンシルを使用するかしないか
            if self.my_onGP:
                fobjLoc = copy.copy(fobj.location)
                fobj.location = [0,0,0]
                fobj.parent = curveobj
                curLoc = bpy.context.scene.cursor_location.copy()
                bpy.context.scene.cursor_location = fobjLoc
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                fobj.location = fobjLoc
                bpy.context.scene.cursor_location = curLoc
                
            else:
                curveobj.location = [0,0,0]
                curveobj.rotation_euler = [0,0,0]
                curveobj.scale = [1,1,1]
                foblot = copy.copy(fobj.location)
                fobj.parent = curveobj
                fobj.location = [0,0,0]
                curveobj.location = foblot
            #複製　頂点にチェック
            curveobj.dupli_type = "VERTS"
            
        else:
            #グリースペンシルを使用しない場合
            objList = []
            for c in range(self.my_count):
                bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":self.my_objlink, "mode":'TRANSLATION'},\
                 TRANSFORM_OT_translate={"value":(0,0,0),\
                  "constraint_axis":(False, False, False), "constraint_orientation":'LOCAL',\
                  "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH',\
                  "proportional_size":1, "snap":False, "snap_target":'CLOSEST',\
                  "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0),\
                  "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False,\
                  "release_confirm":False})
                active = bpy.context.active_object
                active.location = [0,0,0]
                active.rotation_euler = [0,0,0]
                active.scale = [1,1,1]
                active.parent = fobj
                objList.append(active)
            
            #選択されたオブジェクトの位置・回転・拡縮をランダム化
            for i,obj in enumerate(objList):
                random.uniform(0,self.my_rand[0])
                i += 1
                obj.location = [obj.location[0]+(self.my_offset[0]*i)+(random.uniform(-self.my_rand[0],self.my_rand[0]))\
                                ,obj.location[1]+(self.my_offset[1]*i)+(random.uniform(-self.my_rand[1],self.my_rand[1]))\
                                ,obj.location[2]+(self.my_offset[2]*i)+(random.uniform(-self.my_rand[2],self.my_rand[2]))]
                obj.rotation_euler =\
                    [obj.rotation_euler[0]+(self.my_offsetrot[0]*i)\
                    +random.uniform(-self.my_randrot[0],self.my_randrot[0]),\
                    obj.rotation_euler[1]+(self.my_offsetrot[1]*i)\
                    +random.uniform(-self.my_randrot[1],self.my_randrot[1]),\
                    obj.rotation_euler[2]+(self.my_offsetrot[2]*i)\
                    +random.uniform(-self.my_randrot[2],self.my_randrot[2])]
                obj.scale =\
                    [obj.scale[0]+(self.my_offsetsca[0]*i)\
                    +random.uniform(-self.my_randsca[0],self.my_randsca[0]),\
                    obj.scale[1]+(self.my_offsetsca[1]*i)\
                    +random.uniform(-self.my_randsca[1],self.my_randsca[1]),\
                    obj.scale[2]+(self.my_offsetsca[2]*i)\
                    +random.uniform(-self.my_randsca[2],self.my_randsca[2])]
                
        bpy.context.scene.objects.active = fobj
        bpy.ops.object.select_pattern(pattern=fobj.name, case_sensitive=False, extend=False)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
#Menu in tools region
class AnimeHairPanel(bpy.types.Panel):
    bl_label = "Amasawa Tools"
    bl_space_type = "VIEW_3D"
    bl_context = "objectmode"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
 
    def draw(self, context):
        hairCol = self.layout.column(align=True)
        hairCol.label(text="Create:")
        hairCol.operator("object.animehair")
        hairCol.operator("object.radiustoweight")
        hairCol.operator("object.crease2line")

        col = self.layout.column(align=True)
        col.label(text="Convert:")
        col.operator("object.hair2mesh")
        col.operator("object.curve2ama")
        col.operator("object.hair2meshfull")
        col.operator("object.curve2amafull")
        
        col = self.layout.column(align=True)
        col.label(text="GreasePencil:")
        col.operator("object.gp2line")
        col.operator("object.gp2mesh")
        col.operator("object.gp2animehair")

        col.label(text="all of Spline IK:")
        row = col.row(align=True)
        row.operator("object.viewspik",text="View")
        row.operator("object.hiddenspik",text="Mute")
        col.label(text="all of Bone constraints:")
        row = col.row(align=True)
        row.operator("object.viewboneconst",text="View")
        row.operator("object.hidenboneconst",text="Mute")
        
        latcol = self.layout.column(align=True)
        latcol.label(text="Object:")
        latcol.operator("object.setcamelattice")
        latcol.operator("object.randarray")
        
        
def register():# 登録
    bpy.utils.register_class(AnimeHairOperator)
    bpy.utils.register_class(Radius2weight)

    bpy.utils.register_class(Hair2MeshOperator)
    bpy.utils.register_class(Curve2AmaOperator)
    bpy.utils.register_class(Hair2MeshFullOperator)
    bpy.utils.register_class(Curve2AmaFullOperator)

    bpy.utils.register_class(AnimeHairPanel)
    bpy.utils.register_class(ViewSpIKOperator)
    bpy.utils.register_class(HiddenSpIKOperator)

    bpy.utils.register_class(ViewBoneConstOperator)
    bpy.utils.register_class(HiddenBoneConstOperator)
    
    bpy.utils.register_class( MakePIOperator )
    bpy.utils.register_class( Gp2LineOperator )
    bpy.utils.register_class( Gp2AnimehairOperator )
    bpy.utils.register_class( Crease2LineOperator )
    bpy.utils.register_class( Gp2MeshOperator )
    
    bpy.utils.register_class(SetCamelattice)
    bpy.utils.register_class(RandArray)
    
    bpy.types.VIEW3D_MT_edit_mesh_specials.append( menu_draw )
    
def unregister():# 解除
    bpy.utils.unregister_class(AnimeHairOperator)
    bpy.utils.unregister_class(Radius2weight)

    bpy.utils.unregister_class(Hair2MeshOperator)
    bpy.utils.unregister_class(Curve2AmaOperator)
    bpy.utils.unregister_class(Hair2MeshFullOperator)
    bpy.utils.unregister_class(Curve2AmaFullOperator)

    bpy.utils.unregister_class(AnimeHairPanel)
    bpy.utils.unregister_class(ViewSpIKOperator)
    bpy.utils.unregister_class(HiddenSpIKOperator)

    bpy.utils.unregister_class(ViewBoneConstOperator)
    bpy.utils.unregister_class(HiddenBoneConstOperator)
    
    bpy.utils.unregister_class( MakePIOperator )
    bpy.utils.unregister_class( Gp2LineOperator )
    bpy.utils.unregister_class( Gp2AnimehairOperator )
    bpy.utils.unregister_class( Crease2LineOperator )
    bpy.utils.unregister_class( Gp2MeshOperator )
    
    bpy.utils.unregister_class( SetCamelattice)
    bpy.utils.unregister_class( RandArray )
    
    bpy.types.VIEW3D_MT_edit_mesh_specials.remove( menu_draw )
  
#入力
#bpy.ops.object.animehair('INVOKE_DEFAULT')

if __name__ == "__main__":
    register()