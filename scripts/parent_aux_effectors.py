#parent_aux_effectors.py
#Author: Seth Meshko, 3danimationartist.com
#This script will take a child, parent selection and then parent the child under the parent with a null buffer
#Note, this leaves the buffer null's transformations relative to world zero (important for AUX effector in HIK system)
import maya.cmds as cmds

selectionList = cmds.ls( selection=True ) #create a list of object from your current selection
effectorObject= selectionList[0]
controlObject = selectionList[1]

if cmds.objExists('AUX_FullBodyIKControl'):
	fullBodyIkControl = 'AUX_FullBodyIKControl'
	print(str(fullBodyIkControl) + ' found')
else:
	print('AUX_FullBodyIKControl not found,  There must be an object named exactly AUX_FullBodyIKControl in the scene')

if cmds.objExists(controlObject + '.hasEffect'):
	print('has effect found, deleting')
	cmds.deleteAttr(controlObject + '.hasEffect')

cmds.addAttr(controlObject, longName = 'hasEffect', attributeType = 'float' , minValue = 0, maxValue = 1, defaultValue = 1, keyable = True)

newHasEffectMultDivNode = cmds.shadingNode('multiplyDivide', asUtility = True, name = controlObject + 'HasEffectMultDivNode')
cmds.connectAttr(fullBodyIkControl + '.AUX_Follow', newHasEffectMultDivNode + '.input1X',  force = True)
cmds.connectAttr(controlObject + '.hasEffect', newHasEffectMultDivNode + '.input2X',  force = True)

cmds.connectAttr(newHasEffectMultDivNode + '.outputX', effectorObject + '.reachRotation', force = True)
cmds.connectAttr(newHasEffectMultDivNode + '.outputX', effectorObject + '.reachTranslation', force = True)

cmds.connectAttr(fullBodyIkControl + '.AUX_IK_Visibility', effectorObject + '.visibility')  

null = cmds.group(empty=True)
null = cmds.rename(null, effectorObject + 'Null')  #appends the name of the object with "Null"
cmds.parent(null, controlObject)
cmds.parent(effectorObject, null)