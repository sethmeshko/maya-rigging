#jfm_hand_setup 
#Released 12/11/2017
#Updated 02/28/2018
#Created by Seth Meshko, Digital Artist, www.3danimationartist.com
#Creates a window that automates a number of tasks for rigging a humanoid character hand
#Requires objects from a folder called assets that must reside in the mydocs maya folder, download and copy that file.  It's available
#in the github directory
import maya.cmds as cmds

globalDuplicatedHandList = [] #This is a variable that will be used to store the joint hierarchies of the duplicated hands 
globalSideOfBody = '' #This is a variable that will be used to store the side of the body that we are on.
globalControlShapeList = [] #This is a variable that will store a list of the duplicated hand joint hierarchies.  The resulting order should be: rig, ik, control, driven, skin
globalControlBoxShape = []	#This is a variable that will store a shape that contains the driven controls for the hand

def reorderFingers(selectedJoint):
	'''
	this insures that the fingers are correctly ordered from thumb to pinky
	'''
	#Getting the value of the selected joint's transforms
	transformPosition = cmds.xform(selectedJoint, query = True, translation = True)
	
	'''The following decides whether the selected joint is on the right or left hand side of the body acording to its position in X
	Note! this assumes that the skeleton was setup with the standard facing down the Z axis with Y being world up and 
	X as the midline(saggital) axis.
	'''
	global globalSideOfBody
	if(transformPosition[0] > 0):
		sideOfBody = 'Left'
	else:
		sideOfBody = 'Right'
	
	globalSideOfBody = sideOfBody 

	fingerRootList = cmds.listRelatives(selectedJoint, children = True)

	#Getting the transform positions of the root finger joints
	zTransformPositionList = []
	xTransformPositionList = []
	for eachJoint in fingerRootList:
		zTransformPosition = cmds.xform(eachJoint, query = True, translation = True)
		xTransformPostion = cmds.xform(eachJoint, query = True, translation = True)
		zTransformPositionList.append(zTransformPosition[2]) #isolating Z
		xTransformPositionList.append(zTransformPosition[0]) #isolating X
	
	if sideOfBody == 'Left':
		furthestJointInZ = zTransformPositionList.index(max(zTransformPositionList))  #Getting the index of the joint that has the greatest value in transformZ
		closestJointInX = xTransformPositionList.index(min(xTransformPositionList))   #Getting the index of the joint that has the smallest value in transformX

	elif sideOfBody =='Right':
		furthestJointInZ = zTransformPositionList.index(min(zTransformPositionList))  #Getting the index of the joint that has the smallest value in transformZ
		closestJointInX = xTransformPositionList.index(max(xTransformPositionList))  #Getting the index of the joint that has the greatest value in transformZ

	#this block removes the thumb from the hand's list and drops it back in at the top of the list
	idThumb = fingerRootList[closestJointInX] 
	fingerRootList.remove(idThumb)
	fingerRootList.insert(0, idThumb)


	indexOfFurthestJointInZ = 0
	del fingerRootList[indexOfFurthestJointInZ]#removing the named finger from the fingerRootList (which is being itterated through in this while loop)
	#the following if statement gets the index of the joint with the largest transformZ value (or smallest depending on the side of body)
	if (globalSideOfBody == 'Left'):
		indexOfFurthestJointInZ = zTransformPositionList.index(max(zTransformPositionList)) #This has to change for left or right
	else:
		indexOfFurthestJointInZ = zTransformPositionList.index(min(zTransformPositionList)) #This has to change for left or right
	

def selectPrefix(prefixNumber, prefixList):
	for eachEntry, eachOutput in prefixList.iteritems():
		if (eachEntry == prefixNumber):
			prefixName = eachOutput
			return prefixName

def renameObject(text, dic):
	for i, j in dic.iteritems():
		text = text.replace(i, j)
	return text 

def transformObjects(objectToTransform, transformValues):
	translateValues = transformValues[0]
	scaleValues = transformValues[2]

	cmds.move(translateValues[0], translateValues[1], translateValues[2], objectToTransform, relative = True)
	cmds.scale(scaleValues[0],scaleValues[1], scaleValues[2], objectToTransform)
	cmds.makeIdentity(objectToTransform, apply = True, translate = True, rotate = True, scale = True)  #Freeze Transform

def snapToObj(target, objToSnap):
	tempPointConstraint = cmds.pointConstraint(target, objToSnap, maintainOffset = False)
	cmds.delete(tempPointConstraint)
	cmds.makeIdentity(objToSnap, apply = True, translate = True, rotate = True, scale = True)  #Freeze Transforms

def snapToObjSkip(target, objToSnap, skipAxis):
	tempPointConstraint = cmds.pointConstraint(target, objToSnap, maintainOffset = False, skip = skipAxis)
	cmds.delete(tempPointConstraint)
	cmds.makeIdentity(objToSnap, apply = True, translate = True)  #Freeze Transforms

def snapToObjInY(target, objToSnap):
	tempPointConstraint = cmds.pointConstraint(target, objToSnap, maintainOffset = False, skip = ["x","z"])
	cmds.delete(tempPointConstraint)
	cmds.makeIdentity(objToSnap, apply = True, translate = True)  #Freeze Transforms

