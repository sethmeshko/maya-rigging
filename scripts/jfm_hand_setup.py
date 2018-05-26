#jfm_hand_setup 
#Released 12/11/2017
#Updated 05/26/2018 -- Modification of the controls to allow for a slower more descrete curl of the fingers, also now script allows for the hand to be unparented
#Created by Seth Meshko, Digital Artist, www.3danimationartist.com
#Creates a window that automates a number of tasks for rigging a humanoid character hand
#Requires objects from a folder called assets that must reside in the mydocs maya folder, download and copy that file.  It's available
#in the github directory
import maya.cmds as cmds

globalDuplicatedHandList = [] #This is a variable that will be used to store the joint hierarchies of the duplicated hands 
globalSideOfBody = '' #This is a variable that will be used to store the side of the body that we are on.
globalControlShapeList = [] #This is a variable that will store a list of the duplicated hand joint hierarchies.  The resulting order should be: rig, ik, control, driven, skin
globalControlBoxShape = []	#This is a variable that will store a shape that contains the driven controls for the hand



def createConnections(controlledObjectRoot, controlledAttribute, controllingObject, controllingAttribute):
	jointList = cmds.listRelatives(controlledObjectRoot, allDescendents = True)
	for eachJoint in jointList:
		cmds.connectAttr(controllingObject + controllingAttribute, eachJoint + controlledAttribute,)



def createIkHandles(jointRoot):	
	loadedControlShape = importShape('jfm_transformControl') 

	fingerRootList = cmds.listRelatives(jointRoot, children = True, type = 'joint')
	
	ikControlGroup = cmds.group(empty = True, name = globalSideOfBody + '_IKControlGroup')#creating a group to parent all controls
	snapToObj(jointRoot, ikControlGroup)#snapping and freezing transforms for the group

	parentConstraint = cmds.parentConstraint(globalDuplicatedHandList[4], ikControlGroup)

	masterIKControlShape = cmds.duplicate(loadedControlShape, name = globalSideOfBody + '_Master_IK_Finger_Control')
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
		newControlShape = cmds.duplicate(loadedControlShape, name = eachJoint + '_IkHndl')
		snapToObj(newIkHandle, newControlShape)
		transformSettings = [[0,0,0], [0,0,0], [.25,.25,.25]]
		transformObjects(newControlShape, transformSettings)
		cmds.parent(newIkHandle[0], newControlShape)
		objectType = cmds.objectType(newIkHandle[0])
		cmds.setAttr(newIkHandle[0] + '.visibility', 0)
		cmds.parent(newControlShape, masterIKControlShape)
		fingerRootIndex = fingerRootIndex + 1
	cmds.delete(loadedControlShape)
	print('createIKHandles() Complete!')



def detectCompoundJointChain(jointToAnalize, index):
	jointChild = cmds.listRelatives(jointToAnalize, children = True, type = 'joint')
	
	if jointChild != None:
		jointLocationA = cmds.xform(jointToAnalize, query = True, translation = True)
		jointLocationB = cmds.xform(jointChild, query = True, translation = True)
		
		if jointLocationA == jointLocationB:
			print('setHandJointLimits(), Compound joint chain detected')
		

	else:
		print('detectCompoundJointChain(), end of joint chain detected')
		return
	

#This function will return the side of the body the passed joint is on
#note, it assumes that the character is oriented down the Z axis with the joint's X transform being to either side of the character
#assumes no nulls or intermediate joints exist above the joint being passed  
def detectSideOfBody(objectToCalculate, frozenTransforms = False):
	print('detectSideOfBody(), the objectToCalculate is: ' + str(objectToCalculate))
	if frozenTransforms == False:
		transformPosition = cmds.xform(objectToCalculate, query = True, translation = True)

	else:
		tempTransform = cmds.group(empty = True, world = True,  name = 'jfmTempGroupNode' + str(objectToCalculate))
		snapToObj(objectToCalculate, tempTransform, False)
		transformPosition = cmds.xform(tempTransform, query = True, translation = True)
		cmds.delete(tempTransform)
	print('detectSideOfBody(), the transformPosition is: ' + str(transformPosition))
	if(transformPosition[0] > 0):
		sideOfBody = 'Lft'
	else:
		sideOfBody = 'Rt'
	
	return sideOfBody 


