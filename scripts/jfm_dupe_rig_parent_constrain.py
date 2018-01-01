#jfm_dupe_rig_parent_constrain
#Created by: Seth Meshko, 3danimationartist.com
#12/17/17

'''
This script opens a gui window that will allow you to select a skeleton then with a button push automatically 
duplicates your skinned rig, renames each joint, removes all shapes, transforms and effectors and 
creates the parent constraints for each joint and establishes a common control to turn the parent 
constraint network on and off with a single attribute on the skin rig root.
NOTE!: This script will fail if there are any objects in your scene that are named the same as any object
in your new rig.  Although this is fairly unlikely it bears mentioning.
ANOTHER NOTE!: If you are using this after having already run jfm_HandSetup.py then you don't want this script
you want jfm_dupeRigPrntConstWithHandSetup
'''

import maya.cmds as cmds
import functools

windowID = 'jfm_dupeRigParentConstrain'

global globalRigToDupe
global globalTargetRig
global globalSideOfBody

def detectSideOfBody(jointToCalculate):
	transformPosition = cmds.xform(jointToCalculate, query = True, translation = True)
	
	'''The following decides whether the selected joint is on the right or left hand side of the body acording to its position in X
	Note! this assumes that the skeleton was setup with the standard facing down the Z axis with Y being world up and 
	X as the midline(saggital) axis.
	'''
	global globalSideOfBody
	if(transformPosition[0] > 0):
		sideOfBody = 'Lft'
	else:
		sideOfBody = 'Rt'
	
	return sideOfBody 

def detectExtantHandRig():
	extantHandRigList = []
	if cmds.objExists('RIG_Right_HandRoot'):
		extantHandRigList.append('TARGET_Left_HandRoot')
	if cmds.objExists('RIG_Right_HandRoot'):
		extantHandRigList.append('RIG_Right_HandRoot')	
	if(len(extantHandRigList) > 0):
		for eachJoint in extantHandRigList:
			sideOfBody = detectSideOfBody(eachJoint)
			deleteFingers = cmds.listRelatives(eachJoint, children = True)
			cmds.delete(deleteFingers)
			cmds.rename(eachJoint, 'TARGET_' + sideOfBody + '_' + 'Wrist')

def loadSelected(loadSelected):
	rigToDupe = cmds.ls(selection = True)
	newSelection = cmds.textField('selectedObjectField', edit = True, text = rigToDupe[0].encode('utf8'))#This changes the text field
	print('loadSelected, the globalRigToDupe is: ' + str(rigToDupe)) 
	global globalRigToDupe
	globalRigToDupe = rigToDupe #This assigns the joint to be duplicated

def renameObject(text, dic):
	for i, j in dic.iteritems():
		text = text.replace(i, j)
	return text 

def deleteFilteredObjects(rootJoint, typeOfObject):
	listToPrune = cmds.listRelatives(rootJoint, allDescendents = True)
	for eachObject in listToPrune:
		objectType = cmds.objectType(eachObject)
		if(objectType == typeOfObject):
			cmds.delete(eachObject)