def reorderJoints(jointRoot):#This seems to be no longer needed.  Delete if confirmed.
	#reordering the firstKnuckle list so that the controls are named in order
	firstKnuckleList = cmds.listRelatives(drivenRootJoint, children = True)  
	#print('reorderJoints(), the firstKnuckleList order before reorder is: ' + str(firstKnuckleList))
	thumbjoint = firstKnuckleList[-1]
	del(firstKnuckleList[-1])
	firstKnuckleList.insert(0, thumbjoint)
	#firstKnuckleList = list(reversed(firstKnuckleList))	
	#print('reorderJoints(), the firstKnuckleList order after reorder is: ' + str(firstKnuckleList))
	return(firstKnuckleList)

def duplicateJoints(jointToDuplicate):
	'''
	We need a total of 5 duplicate joint hierarchies.  The first is the "Skin" joints which are already extant.  Then seconde we need the "Rig" 
	joints which will be setup to follow either the FK or IK rigs with a toggle.  Then third and forth we need the two joint hierarchies that 
	will support "FK" and "Driven" movement (these work in coordination with eachother and ultimately are part of the same immediate hierarchy).
	Finally we will need the "IK" joints.
	'''
	
	reorderFingers(jointToDuplicate)

	#The following block creates a duplicate of the skin hand joint and cleans it before processing the other duplicates
	dirtyJointHierarchy = cmds.duplicate(jointToDuplicate, n='jfm_tempRootJointClean', rc=True) #the objects have to be renamed because there is nothing you can do with them until they have a different name from their originals
	dirtyJointRoot = dirtyJointHierarchy[0]
	print('duplicateJoints(), the dirtyJointHierarchy is: ' + str(dirtyJointHierarchy))
	shapeSelection = cmds.listRelatives(dirtyJointHierarchy, allDescendents = True, type = 'shape' ) #creating a list to select any unwanted shapes in the hierarchy
	shapeTransformSelection = cmds.listRelatives(shapeSelection, allDescendents = True, type = 'transform', parent = True); #selecting the transforms of the shape nodes
	cmds.delete(shapeTransformSelection) #deleting the unwanted shapes
	print('duplicateJoints(), the dirtyJointHierarchy list is: ' + str(dirtyJointHierarchy))
	cleanJointHierarchy = cmds.listRelatives(dirtyJointRoot, allDescendents = True)
	cleanJointHierarchy.insert(0, dirtyJointRoot)
	print('duplicateJoints(), the cleanJointHierarchy is: ' + str(cleanJointHierarchy))
	for eachObject in cleanJointHierarchy:
		print('duplicateJoints(), the object is: ' + str(eachObject))
		objectType = cmds.objectType(eachObject)
		print('duplicateJoints(), the object type is: ' + str(objectType))
		if(objectType == 'parentConstraint'):# if your skeleton has more junk in it, you can remove it by adding more objectTypes
			cmds.delete(eachObject)
	
	cleanJointRoot = cleanJointHierarchy[0]
	newObjectList = []
	jointDupeNumTimes = 4
	newJointList = []
	while(jointDupeNumTimes > 0):
		newObject = cmds.duplicate(cleanJointRoot, n='jfm_tempRootJoint', rc=True) #the objects have to be renamed because there is nothing you can do with them until they have a different name from their originals
		newObject = newObject[0]
		cmds.parent(newObject, world = True)
		newObjectList.append(newObject) #list of the roots of each duplicated hand
		
		jointDupeNumTimes = jointDupeNumTimes - 1
		
		cmds.select(jointToDuplicate)
	
	cmds.delete(cleanJointRoot)
	newObjectList.append(jointToDuplicate)
	prefixNumber = 0
	duplicatedHandList = []
	for eachJointRoot in newObjectList:# at this point newObjectList should be loaded full of each duplicate hand root, this will iterate over that list to rename the joints in each duplication
		selectedJoint = eachJointRoot
		prefixNumber = prefixNumber + 1
		renameHand(prefixNumber, selectedJoint, duplicatedHandList)
		
	
def renameHand(prefixNumber, jointToDuplicate, duplicatedHandList):
	'''
	This function is itterated through to rename each duplicate hand's joints appropriately
	'''
	prefixList = {5 : 'SKIN', 4 : 'DRIVEN', 3 : 'CONTROL', 2 : 'IK', 1 : 'RIG' }  

	#This composes the name for the selected joint chain
	prefixName = selectPrefix(prefixNumber, prefixList)#this takes the prefix number and the prefixList dictionary and compares until it returns the appropriate prefix
	rootJoint = cmds.rename(jointToDuplicate, prefixName + '_' + globalSideOfBody + '_' + 'HandRoot' )#this does the actual renaming of the root joints but also stores the joint after renaming it.

	#This adds joints to the global variable lists for the duplicated hand joint hierarchies. These will be used in other scripts for further setup.
	global globalDuplicatedHandList
	globalDuplicatedHandList.append(rootJoint)

	fingerRootList = cmds.listRelatives(rootJoint, children = True, type = 'joint') # this creates a list of the fingers under the hand's root
	print('renameHand(), the fingerRootList is: ' + str(fingerRootList) )
	#Renaming all of the fingers.  This for loop functions by itterating through each of the fingerRootList joints, renaming
	#the joint chain and then removing that joint chain from the finger root list and then proceeding to the next joint
	i = 0
	fingerSequence = 1#this will be the number of the finger, i.e. thumb = 1, index = 2 and so on
	for eachJoint in fingerRootList:
		fingerRoot = fingerRootList[i]#setting the selected joint to the root of the finger with the largest transformZ value 
		print('renameHand(), the fingerRoot is: ' + str(fingerRoot))
		fingerHierarchy = cmds.listRelatives(fingerRoot, allDescendents = True, type = 'joint')#getting the child joints of the finger
		fingerHierarchy.append(fingerRoot)#adding the root joint into the finger hierarchy
		jointNumber = 1 #this will be the number of the joint number, i.e. first knuckle = 1, second knuckle = 2 and so on.
		fingerPrefixName = selectPrefix(prefixNumber, prefixList)#this calls a function that returns an appropriate value for the prefix of the joint chain
		#the following for loop renames each finger based on its hierarchy, side and order in hierarchy
		for eachJoint in (list(reversed(fingerHierarchy))):
			cmds.rename(eachJoint, str(fingerPrefixName) + '_'+ str(globalSideOfBody) + '_Finger_' + str(fingerSequence) + '_' + str(jointNumber))
			jointNumber = jointNumber + 1
		fingerSequence = fingerSequence + 1
		i = i+1

