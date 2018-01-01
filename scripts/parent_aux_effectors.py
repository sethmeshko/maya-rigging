#parent_aux_effectors.py
#Author: Seth Meshko, 3danimationartist.com
#This script will take a child, parent selection and then parent the child under the parent with a null buffer
#Note, this leaves the buffer null's transformations relative to world zero (important for AUX effector in HIK system)
import maya.cmds as cmds

selectionList = cmds.ls( selection=True ) #create a list of object from your current selection
storedSelectionList = selectionList

null=cmds.group(empty=True)
nullName = cmds.rename(null, selectionList[0] + 'Null')  #appends the name of the object with "Null"
print (nullName)
cmds.parent(selectionList,nullName)
cmds.parent(storedSlectionList[1],nullName)