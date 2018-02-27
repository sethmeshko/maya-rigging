#jfm_elbow_setup
#Author: Seth Meshko, 3danimationartist.com
#This script creates a GUI that sets up an elbow control system for an HIK rig in maya.
#Designed to work in a larger setup that involves a second AUX rig that exists on top of an HIK rig
#Requires an object from a folder in the main my docs maya folder.  This folder is called assets and has a variety of shapes for rigging
#Be sure to download that assets foler and copy it to your maya folder in my docs 

import maya.cmds as cmds
import functools
import jfm_rigging_functions

global globalLoadedObjectList

def collectFields(*args):
	
	fullBodyIKControlString = cmds.textField(fullBodyIKControl, editable = True, query = True, text=True)
	auxElbowControlString = cmds.textField(auxElbowControl, editable = True, query = True, text=True)
	fkElbowControlString = cmds.textField(fkElbowControl, editable = True, query = True, text=True)
	auxWristControlString = cmds.textField(auxWristControl, editable = True, query = True, text=True)
	
	global globalLoadedObjectList
	globalLoadedObjectList = []#Clearing the globalLoadedObjectList before using it.

	testLoadedObject(fullBodyIKControlString, 'nurbsCurve', 'Full Body IK Control', 'fullBodyIKControl')
	testLoadedObject(auxElbowControlString, 'hikIKEffector', 'HIK Elbow Effector', 'auxElbowControl')
	testLoadedObject(fkElbowControlString, 'hikFKJoint', 'FK Elbow Handle', 'fkElbowControl')
	testLoadedObject(auxWristControlString, 'nurbsCurve', 'AUX Wrist Control', 'auxWristControl')

	print('the globalLoadedObjectList is: ' + str(globalLoadedObjectList))
	setupElbow(globalLoadedObjectList)


def cleanDroppedObject(cleanDroppedObject, activeField, textFieldString):	
	#if(activeField)
	
	listToClean = [activeField, textFieldString]
	
	i = 0
	for eachItem in listToClean:
		print('cleanDroppedObject(), The item is: ' + str(eachItem))
		hierarchyCount = eachItem.count('|')
		dividedString = eachItem.rsplit('|', hierarchyCount)
		print('the dividedString is: ' + str(dividedString))
		listToClean[i] = dividedString[hierarchyCount].encode('utf8')
		print('cleanDroppedObject(), the listToClean[i] is: ' + listToClean[i])
		i=i+1
	cmds.textField(listToClean[0], edit = True, text = listToClean[1])
	return listToClean[1]


def testLoadedObject(objectString, type, expectedInput, outputField):
	
	global globalLoadedObjectList

	if objectString == '':
		print('No ' + expectedInput + ' Loaded')
	else:
		print('the ' + expectedInput +  'is: ' + expectedInput)
		objectString = cleanDroppedObject('null', outputField, objectString)
		objectString = cmds.textField(outputField, editable = True, query = True, text=True)
		
		objectType = cmds.objectType(objectString)
		if objectType == 'joint' or objectType == 'hikIKEffector':
			print('testLoadedObject(), the object is special, a: ' + objectType)
		else:
			testItem = cmds.listRelatives(objectString)
			print('the testItem is: ' + str(testItem[0]))
			objectType = cmds.objectType(testItem[0])
		
		print ('testLoadedObject(), object type is: ' + str(objectType))

		if(objectType == type):
			print('testLoadedObject(), the selected object is: ' + str(objectString))
			globalLoadedObjectList.append(objectString.encode('utf8'))
		else:
			print('You need to load a ' + expectedInput)


def detectSideOfBody(objectToCalculate):
	transformPosition = cmds.xform(objectToCalculate, query = True, translation = True)
	
	'''The following decides whether the selected joint is on the right or left hand side of the body acording to its position in X
	Note! this assumes that the skeleton was setup with the standard facing down the Z axis with Y being world up and 
	X as the midline(saggital) axis.
	'''
	if(transformPosition[0] > 0):
		sideOfBody = 'Lft'
	else:
		sideOfBody = 'Rt'
	
	return sideOfBody 