def setupControlNodes(jointList, controlList):
	controlShapeList = globalControlShapeList
	masterControlShape = controlList.pop(0)

	i = 0
	for eachControl in controlList:
		firstKnuckle = jointList[i]
		#firstKnuckle = list(reversed(firstKnuckle))
		#setting up the attributes for the control shapes that will multiply the effect of the the movement of the controls (these can be adjusted for variance between curl of each finger)
		cmds.addAttr(eachControl, longName = 'CurlMultiplyerJoint1', attributeType = 'float', minValue = 0, maxValue = 180, defaultValue = 90, keyable = True)
		cmds.addAttr(eachControl, longName = 'CurlMultiplyerJoint2', attributeType = 'float', minValue = 0, maxValue = 180, defaultValue = 90, keyable = True)
		cmds.addAttr(eachControl, longName = 'CurlMultiplyerJoint3', attributeType = 'float', minValue = 0, maxValue = 180, defaultValue = 90, keyable = True)
		cmds.addAttr(eachControl, longName = 'SpreadMultiplyerJoint1', attributeType = 'float', minValue = -45, maxValue = 45, defaultValue = -15, keyable = True)

		#creating the math nodes that will take translate values from the controls and output them to rotation values for joints
		newSpreadPlusMinusAverageNode = cmds.shadingNode('plusMinusAverage', asUtility = True, name = eachControl + '_SpreadPlusMinusAverageNode')
		newSpreadMultDivNode = cmds.shadingNode('multiplyDivide', asUtility = True, name = eachControl + 'SpreadMultDivNode')

		#by default there is just one input for the 1D list.  You have to set the attributes to create them (buggy autodesk stuff)
		cmds.setAttr(newSpreadPlusMinusAverageNode + '.input1D[0]', 0)
		cmds.setAttr(newSpreadPlusMinusAverageNode + '.input1D[1]', 0)

		if controlList.index(controlList[i]) > 1:
			print('Pinky or Ring Found')

			newSpreadNegativeMultDivNode = cmds.shadingNode('multiplyDivide', asUtility  =  True, name = eachControl + 'SpreadNegMultDivNode')

			cmds.connectAttr(eachControl + '.translateZ', newSpreadPlusMinusAverageNode + '.input1D[0]', force = True)
			cmds.connectAttr(masterControlShape + '.translateZ', newSpreadNegativeMultDivNode + '.input1X',  force = True)
			cmds.setAttr(newSpreadNegativeMultDivNode + '.input2X', -1)
			cmds.connectAttr(newSpreadPlusMinusAverageNode + '.output1D', newSpreadMultDivNode + '.input1X')
			cmds.connectAttr(newSpreadNegativeMultDivNode + '.outputX', newSpreadPlusMinusAverageNode + '.input1D[1]', force = True)
			cmds.connectAttr(eachControl + '.SpreadMultiplyerJoint1', newSpreadMultDivNode + '.input2X', force = True )
			cmds.connectAttr(newSpreadMultDivNode + '.outputX', firstKnuckle + '.rotateY', force = True)

		else:
			objectType = cmds.objectType(firstKnuckle)
			cmds.connectAttr(eachControl + '.translateZ', newSpreadPlusMinusAverageNode + '.input1D[0]', force = True)
			cmds.connectAttr(masterControlShape + '.translateZ', newSpreadPlusMinusAverageNode + '.input1D[1]',  force = True)
			cmds.connectAttr(newSpreadPlusMinusAverageNode + '.output1D', newSpreadMultDivNode + '.input1X')
			cmds.connectAttr(eachControl + '.SpreadMultiplyerJoint1', newSpreadMultDivNode + '.input2X', force = True )
			cmds.connectAttr(newSpreadMultDivNode + '.outputX', firstKnuckle + '.rotateY', force = True)

		fingerJoints = cmds.listRelatives(firstKnuckle, allDescendents = True, type = 'joint')
		fingerJoints.append(firstKnuckle)
		i = i+1
		
		ia = 3
		for eachJoint in fingerJoints:

			newCurlMultDivNode = cmds.shadingNode('multiplyDivide', asUtility = True)
			newCurlPlusMinusAverageNode = cmds.shadingNode('plusMinusAverage', asUtility = True)

			#by default there is just one input for the 1D list.  You have to set the attributes to create them (buggy autodesk stuff)
			cmds.setAttr(newCurlPlusMinusAverageNode + '.input1D[0]', 0)
			cmds.setAttr(newCurlPlusMinusAverageNode + '.input1D[1]', 0)

			cmds.connectAttr(newCurlMultDivNode + '.outputX', eachJoint + '.rotateZ', force = True)
			cmds.connectAttr(eachControl + '.translateX', newCurlPlusMinusAverageNode + '.input1D[0]', force = True)
			cmds.connectAttr(masterControlShape + '.translateX', newCurlPlusMinusAverageNode + '.input1D[1]',  force = True)
			cmds.connectAttr(newCurlPlusMinusAverageNode + '.output1D', newCurlMultDivNode + '.input1X',  force = True)
			
			cmds.connectAttr(eachControl + '.CurlMultiplyerJoint' + str(ia), newCurlMultDivNode + '.input2X', force = True )
			ia = ia -1 

