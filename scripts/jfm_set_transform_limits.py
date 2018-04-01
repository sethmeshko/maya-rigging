#jfm_set_transform_limits
#created by Seth Meshko 12/21/2017
#www.3danimationartist.com
#Creates a gui interface that allows you to set min and max transform limits on a selection

import maya.cmds as cmds
import functools


windowID = 'jfm_setTransformLimits'

def applyLimits(applyLimits):
	
	translateXMaxLimit = cmds.checkBox(setLimitsTranslateXMax, editable = True, query = True, value = True)
	translateXMinLimit = cmds.checkBox(setLimitsTranslateXMin, editable = True, query = True, value = True)
	translateYMaxLimit = cmds.checkBox(setLimitsTranslateYMax, editable = True, query = True, value = True)
	translateYMinLimit = cmds.checkBox(setLimitsTranslateYMin, editable = True, query = True, value = True)
	translateZMaxLimit = cmds.checkBox(setLimitsTranslateZMax, editable = True, query = True, value = True)
	translateZMinLimit = cmds.checkBox(setLimitsTranslateZMin, editable = True, query = True, value = True)
	
	translateXMaxFieldValue = cmds.floatField(translateXMaxField, editable = True, query = True, value = True)
	translateXMinFieldValue = cmds.floatField(translateXMinField, editable = True, query = True, value = True)
	
	translateYMaxFieldValue = cmds.floatField(translateYMaxField, editable = True, query = True, value = True)
	translateYMinFieldValue = cmds.floatField(translateYMinField, editable = True, query = True, value = True)
	
	translateZMaxFieldValue = cmds.floatField(translateZMaxField, editable = True, query = True, value = True)
	translateZMinFieldValue = cmds.floatField(translateZMinField, editable = True, query = True, value = True)

	
	rotateXMaxLimit = cmds.checkBox(setLimitsRotateXMax, editable = True, query = True, value = True)
	rotateXMinLimit = cmds.checkBox(setLimitsRotateXMin, editable = True, query = True, value = True)
	rotateYMaxLimit = cmds.checkBox(setLimitsRotateYMax, editable = True, query = True, value = True)
	rotateYMinLimit = cmds.checkBox(setLimitsRotateYMin, editable = True, query = True, value = True)
	rotateZMaxLimit = cmds.checkBox(setLimitsRotateZMax, editable = True, query = True, value = True)
	rotateZMinLimit = cmds.checkBox(setLimitsRotateZMin, editable = True, query = True, value = True)
	
	rotateXMaxFieldValue = cmds.floatField(rotateXMaxField, editable = True, query = True, value = True)
	rotateXMinFieldValue = cmds.floatField(rotateXMinField, editable = True, query = True, value = True)
	
	rotateYMaxFieldValue = cmds.floatField(rotateYMaxField, editable = True, query = True, value = True)
	rotateYMinFieldValue = cmds.floatField(rotateYMinField, editable = True, query = True, value = True)
	
	rotateZMaxFieldValue = cmds.floatField(rotateZMaxField, editable = True, query = True, value = True)
	rotateZMinFieldValue = cmds.floatField(rotateZMinField, editable = True, query = True, value = True)


	scaleXMaxLimit = cmds.checkBox(setLimitsScaleXMax, editable = True, query = True, value = True)
	scaleXMinLimit = cmds.checkBox(setLimitsScaleXMin, editable = True, query = True, value = True)
	scaleYMaxLimit = cmds.checkBox(setLimitsScaleYMax, editable = True, query = True, value = True)
	scaleYMinLimit = cmds.checkBox(setLimitsScaleYMin, editable = True, query = True, value = True)
	scaleZMaxLimit = cmds.checkBox(setLimitsScaleZMax, editable = True, query = True, value = True)
	scaleZMinLimit = cmds.checkBox(setLimitsScaleZMin, editable = True, query = True, value = True)
	
	scaleXMaxFieldValue = cmds.floatField(scaleXMaxField, editable = True, query = True, value = True)
	scaleXMinFieldValue = cmds.floatField(scaleXMinField, editable = True, query = True, value = True)
	
	scaleYMaxFieldValue = cmds.floatField(scaleYMaxField, editable = True, query = True, value = True)
	scaleYMinFieldValue = cmds.floatField(scaleYMinField, editable = True, query = True, value = True)
	
	scaleZMaxFieldValue = cmds.floatField(scaleZMaxField, editable = True, query = True, value = True)
	scaleZMinFieldValue = cmds.floatField(scaleZMinField, editable = True, query = True, value = True)


	lockTranslateXValue = cmds.checkBox(lockTranslateX, editable = True, query = True, value = True)
	lockTranslateYValue = cmds.checkBox(lockTranslateY, editable = True, query = True, value = True)
	lockTranslateZValue = cmds.checkBox(lockTranslateZ, editable = True, query = True, value = True)

	lockRotateXValue = cmds.checkBox(lockRotateX, editable = True, query = True, value = True)
	lockRotateYValue = cmds.checkBox(lockRotateY, editable = True, query = True, value = True)
	lockRotateZValue = cmds.checkBox(lockRotateZ, editable = True, query = True, value = True)

	lockScaleXValue = cmds.checkBox(lockScaleX, editable = True, query = True, value = True)
	lockScaleYValue = cmds.checkBox(lockScaleY, editable = True, query = True, value = True)
	lockScaleZValue = cmds.checkBox(lockScaleZ, editable = True, query = True, value = True)


	selection = cmds.ls(selection = True)
	i = 0
	for eachObject in selection:
		transformPosition = cmds.xform(eachObject, query = True, translation = True)
		print('applyLimits(), the transformPositionValues for ' + str(eachObject) + ' are: ' + str(transformPosition))
		
		cmds.transformLimits(selection[i], enableTranslationX = [translateXMinLimit, translateXMaxLimit], tx=(transformPosition[0] + translateXMinFieldValue, transformPosition[0] + translateXMaxFieldValue))
		cmds.transformLimits(selection[i], enableTranslationY = [translateYMinLimit, translateYMaxLimit], ty=(transformPosition[1] + translateYMinFieldValue, transformPosition[1] + translateYMaxFieldValue))
		cmds.transformLimits(selection[i], enableTranslationZ = [translateZMinLimit, translateZMaxLimit], tz=(transformPosition[2] + translateZMinFieldValue, transformPosition[2] + translateZMaxFieldValue))

		cmds.transformLimits(selection[i], enableRotationX = [rotateXMinLimit, rotateXMaxLimit], rx =(rotateXMinFieldValue, rotateXMaxFieldValue))
		cmds.transformLimits(selection[i], enableRotationY = [rotateYMinLimit, rotateYMaxLimit], ry=(rotateYMinFieldValue, rotateYMaxFieldValue))
		cmds.transformLimits(selection[i], enableRotationZ = [rotateZMinLimit, rotateZMaxLimit], rz=(rotateZMinFieldValue, rotateZMaxFieldValue))

		cmds.transformLimits(selection[i], enableScaleX = [scaleXMinLimit, scaleXMaxLimit], sx =(scaleXMinFieldValue, scaleXMaxFieldValue))
		cmds.transformLimits(selection[i], enableScaleY = [scaleYMinLimit, scaleYMaxLimit], sy=(scaleYMinFieldValue, scaleYMaxFieldValue))
		cmds.transformLimits(selection[i], enableScaleZ = [scaleZMinLimit, scaleZMaxLimit], sz=(scaleZMinFieldValue, scaleZMaxFieldValue))
		
		print('the lockTranslateXValue is: ' + str(not lockTranslateXValue))

		cmds.setAttr(str(selection[i]) + '.translateX', lock = lockTranslateXValue, keyable = not lockTranslateXValue)
		cmds.setAttr(str(selection[i]) + '.translateY', lock = lockTranslateYValue, keyable = not lockTranslateYValue)
		cmds.setAttr(str(selection[i]) + '.translateZ', lock = lockTranslateZValue, keyable = not lockTranslateZValue)

		cmds.setAttr(str(selection[i]) + '.rotateX', lock = lockRotateXValue, keyable = not lockRotateXValue)
		cmds.setAttr(str(selection[i]) + '.rotateY', lock = lockRotateYValue, keyable = not lockRotateYValue)
		cmds.setAttr(str(selection[i]) + '.rotateZ', lock = lockRotateZValue, keyable = not lockRotateZValue)

		cmds.setAttr(str(selection[i]) + '.scaleX', lock = lockScaleXValue, keyable = not lockScaleXValue)
		cmds.setAttr(str(selection[i]) + '.scaleY', lock = lockScaleYValue, keyable = not lockScaleYValue)
		cmds.setAttr(str(selection[i]) + '.scaleZ', lock = lockScaleZValue, keyable = not lockScaleZValue)
		
		i = i + 1