def duplicateJoints(jointToDuplicate):
	'''
	We need a total of 5 duplicate joint hierarchies.  The first is the "Skin" joints which are already extant.  Then seconde we need the "Rig" 
	joints which will be setup to follow either the FK or IK rigs with a toggle.  Then third and forth we need the two joint hierarchies that 
	will support "FK" and "Driven" movement (these work in coordination with eachother and ultimately are part of the same immediate hierarchy).
	Finally we will need the "IK" joints.
	'''
	print('duplicateJoints(), the jointToDuplicate is: ' + str(jointToDuplicate))
	originalJointHierarchy = cmds.listRelatives(jointToDuplicate, allDescendents = True, type = 'joint')


	KnuckleTranslateList=[['translation'], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
	KnuckleRotationList=[['rotation'], [0, 0, 0, 0, 0, 0], [-360, 360, -360, 360, -360, 360]]
	KnuckleScaleList=[['scale'], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1]]


	for eachJoint in originalJointHierarchy:
		#removing limitations if they exist
		applyLimits([eachJoint], KnuckleTranslateList)
		applyLimits([eachJoint], KnuckleRotationList)
		applyLimits([eachJoint], KnuckleScaleList)
		#removing locks if they exist
		cmds.setAttr(str(eachJoint) + '.translateX', lock = False, keyable = True)
		cmds.setAttr(str(eachJoint) + '.translateY', lock = False, keyable = True)
		cmds.setAttr(str(eachJoint) + '.translateZ', lock = False, keyable = True)
		cmds.setAttr(str(eachJoint) + '.rotateX', lock = False, keyable = True)
		cmds.setAttr(str(eachJoint) + '.rotateY', lock = False, keyable = True)
		cmds.setAttr(str(eachJoint) + '.rotateZ', lock = False, keyable = True)
		cmds.setAttr(str(eachJoint) + '.scaleX', lock = False, keyable = True)
		cmds.setAttr(str(eachJoint) + '.scaleY', lock = False, keyable = True)
		cmds.setAttr(str(eachJoint) + '.scaleZ', lock = False, keyable = True)

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
		newObjectParent = cmds.listRelatives(newObject, parent = True)
		if newObjectParent != None:
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
		
	

#imports a shape from the assets file, you just need to know the name of the file to get
#IMPORTANT use namespace check mark has to be off in your file import settings for this to work
def importShape(nameOfFile):
	scriptsUserDirectory = cmds.internalVar(usd=True) #getting this version of maya scripts directory which is in the same directory as the assets folder
	pathToFile = '%s/%s' % (scriptsUserDirectory.rsplit('/', 3)[0], 'assets/' + nameOfFile + '.mb')#regroving that path to go to the assets folder
	cmds.file(pathToFile, i = True, groupReference = True, groupName = 'loadedShapeGroup')
	importedObject = cmds.listRelatives('loadedShapeGroup', children = True)
	cmds.parent(importedObject, world = True)
	cmds.delete('loadedShapeGroup')
	return importedObject



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
		for eachJoint in controlJointHierarchyList:
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



def renameObject(text, dic):
	for i, j in dic.iteritems():
		text = text.replace(i, j)
	return text 



def reorderFingers(selectedJoint):
	print('reorderFingers(), the selectedJoint is: ' + str(selectedJoint))
	
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



def selectPrefix(prefixNumber, prefixList):
	for eachEntry, eachOutput in prefixList.iteritems():
		if (eachEntry == prefixNumber):
			prefixName = eachOutput
			return prefixName