def parentControlShape(controlShape, controlJointRoot):
	hierarchyList = cmds.listRelatives(controlJointRoot, allDescendents=True, type='joint')
	for eachJoint in hierarchyList:
		shapeDupe = cmds.duplicate(controlShape, name = 'controlShape' + eachJoint)
		getShape = cmds.listRelatives(shapeDupe, shapes=True)
		cmds.parent(getShape, eachJoint, s=True, r=True)
		cmds.delete(shapeDupe)

def parentControlJoints_DrivenJoints(drivenRootJoint, controlRootJoint):
	drivenJointFingerList = cmds.listRelatives(drivenRootJoint, children=True, type = 'joint')
	controlJointFingerList = cmds.listRelatives(controlRootJoint, children=True, type = 'joint')
	
	#at this point the finger lists are lists of each of the first knuckles in each hierarchy
	i=0
	for eachJoint in controlJointFingerList:
		#if the list already exists it will continue to be added to rather than replaced.  The following will clear the list
		try:
			drivenJointHierarchyList
			del drivenJointHierarchyList[:]
			print('driven list found')
			
		except NameError:
			print('no driven list yet')
		try:
			controlJointHierarchyList
			del controlJointHierarchyList[:]
			print('control list found')
			
		except NameError:
			print('no control list yet')

		#adding the children of the passed root joints into a new list
		drivenJointHierarchyList = cmds.listRelatives(drivenJointFingerList[i], allDescendents=True, type='joint')
		controlJointHierarchyList = cmds.listRelatives(controlJointFingerList[i], allDescendents=True, type='joint')
		drivenJointHierarchyList.append(drivenJointFingerList[i])
		controlJointHierarchyList.append(controlJointFingerList[i])
		reversedDrivenJointHierarchyList = list(reversed(drivenJointHierarchyList))
		reversedControlJointHierarchyList = list(reversed(controlJointHierarchyList))

		ia = 0
		for eachjoint in controlJointHierarchyList:
			cmds.parent(reversedControlJointHierarchyList[ia], reversedDrivenJointHierarchyList[ia])
			if (ia+1 < len(reversedControlJointHierarchyList)):
				cmds.parent(reversedDrivenJointHierarchyList[ia+1], reversedControlJointHierarchyList[ia])
				ia = ia+1
		i = i+1