#Start GUI

if cmds.window(windowID, exists=True):
	cmds.deleteUI(windowID)

cmds.window(windowID, title='Set min, max transform limits', sizeable=True, width = 550)

#Start of 1st frame
cmds.rowColumnLayout(numberOfColumns=1, columnWidth=[(1,500)], columnOffset=[(1,'both', 3)])
cmds.frameLayout(label='Translate Limits', collapsable=True)

cmds.text(label = 'Select the obect to set limits, dial in limits and hit apply')
#Start of 1st frame content
cmds.rowColumnLayout(numberOfColumns=7, columnWidth=[ (1,150), (2,50), (3,10), (4,130), (5,50), (6,10), (7,150)], columnOffset=[(1,'both', 3)])


#New Row

setLimitsTranslateXMin = cmds.checkBox(label = 'translateX min value', editable = True)

translateXMinField = cmds.floatField(editable = True)

cmds.separator(h=10, style='none')

setLimitsTranslateXMax = cmds.checkBox(label = 'translateX max value', editable = True)

translateXMaxField = cmds.floatField(editable = True)

cmds.separator(h=10, style='none')

lockTranslateX = cmds.checkBox(label = 'lock and hide', editable = True)


#New Row

setLimitsTranslateYMin = cmds.checkBox(label ='translateY min value', editable = True)