def setupControlNodes(jointList, controlList):
	masterControlShape = controlList.pop(0)
		
	i = 0
	for eachControl in controlList:
		firstKnuckle = jointList[i]
		#setting up the attributes for the control shapes that will multiply the effect of the the movement of the controls (these can be adjusted for variance between curl of each finger)
		cmds.addAttr(eachControl, longName = 'CurlMultiplyerJoint1', attributeType = 'float', minValue = 0, maxValue = 180, defaultValue = 30, keyable = True)
		cmds.addAttr(eachControl, longName = 'CurlMultiplyerJoint2', attributeType = 'float', minValue = 0, maxValue = 180, defaultValue = 30, keyable = True)
		cmds.addAttr(eachControl, longName = 'CurlMultiplyerJoint3', attributeType = 'float', minValue = 0, maxValue = 180, defaultValue = 30, keyable = True)
		cmds.addAttr(eachControl, longName = 'SpreadMultiplyerJoint1', attributeType = 'float', minValue = -45, maxValue = 45, defaultValue = -15, keyable = True)
		cmds.addAttr(masterControlShape, longName = str(jointList[i]) + '_SpreadMultiplier', attributeType = 'float', minValue = -5, maxValue = 5, defaultValue = 1, keyable = True)

		#creating the math nodes that will take translate values from the controls and output them to rotation values for joints	
		newMasterSpreadMultDivNode = cmds.shadingNode('multiplyDivide', asUtility  =  True, name = jointList[i] + 'MasterSpreadMultDivNode')
		newSpreadPlusMinusAverageNode = cmds.shadingNode('plusMinusAverage', asUtility = True, name = eachControl + '_SpreadPlusMinusAverageNode')
		newSpreadMultDivNode = cmds.shadingNode('multiplyDivide', asUtility = True, name = eachControl + 'SpreadMultDivNode')

		#by default there is just one input for the 1D list.  You have to set the attributes to create them (buggy autodesk stuff)
		cmds.setAttr(newSpreadPlusMinusAverageNode + '.input1D[0]', 0)
		cmds.setAttr(newSpreadPlusMinusAverageNode + '.input1D[1]', 0)

		cmds.connectAttr(eachControl + '.translateZ', newSpreadPlusMinusAverageNode + '.input1D[0]', force = True)
		cmds.connectAttr(masterControlShape + '.' + str(jointList[i]) + '_SpreadMultiplier', newMasterSpreadMultDivNode + '.input2X')
		cmds.connectAttr(masterControlShape + '.translateZ', newMasterSpreadMultDivNode + '.input1X',  force = True)
		cmds.connectAttr(newSpreadPlusMinusAverageNode + '.output1D', newSpreadMultDivNode + '.input1X')
		cmds.connectAttr(newMasterSpreadMultDivNode + '.outputX', newSpreadPlusMinusAverageNode + '.input1D[1]', force = True)
		cmds.connectAttr(eachControl + '.SpreadMultiplyerJoint1', newSpreadMultDivNode + '.input2X', force = True )
		cmds.connectAttr(newSpreadMultDivNode + '.outputX', firstKnuckle + '.rotateY', force = True)

		fingerJoints = cmds.listRelatives(firstKnuckle, allDescendents = True, type = 'joint')
		fingerJoints.append(firstKnuckle)
		i = i+1
		
		ia = 3
		for eachJoint in fingerJoints:

			newCurlMultDivNode = cmds.shadingNode('multiplyDivide', asUtility = True, name = eachJoint + 'CurlMultDivNode')
			newCurlPlusMinusAverageNode = cmds.shadingNode('plusMinusAverage', asUtility = True, name = eachJoint + 'CurlPlusMinusAverageNode')

			#by default there is just one input for the 1D list.  You have to set the attributes to create them (buggy autodesk stuff)
			cmds.setAttr(newCurlPlusMinusAverageNode + '.input1D[0]', 0)
			cmds.setAttr(newCurlPlusMinusAverageNode + '.input1D[1]', 0)

			cmds.connectAttr(newCurlMultDivNode + '.outputX', eachJoint + '.rotateZ', force = True)
			cmds.connectAttr(eachControl + '.translateX', newCurlPlusMinusAverageNode + '.input1D[0]', force = True)
			cmds.connectAttr(masterControlShape + '.translateX', newCurlPlusMinusAverageNode + '.input1D[1]',  force = True)
			cmds.connectAttr(newCurlPlusMinusAverageNode + '.output1D', newCurlMultDivNode + '.input1X',  force = True)
			
			cmds.connectAttr(eachControl + '.CurlMultiplyerJoint' + str(ia), newCurlMultDivNode + '.input2X', force = True )
			ia = ia -1 
	controlList.append(masterControlShape)



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



