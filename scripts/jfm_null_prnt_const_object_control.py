#jfm_null_prnt_const_object_control
#Author : Seth Meshko, 3danimationartist.com
#Creates a null above an object, then parent constrains the null to a second object, creates an attribute
#on the shape of the original object to control the blend of the parent constraint
#to use, select the target object then the object to be constrained


import maya.cmds as cmds

def snapToObj(target, objToSnap):
	tempPointConstraint = cmds.pointConstraint(target, objToSnap, maintainOffset = False)
	cmds.delete(tempPointConstraint)
	cmds.makeIdentity(objToSnap, apply = True, translate = True, rotate = True, scale = True)  #Freeze Transforms

listSelected = cmds.ls(selection = True)

if len(listSelected) == 2:
	targetObject = listSelected[0]
	constrainedObject = listSelected[1]

	cmds.addAttr(constrainedObject, longName = 'Foot_Follow', attributeType = 'float' , minValue = 0, maxValue = 1, defaultValue = 1, keyable = True)

	constrainedNull = cmds.group(empty = True, name = constrainedObject + 'Null')

	snapToObj(constrainedObject, constrainedNull)
	cmds.parent(constrainedObject, constrainedNull)
	parentConstraint = cmds.parentConstraint(targetObject, constrainedNull, maintainOffset = True)

	cmds.connectAttr(str(constrainedObject) + '.Foot_Follow', parentConstraint[0].encode('utf8') + '.' + targetObject + 'W0')
					

else:
	print('You have to select exactly two objects')
