#jfm_select_all_skin_joints
#Author: Seth Meshko, 3danimationartist.com
#This script allows the user to select the root and 
import maya.cmds as cmds

selection = cmds.ls(selection = True)
childList = cmds.listRelatives(selection, allDescendents = True)
print('selectAllSkinJoints() all objects in childList are:' + str(childList))
justJointsList = []
justSkinJointsList = []
skinString = 'SKIN'

for eachObject in childList:
	cmds.rotate(0,0,0, eachObject, absolute = True)
	print('selectAllSkinJoints(), the current object is: ' + str(eachObject))
	objectType = cmds.objectType(eachObject)
	if(objectType == 'joint'):
		justJointsList.append(eachObject)
for eachObject in justJointsList:
	cmds.setAttr(str(eachObject) + '.segmentScaleCompensate', 0)
	if(skinString in eachObject):
		justSkinJointsList.append(eachObject)
print(justJointsList)
cmds.select(justSkinJointsList)
newSet = cmds.sets(name = 'skinJoints')