def transformObjects(objectToTransform, transformValues):
	translateValues = transformValues[0]
	scaleValues = transformValues[2]

	cmds.move(translateValues[0], translateValues[1], translateValues[2], objectToTransform, relative = True)
	cmds.scale(scaleValues[0],scaleValues[1], scaleValues[2], objectToTransform)
	cmds.makeIdentity(objectToTransform, apply = True, translate = True, rotate = True, scale = True)  #Freeze Transform




def setHandJointLimits(handJointRoot, maintainOffsets, compoundJoints):
	#this block sets transform limits on the fingers of the hand
	print('setHandJointLimits(), the selectedJoint is: ' + str(handJointRoot))
	reorderFingers(handJointRoot)
	fingerList = cmds.listRelatives(handJointRoot, children = True, type = 'joint')
	print('setHandJointLimits(), the fingerList is: ' + str(fingerList))
	#taking thumb out of finger list as it has different limitations than the other fingers
	thumbRoot = fingerList.pop(0)
	thumbKnuckleList = cmds.listRelatives(thumbRoot, allDescendents = True, type = 'joint')
	thumbKnuckleList.append(thumbRoot)
	thumbKnuckleList = list(reversed(thumbKnuckleList))
	print('thumbKnuckleList is: ' + str(thumbKnuckleList))

	#setting up lists that will contain lists of transformSettings for successive joints in the thumb chain
	thumbKnuckleTranslateList = []
	thumbKnuckleRotationList = []
	thumbKnuckleScaleList = []

	fingerKnuckleTranslateList = []
	fingerKnuckleRotationList = []
	fingerKnuckleScaleList = []


	#poplulating the lists with specific values for each joint in the chain
	thumbKnuckleTranslateList.append([['translation'], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0]])
	thumbKnuckleTranslateList.append([['translation'], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0]])
	thumbKnuckleTranslateList.append([['translation'], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0]])

	thumbKnuckleRotationList.append([['rotation'], [1, 1, 1, 1, 1, 1], [0, 0, -40, 40, -65, 20]])
	thumbKnuckleRotationList.append([['rotation'], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, -90, 20]])
	thumbKnuckleRotationList.append([['rotation'], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, -90, 45]])

	thumbKnuckleScaleList.append([['scale'], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]])
	thumbKnuckleScaleList.append([['scale'], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]])
	thumbKnuckleScaleList.append([['scale'], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]])


	fingerKnuckleTranslateList.append([['translation'], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0]])
	fingerKnuckleTranslateList.append([['translation'], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0]])
	fingerKnuckleTranslateList.append([['translation'], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0]])

	fingerKnuckleRotationList.append([['rotation'], [1, 1, 1, 1, 1, 1], [0, 0, -40, 40, -100, 35]])
	fingerKnuckleRotationList.append([['rotation'], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, -90, 20]])
	fingerKnuckleRotationList.append([['rotation'], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, -90, 20]])

	fingerKnuckleScaleList.append([['scale'], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]])
	fingerKnuckleScaleList.append([['scale'], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]])
	fingerKnuckleScaleList.append([['scale'], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]])

	
	if compoundJoints == True:
		print('_____________________________________Compound Joints Activated_____________________')
		#thumbKnuckleList is all of the joints of the thumb including compound joints
		i=0
		while len(thumbKnuckleList) > 1:
			print('setHandJointsLimits(), the thumbKnuckleList 0 is: ' + str(thumbKnuckleList[0]))	
			jointChild = cmds.listRelatives(thumbKnuckleList[0], children = True, type = 'joint')
			print('setHandJointsLimits(), the jointChild is: ' + str(jointChild))	
			if jointChild != None:
				compoundJointList = [thumbKnuckleList[0], jointChild]
				applyLimits(compoundJointList, thumbKnuckleTranslateList[i])
				applyLimits(compoundJointList, thumbKnuckleRotationList[i])
				applyLimits(compoundJointList, thumbKnuckleScaleList[i])
				#these should shorten the list, making it terminate
			del thumbKnuckleList[0]
			del thumbKnuckleList[0]
			print('setHandJointsLimits(), thumbKnuckleList is: ' + str(thumbKnuckleList))	
			i = i+1
		print('setHandJointsLimits(), Compound Thumb Joints Complete')
	
		for eachFinger in fingerList:
			print('setHandJointsLimits(), the fingerList is: ' + str(fingerList))
			fingerKnuckleList = cmds.listRelatives(eachFinger, allDescendents = True, type = 'joint')
			fingerKnuckleList.append(eachFinger)
			fingerKnuckleList = list(reversed(fingerKnuckleList))
			ia=0
			while len(fingerKnuckleList) > 1:
				print('setHandJointsLimits(), the fingerKnuckleList[0] is: ' + str(fingerKnuckleList[0]))	
				fingerJointChild = cmds.listRelatives(fingerKnuckleList[0], children = True, type = 'joint')
				print('setHandJointsLimits(), the fingerJointChild is: ' + str(fingerJointChild))
				if fingerJointChild != None:
					compoundJointList = [fingerKnuckleList[0], fingerJointChild]
					applyLimits(compoundJointList, fingerKnuckleTranslateList[ia])
					applyLimits(compoundJointList, fingerKnuckleRotationList[ia])
					applyLimits(compoundJointList, fingerKnuckleScaleList[ia])
					#these should shorten the list, making it terminate
					del fingerKnuckleList[0]
					del fingerKnuckleList[0]
					print('setHandJointsLimits(), fingerList is: ' + str(fingerList))	
					ia = ia+1
			print('setHandJointsLimits(), Compound Finger Joints Complete')		
	else:
		print('Compound Joints Not Active')
		ib = 0
		for eachjoint in thumbKnuckleList:
			applyLimits([eachjoint], thumbKnuckleTranslateList[ib])
			applyLimits([eachjoint], thumbKnuckleRotationList[ib])
			applyLimits([eachjoint], thumbKnuckleScaleList[ib])
			ib = ib+1
		for eachFinger in fingerList:
			#The first knuckle has different rotation limits than the rest
			applyLimits([eachFinger], fingerKnuckleTranslateList[0])
			applyLimits([eachFinger], fingerKnuckleRotationList[0])
			applyLimits([eachFinger], fingerKnuckleScaleList[ 0])
			knuckleList = cmds.listRelatives(eachFinger, allDescendents = True, type = 'joint')
			#The second and third knuckles have the same limitations
			for eachKnuckle in knuckleList:
				applyLimits([eachKnuckle], fingerKnuckleTranslateList[1])
				applyLimits([eachKnuckle], fingerKnuckleRotationList[1])
				applyLimits([eachKnuckle], fingerKnuckleScaleList[1])
				

