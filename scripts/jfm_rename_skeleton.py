#jfm_rename_skeleton.py
#author: Seth Meshko, 3danimationartist.com
#Opens a window that allows the user create a prefix and rename an entire skeleton for retargeting ease in unreal.
#Change the names in the directory to match your rig

import maya.cmds as cmds
import functools

windowID = 'jfm_rename_skeleton_window'

def renameObject(text, dic):
	for i, j in dic.iteritems():
		text = text.replace(i, j)
	return text 

def renameSkeleton(*args):
    prefixName = cmds.textField(prefixNameTextField, editable = True, query = True, text=True)
    handList = [prefixName +'LeftHand', prefixName +'RightHand']
    print('The hand list is: ' + str(handList))
    fingerList = []
    for eachHand in handList:
        fingerList.extend(cmds.listRelatives(eachHand, allDescendents = True, type = 'joint'))
    print('The finger list is: ' + str(fingerList))
    for eachJoint in fingerList:
        dictionary = {'Hand' : ""}
        print('eachJoint is: ' + str(eachJoint))
        newName = renameObject(str(eachJoint), dictionary)
        newObject = cmds.rename(eachJoint, newName)

    skeletonRoot = cmds.ls(selection = True)
    skeletonList = cmds.listRelatives(skeletonRoot, allDescendents = True, type = 'joint')
    skeletonList.insert(0, skeletonRoot[0])
    print('The skeleton list is: ' + str(skeletonList))

    for eachJoint in skeletonList:
        print('The joint being checked for ' + str(prefixName) + ' is ' + eachJoint)
        if str(prefixName) not in eachJoint:
            print(str(prefixName) + 'was not found in ' + eachJoint)
        else:
            for eachJoint in skeletonList:
                dictionary = {str(prefixName) : "", 'Reference' : 'root', 'Hips' : 'pelvis', 'Spine' : 'spine_01', 'Spine1' : 'spine_02', 'Spine2' : 'spine_03',
                'LeftShoulder' : 'clavicle_l', 'RightShoulder' : 'clavicle_r',  'LeftArm' : 'upperarm_l', 'RightArm' : 'upperarm_r', 'LeftForeArm' : 'lowerarm_l', 'RightForeArm' : 'lowerarm_r',
                'LeftHand' : 'hand_l', 'RightHand' : 'hand_r',
                'LeftIndex1' : 'index_01_l', 'LeftIndex2' : 'index_02_l', 'LeftIndex3' : 'index_03_l',
                'RightIndex1' : 'index_01_r', 'RightIndex2' : 'index_02_r', 'RightIndex3' : 'index_03_r',
                'LeftMiddle1' : 'middle_01_l', 'LeftMiddle2' : 'middle_02_l', 'LeftMiddle3' : 'middle_03_l',
                'RightMiddle1' : 'middle_01_r', 'RightMiddle2' : 'middle_02_r', 'RightMiddle3' : 'middle_03_r',
                'LeftRing1' : 'ring_01_l', 'LeftRing2' : 'ring_02_l', 'LeftRing3' : 'ring_03_l',
                'RightRing1' : 'ring_01_r', 'RightRing2' : 'ring_02_r', 'RightRing3' : 'ring_03_r',
                'LeftPinky1' : 'pinky_01_l', 'LeftPinky2' : 'pinky_02_l', 'LeftPinky3' : 'pinky_03_l',
                'RightPinky1' : 'pinky_01_r', 'RightPinky2' : 'pinky_02_r', 'RightPinky3' : 'pinky_03_r',
                'LeftThumb1' : 'thumb_01_l', 'LeftThumb2' : 'thumb_02_l', 'LeftThumb3' : 'thumb_03_l',
                'RightThumb1' : 'thumb_01_r', 'RightThumb2' : 'thumb_02_r', 'RightThumb3' : 'thumb_03_r',
                'Rig_Neck' : 'neck_01', 'Rig_Head' : 'head', 
                'LeftUpLeg' : 'thigh_l', 'LeftLeg' : 'calf_l', 'LeftFoot' : 'foot_l', 'LeftToeBase' : 'ball_l',
                'RightUpLeg' : 'thigh_r', 'RightLeg' : 'calf_r', 'RightFoot' : 'foot_r', 'RightToeBase' : 'ball_r', }
                newName = renameObject(eachJoint, dictionary)
                cmds.rename(eachJoint, newName)
            

#Start GUI

if cmds.window(windowID, exists=True):
	cmds.deleteUI(windowID)

cmds.window(windowID, title='SM Rename Skeleton', sizeable=True, width = 500)

#Start of 1st frame
cmds.rowColumnLayout(numberOfColumns=1, columnWidth=[(1,500)], columnOffset=[(1,'both', 3)])

cmds.text(label = 'Select the root of the skeleton', align = 'center')

#Start of 1st frame content
cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1,200), (2,300)], columnOffset=[(1,'both', 3)])

#horizontal spacer row
cmds.separator(h=10, style='none')
cmds.separator(h=10, style='none')
cmds.setParent('..')


cmds.text(label = 'Enter the prefix to remove', align = 'center')
prefixNameTextField = cmds.textField(text = 'Sinful_baseSkeleton:BaseRig_')


#horizontal spacer row
cmds.separator(h=10, style='none')
cmds.separator(h=10, style='none')
cmds.setParent('..')

cmds.rowColumnLayout(numberOfColumns=1, columnWidth=[(1,500)], columnOffset=[(1,'both', 3)])
cmds.button(label = 'Rename Skeleton', command = renameSkeleton)


cmds.showWindow()