#imports a shape from the assets file, you just need to know the name of the file to get
def importShape(nameOfFile):
	scriptsUserDirectory = cmds.internalVar(usd=True) #getting this version of maya scripts directory which is in the same directory as the assets folder
	pathToFile = '%s/%s' % (scriptsUserDirectory.rsplit('/', 3)[0], 'assets/' + nameOfFile + '.mb')#regroving that path to go to the assets folder
	cmds.file(pathToFile, i = True, groupReference = True, groupName = 'loadedShapeGroup')
	importedShape = cmds.listRelatives('loadedShapeGroup', allDescendents = True, type = 'shape')
	footControlShapeList = cmds.listRelatives(importedShape, parent = True)
	footControlShape = footControlShapeList[0]
	cmds.parent(footControlShape, world = True)
	cmds.delete('loadedShapeGroup')
	return footControlShape


def snapToObj(target, objToSnap):
	print('snapToObj(), the target is: ' + str(target) + ' the object being snapped is: ' + str(objToSnap) )
	tempPointConstraint = cmds.pointConstraint(target, objToSnap, maintainOffset = False)
	cmds.delete(tempPointConstraint)
	cmds.makeIdentity(objToSnap, apply = True, translate = True, rotate = True, scale = True)  #Freeze Transforms


#Use this if you want to setup a null above and follow attribute on the object you are constraining
def parentConstrainWithControl(targetObject, constrainedObject):
	cmds.addAttr(constrainedObject, longName = 'Rig_Follow', attributeType = 'float' , minValue = 0, maxValue = 1, defaultValue = 1, keyable = True)
	constrainedNull = cmds.group(empty = True, name = constrainedObject + 'Null')
	snapToObj(constrainedObject, constrainedNull)
	cmds.parent(constrainedObject, constrainedNull)
	parentConstraint = cmds.parentConstraint(targetObject, constrainedNull, maintainOffset = True)
	cmds.connectAttr(str(constrainedObject) + '.Rig_Follow', parentConstraint[0].encode('utf8') + '.' + str(targetObject) + 'W0')
	return constrainedNull

def pointConstrainWithControl(targetObject, constrainedObject):
	cmds.addAttr(constrainedObject, longName = 'Rig_Follow', attributeType = 'float' , minValue = 0, maxValue = 1, defaultValue = 1, keyable = True)
	constrainedNull = cmds.group(empty = True, name = constrainedObject + 'Null')
	snapToObj(constrainedObject, constrainedNull)
	cmds.parent(constrainedObject, constrainedNull)
	pointConstraint = cmds.pointConstraint(targetObject, constrainedNull, maintainOffset = True)
	cmds.connectAttr(str(constrainedObject) + '.Rig_Follow', pointConstraint[0].encode('utf8') + '.' + str(targetObject) + 'W0')
	return constrainedNull

def nullOverObject(object):
	null = cmds.group(empty=True)
	null = cmds.rename(null, object + 'Null')
	cmds.parent(object, null)
	return null