#to use this function build a list of lists and pass it as the second argument:
#knuckleTranslateList=[['translation'], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
#knuckleRotationList=[['rotation'], [0, 0, 0, 0, 0, 0], [-360, 360, -360, 360, -360, 360]]
#knuckleScaleList=[['scale'], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1]]
#applyLimits(someJoint, knuckleTranslateList)
#the structure for the list of lists is [[the transform channel], [6 bools for min/max limits], [6 values for min/max values]]
def applyLimits(objectListForLimits, transformSettings):
	#print('applyLimits(), the objectListForLimits is: ' + str(objectListForLimits))
	#print('applyLimits(), the transformSettings are: ' + str(transformSettings))
	transformType = transformSettings[0][0]
	#print('applyLimits(), the transformType is: ' + str(transformType))
	transformLimits = transformSettings[1]
	#print('applyLimits(), the transformLimits are: ' + str(transformLimits))
	transformValues = list(transformSettings[2])
	#print('applyLimits(), the transformValues are: ' + str(transformValues))


	i = 0
	for eachObject in objectListForLimits:
		transformValues = list(transformSettings[2])
		if transformType == 'translation':
			#print('applyLimits(), the object for transformPosition is: ' + str(eachObject))
			#print('applyLimits(), the transformType is ' + str(transformType))
			transformPosition = cmds.xform(eachObject, query = True, translation = True)
		else:
			transformPosition = [0,0,0]
	
		#print('applyLimits(), the transformPosition values for ' + str(eachObject) + ' are: ' + str(transformPosition))
		#print('applyLimits(), the transform value transformPosition[0] data type is:  ' + str(type(transformPosition[0])))

		#print('applyLimits(), the max and min transformX value for ' + str(eachObject) + ' is: ' + str(transformPosition[0]))
		transformValues[0] = transformPosition[0] + transformValues[0]
		transformValues[1] = transformPosition[0] + transformValues[1]
		
		#print('applyLimits(), the max and min transformY value for ' + str(eachObject) + ' is: ' + str(transformPosition[1]))
		transformValues[2] = transformPosition[1] + transformValues[2]
		transformValues[3]= transformPosition[1] + transformValues[3]
		
		#print('applyLimits(), the max and min transformZ value for ' + str(eachObject) + ' is: ' + str(transformPosition[2]))
		transformValues[4] = transformPosition[2] + transformValues[4]
		transformValues[5] = transformPosition[2] + transformValues[5]

		if transformType == 'translation':
			print('applyLimits(), Limiting translation')
			cmds.transformLimits(eachObject, enableTranslationX = (transformLimits[0], transformLimits[1]), tx=(transformValues[0], transformValues[1]))
			cmds.transformLimits(eachObject, enableTranslationY = (transformLimits[2], transformLimits[3]), ty=(transformValues[2], transformValues[3]))
			cmds.transformLimits(eachObject, enableTranslationZ = (transformLimits[4], transformLimits[5]), tz=(transformValues[4], transformValues[5]))
		elif transformType == 'rotation':
			print('applyLimits(), Limiting rotation')
			cmds.transformLimits(eachObject, enableRotationX = (transformLimits[0], transformLimits[1]), rx=(transformValues[0], transformValues[1]))
			cmds.transformLimits(eachObject, enableRotationY = (transformLimits[2], transformLimits[3]), ry=(transformValues[2], transformValues[3]))
			cmds.transformLimits(eachObject, enableRotationZ = (transformLimits[4], transformLimits[5]), rz=(transformValues[4], transformValues[5]))
		elif transformType == 'scale':
			print('applyLimits(), Limiting scale')
			cmds.transformLimits(eachObject, enableScaleX = (transformLimits[0], transformLimits[1]), sx=(transformValues[0], transformValues[1]))
			cmds.transformLimits(eachObject, enableScaleY = (transformLimits[2], transformLimits[3]), sy=(transformValues[2], transformValues[3]))
			cmds.transformLimits(eachObject, enableScaleZ = (transformLimits[4], transformLimits[5]), sz=(transformValues[4], transformValues[5]))
		else:
			print('Neither transform, rotation or scale was detected')
		i = i + 1