def parentConstrainHierarchy(targetJointsList, controlledJoints):
	print('parentConstrainHierarchy(), the targetJointsList is: ' + str(targetJointsList))
	print('parentConstrainHierarchy(), the targetJointsList length is: ' + str(len(targetJointsList)))
	if(len(targetJointsList) > 1):
		targetJointChildrenList = [] #This is a list that will hold lists of the children of each target joint that has been passed into parentConstrainHierarchy()
		#Breaking down the root joints into lists of their first sets of children (the root of each finger)
		i = 0
		for eachJointRoot in targetJointsList:
			targetJointChildrenList.append(cmds.listRelatives(targetJointsList[i], children = True, type = 'joint'))
			i = i + 1
			#At this point targetJointChildrenList is a list of each of the target hand's children, so a list that lists the roots of each hand's fingers
		print('parentConstrainHierarchy(), the targetJointChildrenList is: ' + str(targetJointChildrenList))

		controlledJointChildren = cmds.listRelatives(controlledJoints, children=True, type = 'joint')
		print('parentConstrainHierarchy(), the controlledJointChildern is: ' + str(controlledJointChildren))

		i = 0
		tempTargetKnuckles = []
		targetList = []  # we are trying to make a string? that will list all of the target joints to pass into the parent command
		targetJointHierarchyList = [[] for eachTopEntry in targetJointChildrenList]
		for eachTopEntry in targetJointChildrenList:

			for eachJoint in targetJointChildrenList[i]:#for each list of target fingers (divided by the root hands they belong to)  
				tempTargetKnuckles.extend(cmds.listRelatives(eachJoint, allDescendents = True, type='joint'))
				tempTargetKnuckles.append(eachJoint)
				print('parentConstrainHierarchy(), The tempTargetKnuckles list is:' ) + str(tempTargetKnuckles)
				targetJointHierarchyList[i].append(tempTargetKnuckles)
				tempTargetKnuckles = []
			print('parentConstrainHierarchy(), the targetJointHierarchyList is: ' + str(targetJointHierarchyList[i]))	
			i = i+1

		print('parentConstrainHierarchy(), the targetJointHierarchyList is: ' + str(targetJointHierarchyList))
		print('parentConstrainHierarchy(), a sample of the targetJointHierarchyList is: ' + str(targetJointHierarchyList[0][0]))

		i = 0
		for eachJoint in controlledJointChildren:
			#breaking each finger root down into lists of its children
			parentedJointKnuckleList = cmds.listRelatives(controlledJointChildren[i], allDescendents=True, type='joint')
			#adding the root back into each finger list
			parentedJointKnuckleList.append(controlledJointChildren[i])
		
			print('parentConstrainHierarchy(), the parentedJointHierarchyList is: ' + str(parentedJointKnuckleList))

			targetJointKnuckleList = targetJointHierarchyList[0][i], targetJointHierarchyList[1][i]
	

			print('parentConstrainHierarchy(), the targetJointKnuckleList is: ' + str(targetJointKnuckleList))

			ia = 0
			for eachJoint in parentedJointKnuckleList:#at this point parentedJointHierarchyList is a dynamic list of the finger joints to be parent constrained
				if ia < len(parentedJointKnuckleList):
					unpackedTargetList = targetJointKnuckleList[0][ia], targetJointKnuckleList[1][ia]
					print('parentConstrainHierarchy(), the unpackedTargetList is: ' + str(unpackedTargetList))
					parentConstraint = cmds.parentConstraint(unpackedTargetList, parentedJointKnuckleList[ia])
					cmds.connectAttr(str(globalControlBoxShape) + '.fkRigFollow', parentConstraint[0].encode('utf8') + '.' + targetJointKnuckleList[0][ia] + 'W0')
					cmds.connectAttr(str(globalControlBoxShape) + '.ikRigFollow', parentConstraint[0].encode('utf8') + '.' + targetJointKnuckleList[1][ia] + 'W1')
					ia = ia+1
			i = i+1


	elif(len(targetJointsList) == 1):
		print('parentConstrainHierarchy() , There is only one target')
		targetJointChildrenList = (cmds.listRelatives(targetJointsList, children = True, type = 'joint'))
		controlledJointChildrenList = cmds.listRelatives(controlledJoints, children=True, type = 'joint')

		print('parentConstrainHierarchy(), the targetJointChildrenList is: ' + str(targetJointChildrenList))
		print('parentConstrainHierarchy(), the controlledJointChildrenList is: ' + str(controlledJointChildrenList))

		i = 0
		for eachJoint in controlledJointChildrenList:
			print('parentConstrainHierarchy(), the targetJointChildrenList is: ' + str(targetJointChildrenList))
			print('parentConstrainHierarchy(), the controlledJointChildrenList is: ' + str(controlledJointChildrenList))
			#breaking each finger root down into lists of its children
			parentedJointKnuckleList = cmds.listRelatives(controlledJointChildrenList[i], allDescendents=True, type='joint')
			targetJointKnuckleList = cmds.listRelatives(targetJointChildrenList[i], allDescendents=True, type='joint')
			#adding the root back into each finger list
			parentedJointKnuckleList.append(controlledJointChildrenList[i])
			targetJointKnuckleList.append(targetJointChildrenList[i])

			print('parentConstrainHierarchy(), the parentedJointHierarchyList is: ' + str(parentedJointKnuckleList))
			print('parentConstrainHierarchy(), the targetJointKnuckleList is: ' + str(targetJointKnuckleList))

			ia = 0
			for eachJoint in parentedJointKnuckleList:#at this point parentedJointHierarchyList is a dynamic list of the finger joints to be parent constrained
				if ia < len(parentedJointKnuckleList):
					parentConstraint = cmds.parentConstraint(targetJointKnuckleList[ia], parentedJointKnuckleList[ia])
					cmds.connectAttr(str(globalControlBoxShape) + '.targetRigFollow', parentConstraint[0].encode('utf8') + '.' + targetJointKnuckleList[ia] + 'W0')
					ia = ia+1
			i = i+1