def dupeRig(dupeRig, pNameSearchField, pNameReplaceField):

	#The order in which these are assigned matters more than the first arguement
	searchForField = cmds.textField(nameSearchField, query=True, text=True)
	replaceWithField = cmds.textField(nameReplaceField, query=True, text=True)

	print('dupeRig(), the searchForField is: ' + searchForField)
	print('dupeRig(), the replaceWithField is: ' + replaceWithField)

	objectType = cmds.objectType(globalRigToDupe)

	if (objectType != 'joint'):
		print('You must load a joint to duplicate')
	elif (objectType == 'joint'):

		originalRootName = globalRigToDupe[0]  #Storing the original name of root
		print('dupeRig(), the originalRootName is : ' + str(originalRootName))
		newObject = cmds.duplicate(globalRigToDupe[0], n='temp', rc=True) #the objects have to be renamed because there is nothing you can do with them until they have a different name from their originals
		cmds.parent(newObject[0], world = True)
		print('dupeRig(), the newObject is : ' + str(newObject))
		reps = {searchForField: replaceWithField, 'SknNoWeight':'TARGET', '1': ''}
		nameForRootObject = renameObject(originalRootName, reps) #replacing the prefix
		print('dupeRig(), the newObject[0] is : ' + str(newObject[0]))
		duplicatedJoint = cmds.rename(newObject[0], nameForRootObject) #Changing the name back to something that makes sense
		print('dupeRig(), the duplicatedJoint is : ' + str(duplicatedJoint))
		global globalTargetRig
		globalTargetRig = duplicatedJoint
		newSelection = cmds.listRelatives(duplicatedJoint, allDescendents=True)#creating a new list from the childern of the duplicated object, note we had to use the new name for the root object
		print('dupeRig(), the newSelection is: ' + str(newSelection))

		#renaming the childen
		i=0
		originalNameList = cmds.listRelatives(globalRigToDupe[0], allDescendents = True)
		print('dupeRig(), the originalNameList is: ' + str(originalNameList))
		reps = {searchForField: replaceWithField, 'SknNoWeight': 'TARGET', 'SknGeo' : 'TARGET', 'Hair':'TARGET_Hair'}
		for eachObject in newSelection:
			objectName = originalNameList[i]
			# bind the returned text of the method
			# to a variable and print it
			newNameA = renameObject(objectName, reps)
			#print newNameAs
			print('dupeRig(), the object to rename is: ' + str(eachObject))
			newName = cmds.rename(eachObject, newNameA)
			i= i+1

	#parent constraining original rig to duplicated rig	
	parentConstrainedRigList = cmds.listRelatives(globalRigToDupe[0], allDescendents = True, type = 'joint')
	print('dupRig(), globalTargetRig is: ' + str(globalTargetRig)) #at this point globalTargetRig is the root of the target rig
	targetRigList = cmds.listRelatives(globalTargetRig, allDescendents = True, type = 'joint')
	parentConstrainedRigList.insert(0, globalRigToDupe[0])
	targetRigList.insert(0, globalTargetRig)
	print('dupeRig(), the parentConstrainedRigList[0] is: ' + str(parentConstrainedRigList[0]))
	print('dupeRig(), the targetRigList[0] is: ' + str(targetRigList[0]))
	#if cmds.attributeQuery(parentConstrainedRigList[0], node = 'RigFollow'):
	if (cmds.objExists(parentConstrainedRigList[0] + '.RigFollow')):
		print('dupeRig(), attribute RigFollow found')
		#cmds.select(parentConstrainedRigList[0])
		cmds.deleteAttr(parentConstrainedRigList[0], attribute = 'RigFollow')
	cmds.addAttr(parentConstrainedRigList[0], attributeType = 'float', longName = 'RigFollow', hasMinValue = True, minValue = 0, maxValue = 1, defaultValue = 1, keyable = True)

	i=0
	for eachJoint in parentConstrainedRigList:
		print('dupeRig(), the parentConstrainedRigList[i] is: ' + str(parentConstrainedRigList[i]))
		print('dupeRig(), the targetRigList[i] is: ' + str(targetRigList[i]))
		newParentConstraint = cmds.parentConstraint(targetRigList[i], parentConstrainedRigList[i])
		reps = {'|':''}
		targetRigString = renameObject(targetRigList[i], reps)
		cmds.connectAttr(str(parentConstrainedRigList[0])  + '.RigFollow', newParentConstraint[0].encode('utf8') + '.' + targetRigString + 'W0', force = True)
		i=i+1
	
		
	#This is all cleanup for the rig skeleton.  It's just deleting all of the unused artifacts from the skin joint skeleton
	shapeSelection = cmds.listRelatives(globalTargetRig, allDescendents = True, type = 'shape' ) #creating a list to select any unwanted shapes in the hierarchy
	#The reason why this is done as a loop is because if the throws an error you will know which shape to deal with
	for eachObject in shapeSelection:
		shapeTransform = cmds.listRelatives(eachObject, type = 'transform', parent = True ); #selecting the transforms of the shape nodes
		cmds.delete(shapeTransform)

	typeToPrune = 'transform'
	deleteFilteredObjects(globalTargetRig, typeToPrune)
	typeToPrune = 'ikEffector'
	deleteFilteredObjects(globalTargetRig, typeToPrune)


	
#Start GUI

if cmds.window(windowID, exists=True):
	cmds.deleteUI(windowID)

cmds.window(windowID, title='Dupe Rig, Parent Constrain Hierarchy', sizeable=False, resizeToFitChildren=True)

#Start of 1st frame
cmds.frameLayout(label='Duplicate and Rename', collapsable=True)

cmds.text(label = 'Select the joint root to duplicate and enter search and replace names')
#Start of 1st frame content
cmds.rowColumnLayout(numberOfColumns=5, columnWidth=[(1,150), (2,150), (3,10), (4,100), (5,150)], columnOffset=[(1,'right', 3)])

#New Row
cmds.text(label='Joint root to duplicate:')

jointNameField = cmds.textField('selectedObjectField')

cmds.separator(h=10, style='none')

cmds.separator(h=10, style='none')

cmds.button(label='Select', command=(loadSelected)) #functools.partial


#New Row

cmds.text(label='Name Search:')

nameSearchField = cmds.textField(text='SKIN')

cmds.separator(h=10, style='none')

cmds.text(label='Name Replace:')

nameReplaceField = cmds.textField(text='TARGET')

#New Row

cmds.separator (h=10, style='none')
cmds.separator (h=10, style='none')
cmds.separator (h=10, style='none')
cmds.separator (h=10, style='none')
cmds.separator (h=10, style='none')

#New Row

cmds.separator (h=10, style='none')
cmds.separator (h=10, style='none')
cmds.separator (h=10, style='none')
cmds.separator (h=10, style='none')
cmds.button(label='Duplicate', command=functools.partial(dupeRig, nameSearchField, nameReplaceField)) #

cmds.setParent('..')
#End of 1st frame

cmds.showWindow()