#setAttributes(eachObject, attributeSuffixStringList, [0, 0, 0, 0, 1, 1, 1], True, False)
def setAttributes(objectString, attributeStringList, attributeValueList, locked, keyable):
	i = 0
	for eachChannel in attributeStringList:
		cmds.setAttr(objectString + eachChannel, attributeValueList[i], lock = locked, keyable = keyable)
		i = i+1



#start of main function
selectedJoint = cmds.ls(selection = True)
print('main(), the selectedJoint is: ' + str(selectedJoint))

#this block checks to see if a target rig already exists for the hand and removes the finger joints, retaining the root for orienting the hand rigs.
#This is pretty specific to a larger rigging process that contains this script.  If there is no existing Target Rig then this is of no consequence.

targetHand = renameObject(selectedJoint[0], {'SKIN': 'TARGET'})
print('main(), the targetHand string is: ' + targetHand)

if cmds.objExists(targetHand):
	print(str(targetHand) + ' Exists' )
	deleteFingerList = cmds.listRelatives(targetHand)
	cmds.delete(deleteFingerList)
	sideOfBody = detectSideOfBody(selectedJoint)	
	targetJoint = cmds.rename(targetHand, 'TARGET_' + str(sideOfBody) + '_Wrist')
	print('duplicateJoints(), the targetJoint is: ' + str(targetJoint))

	#the following block detects if there is an existing parent constraint attribute for each joint and if so removes that attr 
	selectedJointChildList = cmds.listRelatives(selectedJoint, allDescendents = True, type = 'joint')
	for eachJoint in selectedJointChildList:
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
	loadedControlShape = importShape('jfm_Left_Hand_Control_Box')
	print('globalSideOfBody(), the loadedControlShape is: ' + str(loadedControlShape))