def createIkHandles(jointRoot):	
	pathToFile = '%s/%s' % (scriptsUserDirectory.rsplit('/', 3)[0], 'assets/jfm_transformControl.mb')#regroving the scripts path to go to the assets file
	loadedControlShape = cmds.file(pathToFile, i = True) #importing the objects from the file, this does not return the object so you must refer to it by name 'jfm_transformControl'
	fingerRootList = cmds.listRelatives(jointRoot, children = True, type = 'joint')
	
	ikControlGroup = cmds.group(empty = True, name = globalSideOfBody + '_IKControlGroup')#creating a group to parent all controls
	snapToObj(jointRoot, ikControlGroup)#snapping and freezing transforms for the group

	parentConstraint = cmds.parentConstraint(globalDuplicatedHandList[4], ikControlGroup)

	masterIKControlShape = cmds.duplicate('jfm_transformControl', name = globalSideOfBody + '_Master_IK_Finger_Control')
	cmds.parent(masterIKControlShape, ikControlGroup)
	snapToObj(globalDuplicatedHandList[4], masterIKControlShape)
	if globalSideOfBody == 'Left':
		transformValues = [[5,0,0], [0,0,0], [2,2,2]]
	if globalSideOfBody == 'Right':
		transformValues = [[-5,0,0], [0,0,0], [2,2,2]]
	transformObjects(masterIKControlShape, transformValues)
	cmds.connectAttr(globalControlBoxShape + '.ikRigVisibility', masterIKControlShape[0] +  '.visibility', force = True )
	cmds.addAttr(masterIKControlShape[0], longName = 'rigFollow', attributeType = 'float', minValue = 0, maxValue = 1, defaultValue = 1, keyable = True)
	cmds.connectAttr(str(masterIKControlShape[0]) + '.rigFollow', parentConstraint[0].encode('utf8') + '.' + str(globalDuplicatedHandList[4]) + 'W0')
	

	fingerRootIndex = 0
	for eachJoint in fingerRootList:
		objectType = cmds.objectType(eachJoint)
		fingerJointList = cmds.listRelatives(eachJoint, allDescendents = True, type = 'joint')
		fingerJointList.append(fingerRootList[fingerRootIndex])
		firstJoint = fingerJointList[-1]
		lastJoint = fingerJointList[0]
		effectorJoint = cmds.duplicate(lastJoint, name = lastJoint + '_effectorJoint')
		cmds.parent(effectorJoint, lastJoint)
		if globalSideOfBody == 'Left':
			cmds.move(2,0,0, effectorJoint, localSpace = True)
		if globalSideOfBody == 'Right':
			cmds.move(-2,0,0, effectorJoint, localSpace = True)
		newIkHandle = cmds.ikHandle(startJoint = firstJoint, endEffector = effectorJoint[0])
		newControlShape = cmds.duplicate('jfm_transformControl', name = eachJoint + '_IkHndl')
		snapToObj(newIkHandle, newControlShape)
		transformSettings = [[0,0,0], [0,0,0], [.25,.25,.25]]
		transformObjects(newControlShape, transformSettings)
		cmds.parent(newIkHandle[0], newControlShape)
		objectType = cmds.objectType(newIkHandle[0])
		cmds.setAttr(newIkHandle[0] + '.visibility', 0)
		cmds.parent(newControlShape, masterIKControlShape)
		fingerRootIndex = fingerRootIndex + 1
	cmds.delete('jfm_transformControl')

def createConnections(controlledObjectRoot, controlledAttribute, controllingObject, controllingAttribute):
	jointList = cmds.listRelatives(controlledObjectRoot, allDescendents = True)
	for eachJoint in jointList:
		cmds.connectAttr(controllingObject + controllingAttribute, eachJoint + controlledAttribute,)

def setHandJointLimits(handJointRoot, maintainOffsets):
	#this block sets transform limits on the fingers of the hand
	print('main(), the selectedJoint is: ' + str(handJointRoot))
	reorderFingers(handJointRoot)
	fingerList = cmds.listRelatives(handJointRoot, children = True, type = 'joint')
	print('the fingerList is: ' + str(fingerList))
	thumbKnuckleList = cmds.listRelatives(fingerList[0], allDescendents = True, type = 'joint')
	thumbKnuckleList.append(fingerList[0])
	fingerList.pop(0)
	print('thumbKnuckleList is: ' + str(thumbKnuckleList))
	applyLimits([thumbKnuckleList[2]], maintainOffsets, [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [0, 0, -22.5, 22.5, -65, 35], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1] )
	applyLimits([thumbKnuckleList[1]], maintainOffsets, [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, -90, 45], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1] )
	applyLimits([thumbKnuckleList[0]], maintainOffsets, [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, -90, 45], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1] )
	for eachFinger in fingerList:
		knuckleList = cmds.listRelatives(eachFinger, allDescendents = True, type = 'joint')
		knuckleList.append(eachFinger)
		for eachKnuckle in knuckleList:
			applyLimits([eachKnuckle], maintainOffsets, [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [0,0, -22.5,22.5,  -100,35], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1] )
		