translateYMinField = cmds.floatField(editable = True)

cmds.separator(h=10, style='none')

setLimitsTranslateYMax = cmds.checkBox(label = 'translateY max value', editable = True)

translateYMaxField = cmds.floatField(editable = True)

cmds.separator(h=10, style='none')

lockTranslateY = cmds.checkBox(label = 'lock and hide', editable = True)


#New Row

setLimitsTranslateZMin = cmds.checkBox(label ='translateZ min value', editable = True)

translateZMinField = cmds.floatField(editable = True)

cmds.separator(h=10, style='none')

setLimitsTranslateZMax = cmds.checkBox(label = 'translateZ max value', editable = True)

translateZMaxField = cmds.floatField(editable = True)

cmds.separator(h=10, style='none')

lockTranslateZ = cmds.checkBox(label = 'lock and hide', editable = True)

cmds.setParent('..')
#End of 1st frame

#Start of 2nd frame
cmds.frameLayout(label='Rotate Limits', collapsable=True)
cmds.rowColumnLayout(numberOfColumns=7, columnWidth=[(1,150), (2,50), (3,10), (4,130), (5,50), (6,10), (7,150)], columnOffset=[(1,'both', 3)])

setLimitsRotateXMin = cmds.checkBox(label = 'RotateX min value', editable = True)

rotateXMinField = cmds.floatField(editable = True)

cmds.separator(h=10, style='none')

setLimitsRotateXMax = cmds.checkBox(label = 'RotateX max value', editable = True)

rotateXMaxField = cmds.floatField(editable = True)

cmds.separator(h=10, style='none')

lockRotateX = cmds.checkBox(label = 'lock and hide', editable = True)


#New Row

setLimitsRotateYMin = cmds.checkBox(label = 'RotateY min value', editable = True)

rotateYMinField = cmds.floatField(editable = True)

cmds.separator(h=10, style='none')

setLimitsRotateYMax = cmds.checkBox(label = 'RotateY max value', editable = True)

rotateYMaxField = cmds.floatField(editable = True)

cmds.separator(h=10, style='none')

lockRotateY = cmds.checkBox(label = 'lock and hide', editable = True)

#New Row

setLimitsRotateZMin = cmds.checkBox(label = 'RotateZ min value', editable = True)

rotateZMinField = cmds.floatField(editable = True)

cmds.separator(h=10, style='none')

setLimitsRotateZMax = cmds.checkBox(label = 'RotateZ max value', editable = True)

rotateZMaxField = cmds.floatField(editable = True)

cmds.separator(h=10, style='none')

lockRotateZ = cmds.checkBox(label = 'lock and hide', editable = True)

cmds.setParent('..')
#End of Second Frame

#Start of 3rd Frame
cmds.frameLayout(label='Scale Limits', collapsable=True)
cmds.rowColumnLayout(numberOfColumns=7, columnWidth=[(1,150), (2,50), (3,10), (4,130), (5,50), (6,10), (7,150)], columnOffset=[(1,'both', 3)])

setLimitsScaleXMin = cmds.checkBox(label = 'ScaleX min value', editable = True)

scaleXMinField = cmds.floatField(editable = True, value = 1)

cmds.separator(h=10, style='none')

setLimitsScaleXMax = cmds.checkBox(label = 'ScaleX max value', editable = True)

scaleXMaxField = cmds.floatField(editable = True, value = 1)

cmds.separator(h=10, style='none')

lockScaleX = cmds.checkBox(label = 'lock and hide', editable = True)

#New Row

setLimitsScaleYMin = cmds.checkBox(label = 'ScaleY min value', editable = True)

scaleYMinField = cmds.floatField(editable = True, value = 1)

cmds.separator(h=10, style='none')

setLimitsScaleYMax = cmds.checkBox(label = 'ScaleY max value', editable = True)

scaleYMaxField = cmds.floatField(editable = True, value = 1)

cmds.separator(h=10, style='none')

lockScaleY = cmds.checkBox(label = 'lock and hide', editable = True)

#New Row

setLimitsScaleZMin = cmds.checkBox(label = 'ScaleZ min value', editable = True)

scaleZMinField = cmds.floatField(editable = True, value = 1)

cmds.separator(h=10, style='none')

setLimitsScaleZMax = cmds.checkBox(label = 'ScaleZ max value', editable = True)


scaleZMaxField = cmds.floatField(editable = True, value = 1)

cmds.separator(h=10, style='none')

lockScaleZ = cmds.checkBox(label = 'lock and hide', editable = True)

cmds.setParent('..')
#End of Second Frame

#New Row

cmds.button(label = 'Apply', command = functools.partial(applyLimits))


cmds.showWindow()