if globalSideOfBody == 'Right':
	#loading the hand controller shape (a hand shape) which is a container for all of the controls for the hands and fingers 
	loadedControlShape = importShape('jfm_Right_Hand_Control_Box')
	print('globalSideOfBody(), the loadedControlShape is: ' + str(loadedControlShape))

loadedControlShape = cmds.rename(loadedControlShape, globalSideOfBody + '_' + 'Hand_Control_Box')

globalControlBoxShape = loadedControlShape

snapToObj(drivenRootJoint, loadedControlShape)#calling a function that centers and zeros transforms for the hand controller shape

#create a list of the controls contained in the HandControlBox
fingerControlList = cmds.listRelatives(loadedControlShape, children = True, type = 'transform')

firstKnuckleList = cmds.listRelatives(drivenRootJoint, children = True)
setupControlNodes(firstKnuckleList, fingerControlList)
print('--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
print('main(), the fingerControlList is: ' + str(fingerControlList))

#setting up limits on the finger controls
fingerControlTranslateList = [['translation'], [1, 1, 1, 1, 1, 1], [-3, 3, -3, 3, -3, 3]]
fingerControlRotationList = [['rotation'], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0]]
fingerControlScaleList = [['scale'], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]]
applyLimits(fingerControlList, fingerControlTranslateList)
applyLimits(fingerControlList, fingerControlRotationList)
applyLimits(fingerControlList, fingerControlScaleList)
	
targetJointsList = [controlRootJoint, ikRootJoint]		
parentConstrainHierarchy(targetJointsList, rigRootJoint)
parentConstrainHierarchy([rigRootJoint], [skinRootJoint])

#this block creates all of the fk control shapes and places them in the hierarchy for the control joints
controlShape = importShape('jfm_FK_Knuckle_Control')
if globalSideOfBody == 'Right':
	cmds.scale( 1, -1, 1, controlShape )
	cmds.makeIdentity(controlShape, apply = True, translate = True, rotate = True, scale = True)
parentControlShape(controlShape, controlRootJoint)#this function unpacks the hand and distributes the control shapes over each joint
cmds.delete(controlShape)
print('main(), parent controls shape imported')
 
parentControlJoints_DrivenJoints(drivenRootJoint, controlRootJoint)