def setupElbow(listOfObjects):#listOfObjects are the strings loaded in the GUI
	fullBodyControlObject = listOfObjects[0]
	auxElbowControlObject = listOfObjects[1]
	fkElbowControlObject = listOfObjects[2]
	auxWristControlObject = listOfObjects[3]
	
	#this block imports the control shape for the elbow, names and positions it
	elbowControlShape = importShape('jfm_transformControl')
	cmds.rotate(90, 0, 0 , elbowControlShape)
	sideOfBody = detectSideOfBody(auxElbowControlObject)
	elbowControlShape = cmds.rename(elbowControlShape, 'AUX_' + sideOfBody + '_Elbow_Control')
	transformPosition = cmds.xform(auxElbowControlObject, query = True, translation = True)
	cmds.move(transformPosition[0], transformPosition[1], transformPosition[2], elbowControlShape)
	cmds.makeIdentity(elbowControlShape, apply = True, translate = True, rotate = True, scale = True)
	
	#this block sets up a null for the AUX IK Control to follow
	elbowLocatorNull = cmds.group(empty = True, name = 'AUX_' + sideOfBody + '_Elbow_Locator')
	cmds.move(transformPosition[0], transformPosition[1], transformPosition[2], elbowLocatorNull)
	cmds.parent(elbowLocatorNull, auxWristControlObject)
	
	#this block parents the AUX IK Control under a null and sets up the null to follow the wrist or the full body control
	hikElbowNull = nullOverObject(auxElbowControlObject)
	cmds.parent(hikElbowNull, elbowControlShape)
	elbowNull = parentConstrainWithControl(elbowLocatorNull, elbowControlShape)
	cmds.parent(elbowNull, fullBodyControlObject)

	#this block creates an attribute on the elbow to have the elbow control be active or not
	if cmds.objExists(elbowControlShape + '.hasEffect'):
		print('setupElbow(), the attribute .elbowRollMultiplier exists')
	else:
		cmds.addAttr(elbowControlShape, longName = 'hasEffect', attributeType = 'float' , minValue = 0, maxValue = 1, defaultValue = 1, keyable = True)
		cmds.connectAttr(str(elbowControlShape) + '.hasEffect', auxElbowControlObject.encode('utf8') + '.reachTranslation')
		cmds.connectAttr(str(elbowControlShape) + '.hasEffect', auxElbowControlObject.encode('utf8') + '.reachRotation')

	#this block creates a null above the FK elbow joint so that it can be rotated under this null or independently
	fkElbowNull = cmds.group(empty = True, world = True, name = elbowControlShape + '_Null')
	elbowParent = cmds.listRelatives(fkElbowControlObject, parent = True)
	cmds.parent(fkElbowNull, elbowParent)
	snapToObj(fkElbowControlObject, fkElbowNull)
	cmds.parent(fkElbowControlObject, fkElbowNull)

	#this block sets up an attribute for the hand control to change the roll of the forearm
	if cmds.objExists(auxWristControlObject + '.elbowRollMultiplier'):
		print('setupElbow(), the attribute .elbowRollMultiplier exists')
	else:
		print('elbowSetup(), the auxWristControlObject[0] is ' + str(auxWristControlObject))
		cmds.addAttr(auxWristControlObject, longName = 'elbowRollMultiplier', attributeType = 'float' , minValue = 0, maxValue = 1, defaultValue = 1, keyable = True)
	
	#this block creates a math node that will control the rotation of the elbow
	newRotateMultDivNode = cmds.shadingNode('multiplyDivide', asUtility = True, name = elbowControlShape + 'RotateMultDivNode')

	cmds.connectAttr(auxWristControlObject + '.elbowRollMultiplier', newRotateMultDivNode + '.input1X', force = True)
	cmds.connectAttr(auxWristControlObject + '.rotateX', newRotateMultDivNode + '.input2X', force = True)

	cmds.connectAttr(newRotateMultDivNode + '.outputX', fkElbowNull + '.rotateX', force = True)
	
	cmds.connectAttr(fullBodyControlObject + '.HIK_IK_Visibility', auxElbowControlObject + '.visibility', force = True)


windowID = 'jfm_elbow_rig_setup'


if cmds.window(windowID, exists=True):
	cmds.deleteUI(windowID)

cmds.window(windowID, title='Elbow_Setup', sizeable=True, width = 500)

#Start of 1st frame
cmds.rowColumnLayout(numberOfColumns=1, columnWidth=[(1,500)], columnOffset=[(1,'both', 3)])

cmds.text(label = 'load elbow control objects')
#Start of 1st frame content
cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1,200), (2,300)], columnOffset=[(1,'both', 3)])

cmds.text(label = 'MMD the Full Body IK Control:', align = 'right')
fullBodyIKControl = cmds.textField('fullBodyIKControl', enterCommand = functools.partial(cleanDroppedObject, 'fullBodyIKCntrl', 'fullBodyIKControl'))
cmds.text(label = 'MMD the AUX HIK Elbow Control:', align = 'right')
auxElbowControl = cmds.textField('auxElbowControl', enterCommand = functools.partial(cleanDroppedObject, 'auxElbowControl', 'auxElbowControl'))
cmds.text(label = 'MMD the FK Elbow Control:', align = 'right')
fkElbowControl = cmds.textField('fkElbowControl', enterCommand = functools.partial(cleanDroppedObject, 'fkElbowControl', 'fkElbowControl'))
cmds.text(label = 'MMD the AUX Wrist Control:', align = 'right')
auxWristControl = cmds.textField('auxWristControl', enterCommand = functools.partial(cleanDroppedObject, 'auxWristControl', 'auxWristControl'))


#horizontal spacer row
cmds.separator(h=10, style='none')
cmds.separator(h=10, style='none')
cmds.separator(h=10, style='none')
cmds.separator(h=10, style='none')
cmds.separator(h=10, style='none')
cmds.setParent('..')


cmds.rowColumnLayout(numberOfColumns=5, columnWidth=[(1,75), (2,25), (3,75), (4,25), (5,200)], columnOffset=[(1,'both', 3)])

cmds.separator(h=10, style='none')
cmds.separator(h=10, style='none')
cmds.separator(h=10, style='none')
cmds.separator(h=10, style='none')
cmds.button(label = 'Apply', command = collectFields)


cmds.showWindow()