#The form for calling this script will look like:
#applyLimits(listOrObjectToPass, False, [1, 1, 1, 1, 1, 1], [-1.5, 1.5, -1.5, 1.5, -1.5, 1.5], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1])
#note that if you are passing a single item into the function you will need to bundle the item into a list:
#applyLimits([listOrObjectToPass], False, [1, 1, 1, 1, 1, 1], [-1.5, 1.5, -1.5, 1.5, -1.5, 1.5], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1])
#listOrObjectToPass is either a single object or a list that you want to setup limits on
#maintainTranslationOffsets is a bool that tells the function whether it should read the existing translation values and lock them into place (used primarily for joints)
#translateLimits are essentially bools (0 or 1) that tells whether upper or lower limits for each transform channel (xyz) should be imposed or not
#translateValues are the upper and lower max limits for the translate x,y and z channels
#rotateLimits are essentially bools (0 or 1) that tells whether upper or lower limits for each rotation channel (xyz) should be imposed or not
#rotateValues are the upper and lower max limits for the rotate x,y and z channels
#scaleLimits are essentially bools (0 or 1) that tells whether upper or lower limits for each scale channel (xyz) should be imposed or not
#scaleValues are the upper and lower max limits for the scale x,y and z channels
def applyLimits(objectListForLimits, maintainTranslationOffsets, transformLimits, translateValues, rotateLimits, rotateValues, scaleLimits, scaleValues):
	print('applyLimits(), the objectListForLimits is : ' + str(objectListForLimits))

	i = 0
	for eachObject in objectListForLimits:	
		transformPosition = cmds.xform(eachObject, query = True, translation = True)
		print('applyLimits(), the transformPositionValues for ' + str(eachObject) + ' are: ' + str(transformPosition))
		print('applyLimits(), maintainTranslationOffsets for ' + str(eachObject) + ' is: ' + str(maintainTranslationOffsets))
		if maintainTranslationOffsets == True and transformLimits[0] == 1 and transformLimits[1] == 1:
			print('applyLimits(), the max and min translation value for ' + str(eachObject) + ' is: ' + str(transformPosition[0]))
			translateValues[0] = transformPosition[0]
			translateValues[1] = transformPosition[0]
		if maintainTranslationOffsets == True and transformLimits[2] == 1 and transformLimits[3] == 1:
			print('applyLimits(), the max and min translation value for ' + str(eachObject) + ' is: ' + str(transformPosition[1]))
			translateValues[2] = transformPosition[1]
			translateValues[3] = transformPosition[1]
		if maintainTranslationOffsets == True and transformLimits[4] == 1 and transformLimits[5] == 1:
			print('applyLimits(), the max and min translation value for ' + str(eachObject) + ' is: ' + str(transformPosition[2]))
			translateValues[4] = transformPosition[2]
			translateValues[5] = transformPosition[2]

		cmds.transformLimits(eachObject, enableTranslationX = [transformLimits[0], transformLimits[1]], tx =(translateValues[0], translateValues[1]))
		cmds.transformLimits(eachObject, enableTranslationY = [transformLimits[2], transformLimits[3]], ty=(translateValues[2], translateValues[3]))
		cmds.transformLimits(eachObject, enableTranslationZ = [transformLimits[4], transformLimits[5]], tz=(translateValues[4], translateValues[5]))

		cmds.transformLimits(eachObject, enableRotationX = [rotateLimits[0], rotateLimits[1]], rx =(rotateValues[0], rotateValues[1]))
		cmds.transformLimits(eachObject, enableRotationY = [rotateLimits[2], rotateLimits[3]], ry=(rotateValues[2], rotateValues[3]))
		cmds.transformLimits(eachObject, enableRotationZ = [rotateLimits[4], rotateLimits[5]], rz=(rotateValues[4], rotateValues[5]))

		cmds.transformLimits(eachObject, enableScaleX = [scaleLimits[0], scaleLimits[1]], sx =(scaleValues[0], scaleValues[1]))
		cmds.transformLimits(eachObject, enableScaleY = [scaleLimits[2], scaleLimits[3]], sy=(scaleValues[2], scaleValues[3]))
		cmds.transformLimits(eachObject, enableScaleZ = [scaleLimits[4], scaleLimits[5]], sz=(scaleValues[4], scaleValues[5]))
		i = i + 1

#start of main function
selectedJoint = cmds.ls(selection = True)

#this block checks to see if a target rig already exists for the hand and removes the finger joints, retaining the root for orienting the hand rigs
extantHandRigList = []
if cmds.objExists('TARGET_Lft_HandRoot'):
	extantHandRigList.append('TARGET_Lft_HandRoot')
if cmds.objExists('TARGET_Rt_HandRoot'):
	extantHandRigList.append('TARGET_Rt_HandRoot')
if len(extantHandRigList) > 0:
	print('main(), a TARGET rig was found')
	for eachObject in extantHandRigList:
		print('duplicateJoints(), the extantHandRigList: ' + str(extantHandRigList))
		deleteFingerList = cmds.listRelatives(eachObject)
		cmds.delete(deleteFingerList)
		sideOfBody = detectSideOfBody(eachObject)	
		targetJoint = cmds.rename(eachObject, 'TARGET_' + str(sideOfBody) + '_Wrist')
		print('duplicateJoints(), the targetJoint is: ' + str(targetJoint))

	#the following block detects if there is an existing parent constraint attribute for each joint and if so removes that attr 
	selectedJointChildList = cmds.listRelatives(selectedJoint, allDescendents = True, type = 'joint')
	for eachJoint in selectedJointChildList:
		selectedShape = cmds.listRelatives(eachJoint, type = 'parentConstraint')
		attributeList = cmds.listAttr(selectedShape)
		print(attributeList)
		for eachAttribute in attributeList:
				if 'TARGET' in eachAttribute:
					print('found ' + eachAttribute)
					print('The attribute to delete is: ' + str(selectedShape) + '.' + eachAttribute)
					cmds.deleteAttr(str(selectedShape) + '.' + eachAttribute)

if selectedJoint == 'SKIN_Left_HandRoot':
	parentConstrainHierarchy('TARGET_Lft_Wrist', [selectedJoint])
if selectedJoint == 'SKIN_Left_HandRoot':
	parentConstrainHierarchy('TARGET_Rt_Wrist', [selectedJoint])

duplicateJoints(selectedJoint)

#assigning all of the root joints to specific variables (this is really more about being explicative than anything)
rigRootJoint = globalDuplicatedHandList[0]
ikRootJoint = globalDuplicatedHandList[1]
controlRootJoint = globalDuplicatedHandList[2]
drivenRootJoint = globalDuplicatedHandList[3]
skinRootJoint = globalDuplicatedHandList[4]