#this block sets up limits on all of the joints controlling for movements in the hand that should not happen or will "break" the rig
setHandJointLimits(skinRootJoint, True, False)
setHandJointLimits(rigRootJoint, True, False)
setHandJointLimits(ikRootJoint, True, False)
setHandJointLimits(drivenRootJoint, True, True)

createIkHandles(ikRootJoint)

createConnections(drivenRootJoint, '.visibility', globalControlBoxShape, '.fkRigVisibility')
createConnections(ikRootJoint, '.visibility', globalControlBoxShape, '.ikRigVisibility')
createConnections(rigRootJoint, '.visibility', globalControlBoxShape, '.targetRigVisibility')

handControllsNull = cmds.group(empty = True, name = globalSideOfBody + '_HandJointRootNull')
snapToObj(skinRootJoint, handControllsNull) 
skinRootJoint = globalDuplicatedHandList.pop(4)

#placing all of the hand roots in a common group
for eachJoint in globalDuplicatedHandList:
	cmds.parent(eachJoint, handControllsNull)

#insuring that the duplicate joints and controls all follow the rig 
cmds.parentConstraint(skinRootJoint, handControllsNull, maintainOffset = True)
cmds.parent(globalControlBoxShape, handControllsNull)
cmds.delete(controlRootJoint)#unesessary joint

attributeSuffixStringList = ['.translateY','.rotateX', '.rotateY', '.rotateZ', '.scaleX', '.scaleY', '.scaleZ']

if globalSideOfBody == 'Left':
	objectList = ['CONTROLS_Left_Hand_Master', 'CONTROLS_Left_Thumb', 'CONTROLS_Left_Index', 'CONTROLS_Left_Middle', 'CONTROLS_Left_Ring', 'CONTROLS_Left_Pinky']

if globalSideOfBody == 'Right':
	objectList = ['CONTROLS_Right_Hand_Master', 'CONTROLS_Right_Thumb', 'CONTROLS_Right_Index', 'CONTROLS_Right_Middle', 'CONTROLS_Right_Ring', 'CONTROLS_Right_Pinky']

for eachObject in objectList:
	setAttributes(eachObject, attributeSuffixStringList, [0, 0, 0, 0, 1, 1, 1], True, False)


if globalSideOfBody == 'Left':
	cmds.setAttr('CONTROLS_Left_Hand_Master' + '.DRIVEN_Left_Finger_1_1_SpreadMultiplier', 1)
	cmds.setAttr('CONTROLS_Left_Hand_Master' + '.DRIVEN_Left_Finger_2_1_SpreadMultiplier', .75)
	cmds.setAttr('CONTROLS_Left_Hand_Master' + '.DRIVEN_Left_Finger_3_1_SpreadMultiplier', 0)
	cmds.setAttr('CONTROLS_Left_Hand_Master' + '.DRIVEN_Left_Finger_4_1_SpreadMultiplier', -.5)
	cmds.setAttr('CONTROLS_Left_Hand_Master' + '.DRIVEN_Left_Finger_5_1_SpreadMultiplier', -1)

if globalSideOfBody == 'Right':
	cmds.setAttr('CONTROLS_Right_Hand_Master' + '.DRIVEN_Right_Finger_1_1_SpreadMultiplier', 1)
	cmds.setAttr('CONTROLS_Right_Hand_Master' + '.DRIVEN_Right_Finger_2_1_SpreadMultiplier', .75)
	cmds.setAttr('CONTROLS_Right_Hand_Master' + '.DRIVEN_Right_Finger_3_1_SpreadMultiplier', 0)
	cmds.setAttr('CONTROLS_Right_Hand_Master' + '.DRIVEN_Right_Finger_4_1_SpreadMultiplier', -.5)
	cmds.setAttr('CONTROLS_Right_Hand_Master' + '.DRIVEN_Right_Finger_5_1_SpreadMultiplier', -1)

print('----------------------------------------Hand Setup Complete-----------------------------------')