if globalSideOfBody == 'Left':
	#loading the hand controller shape (a hand shape) which is a container for all of the controls for the hands and fingers 
	scriptsUserDirectory = cmds.internalVar(usd=True) #getting this version of maya scripts directory
	pathToFile = '%s/%s' % (scriptsUserDirectory.rsplit('/', 3)[0], 'assets/jfm_leftHandControlbox.mb')#regroving that path to go to the assets file
	loadedControlShape = cmds.file(pathToFile, i = True)
	#for some reason, and I have no idea why, the import is not returning the object
	#so we have to resort to this very sloppy method of knowing the name of the object and passing in its actual name
	loadedControlShape = cmds.rename('jfm_leftHandControlBox', globalSideOfBody + '_' + 'Hand_Control_Box')
	cmds.addAttr(loadedControlShape, longName = 'IK_Blend', attributeType = 'float', minValue = 0, maxValue = 0, defaultValue = 0, keyable = True)

if globalSideOfBody == 'Right':
	#loading the hand controller shape (a hand shape) which is a container for all of the controls for the hands and fingers 
	scriptsUserDirectory = cmds.internalVar(usd=True) #getting this version of maya scripts directory
	pathToFile = '%s/%s' % (scriptsUserDirectory.rsplit('/', 3)[0], 'assets/jfm_rightHandControlbox.mb')#regroving that path to go to the assets file
	loadedControlShape = cmds.file(pathToFile, i = True)
	#for some reason, and I have no idea why, the import is not returning the object
	#so we have to resort to this very sloppy method of knowing the name of the object and passing in its actual name
	loadedControlShape = cmds.rename('jfm_rightHandControlBox', globalSideOfBody + '_' + 'Hand_Control_Box')
	cmds.addAttr(loadedControlShape, longName = 'IK_Blend', attributeType = 'float', minValue = 0, maxValue = 0, defaultValue = 0, keyable = True)

globalControlBoxShape = loadedControlShape

transformSettings = [[0, 0, 0], [0, 0, 0], [1, 1, 1]] #this object will be unchanged so it's transform settings are the default
snapToObj(drivenRootJoint, loadedControlShape)#calling a function that centers and zeros transforms for the hand controller shape

#create a list of the controls contained in the HandControlBox
fingerControlList = cmds.listRelatives(loadedControlShape, children = True, type = 'transform')
#create a list of the joints, reorderJoints() makes sure that the joints are in the same order as the controls
firstKnuckleList = cmds.listRelatives(drivenRootJoint, children = True)
setupControlNodes(firstKnuckleList, fingerControlList)
applyLimits(fingerControlList, False, [1, 1, 1, 1, 1, 1], [-1.5, 1.5, -1.5, 1.5, -1.5, 1.5], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1])

targetJointsList = [controlRootJoint, ikRootJoint]		
parentConstrainHierarchy(targetJointsList, rigRootJoint)
parentConstrainHierarchy([rigRootJoint], [skinRootJoint])

#this block creates all of the fk control shapes and places them in the hierarchy for the control joints
pathToFile = '%s/%s' % (scriptsUserDirectory.rsplit('/', 3)[0], 'assets/jfm_fkKnuckleControl.mb')#regroving that path to go to the assets file
loadedControlShape = cmds.file(pathToFile, i = True)
controlShape = 'jfm_fkKnuckleControl'
if globalSideOfBody == 'Right':
	cmds.scale( 1, -1, 1, controlShape )
	cmds.makeIdentity(controlShape, apply = True, translate = True, rotate = True, scale = True)
parentControlShape(controlShape, controlRootJoint)#this function unpacks the hand and distributes the control shapes over each joint
cmds.delete(controlShape)

#this block sets up limits on all of the joints controlling for movements in the hand that should not happen or will "break" the rig
setHandJointLimits(controlRootJoint, False)
setHandJointLimits(drivenRootJoint, True)
 
parentControlJoints_DrivenJoints(drivenRootJoint, controlRootJoint) 

setHandJointLimits(skinRootJoint, True)
setHandJointLimits(rigRootJoint, True)
setHandJointLimits(ikRootJoint, True)

createIkHandles(ikRootJoint)

createConnections(drivenRootJoint, '.visibility', globalControlBoxShape, '.fkRigVisibility')
createConnections(ikRootJoint, '.visibility', globalControlBoxShape, '.ikRigVisibility')
createConnections(rigRootJoint, '.visibility', globalControlBoxShape, '.targetRigVisibility')

handControllsNull = cmds.group(empty = True, name = globalSideOfBody + '_HandJointRootNull')
snapToObj(skinRootJoint, handControllsNull) 
skinRootJoint = globalDuplicatedHandList.pop(4)

for eachJoint in globalDuplicatedHandList:
	print('main() eachJoint is : ' + str(eachJoint))
	deletedArtifact = cmds.listRelatives(eachJoint, type = 'transform', parent = True)
	cmds.ungroup(deletedArtifact, parent = handControllsNull)	
cmds.parentConstraint(skinRootJoint, handControllsNull, maintainOffset = True)
cmds.parent(globalControlBoxShape, handControllsNull)
cmds.delete(controlRootJoint)
