#AnimIO.py
from maya import cmds
import json
import os


class animCurveIO():
    def __init__(self):
        self.curveDict = {}
        
        
    def addObjects(self):
        """Adds joint objects to list.
        """
        joints = cmds.ls(type='joint')
        keyedObjects = self.keyedAttributes(joints)
        
        self._objectData = keyedObjects
        
        
    def keyedAttributes(self, objects):    
        """Get Keyed attrs of objects

        Args:
            objects (list): The joints found in the scene.
        """
        objectsDict = {}
        for object in objects:
            keyedAttributes = [attr.split('_')[-1] for attr in cmds.keyframe(object, q=1, name=1)]
            objectsDict[object] = keyedAttributes
            
        return objectsDict
                        

    def getAnimCurveData(self, object, attribute):
        """Gets the animation data from the given object and attribute.

        Args:
            object (str): The object with animaton
            attribute (str): The animated attribue on the object.
        """
        if not object in self.curveDict:
            self.curveDict[object] = {}
        self.curveDict[object][attribute] = {}
        
        objectNoNamespace = object.split(':')[-1] # Curves do not hold the namespace, so it is removed to find the curve name.
        curve = f'{objectNoNamespace}_{attribute}'
        
        # Get the tangent type of each keyframe
        keyframe_count = cmds.keyframe(curve, q=1, keyframeCount=1)
        
        for index in range(keyframe_count):
            # Get the tangent type of the keyframe at the given index
            tangent_lock = cmds.keyTangent(curve, index=(index,), q=1, lock=1)[0]
            
            tangent_in_type = cmds.keyTangent(curve, index=(index,), q=1, inTangentType=1)[0]
            tangent_out_type = cmds.keyTangent(curve, index=(index,), q=1, outTangentType=1)[0]
            
            weighted_tangents = cmds.keyTangent(curve, index=(index,), q=1, weightedTangents=1)[0]
            in_weight = cmds.keyTangent(curve, index=(index,), q=1, inWeight=1)[0]
            in_angle = cmds.keyTangent(curve, index=(index,), q=1, inAngle=1)[0]
            
            out_weight = cmds.keyTangent(curve, index=(index,), q=1, outWeight=1)[0]
            out_angle = cmds.keyTangent(curve, index=(index,), q=1, outAngle=1)[0]
            
            out_x = out_weight = cmds.keyTangent(curve, index=(index,), q=1, ox=1)[0]
            out_y = out_weight = cmds.keyTangent(curve, index=(index,), q=1, oy=1)[0]
            in_x = out_weight = cmds.keyTangent(curve, index=(index,), q=1, ix=1)[0]
            in_y = out_weight = cmds.keyTangent(curve, index=(index,), q=1, iy=1)[0]
            
            key = cmds.keyframe(curve, q=1, index=(index,), timeChange=1)[0]
            value = cmds.keyframe(object, attribute=attribute, time=(key,), q=1, valueChange=1)[0] 
            
            self.curveDict[object][attribute][index] = { # ADD ONE FOR TANGENT BREAK/ LOCKING
                "curve" : curve,
                'tangent lock' : tangent_lock,
                'keyframe' : key,
                'value' : value,
                'tangent in' : tangent_in_type,
                'tangent out' : tangent_out_type,
                'weighted tangents' : weighted_tangents,
                'tangent in weight' : in_weight,
                'tangent out weight' : out_weight,
                'tangent in angle' : in_angle,
                'tangent out angle' : out_angle,
                'outX' : out_x,
                'outY' : out_y,
                'inX'  : in_x,
                'inY'  : in_y
            }
  
    
    
    def exportJSON(self, data, file):
        """Export a JSON file of all the animation data.

        Args:
            data (dict): The animation data dictionary.
            file (str): The filepath
        """
        with open(file, 'w') as f:
            json.dump(data, f, indent=2)
        print(end=file)


    def importJSON(self, file):
        """Imports a JSON file of the animateion data.

        Args:
            file (str): The filepath

        Returns:
            data (dict): The read animation data.
        """
        with open(file) as f:
            data = json.load(f)
            
        return data


    def setAnimCurveData(self, curveDict):
        """Adds the keys and edits the curves to match exactly.

        Args:
            curveDict (dict): Dictionary of the animation data.
        """
        for object in curveDict:
            for attribute in curveDict[object]:
                for index in curveDict[object][attribute]: 
                    curveData = curveDict[object][attribute][index]
                    
                    curve = curveData['curve']
                    
                    key = curveData["keyframe"]
                    cmds.setKeyframe(object, attribute=attribute, time=key, value=curveData['value'])  

                    cmds.keyTangent(curve, e=1, index=(index,), inTangentType=curveData['tangent in'])
                    cmds.keyTangent(curve, e=1, index=(index,), outTangentType=curveData['tangent out'])
                    cmds.keyTangent(curve, e=1, index=(index,), lock=curveData['tangent lock'])
                    cmds.keyTangent(curve, e=1, index=(index,), weightedTangents=curveData['weighted tangents'])
                    cmds.keyTangent(curve, e=1, index=(index,), inWeight=curveData['tangent in weight'])
                    cmds.keyTangent(curve, e=1, index=(index,), outWeight=curveData['tangent out weight'])
                    cmds.keyTangent(curve, e=1, index=(index,), inAngle=curveData['tangent in angle'])
                    cmds.keyTangent(curve, e=1, index=(index,), outAngle=curveData['tangent out angle'])
                    
                    cmds.keyTangent(curve, e=1, index=(index,), ox=curveData['outX'])
                    cmds.keyTangent(curve, e=1, index=(index,), oy=curveData['outY'])
                    cmds.keyTangent(curve, e=1, index=(index,), ix=curveData['inX'])
                    cmds.keyTangent(curve, e=1, index=(index,), iy=curveData['inY'])
                    
    
        
    def offsetKeys(self, objects, offsetFactor):
        """Offset the keys of the imported animation.

        Args:
            objects (list): The joint objects.
            offsetFactor (float): How many frames to offset by.
        """
        cmds.keyframe(objects, relative=1, timeChange=offsetFactor)
        
        
    def scaleKeys(self, objects, scaleFactor, timePivot):
        """Scale the keys of the imported animation.

        Args:
            objects (list): The joint objects.
            scaleFactor (float): How much to scale the keys by.
            timePivot (float): The anchor for where everything scales from.
        """
        cmds.scaleKey(objects, timeScale=scaleFactor, timePivot=timePivot)
       
        
    def fixRotations(self, objects):
        """Performs the euler filter on the curves after they've been scaled.
        This is because when scaling the keys, many times the created in-betweens are not calculated correctly. 

        Args:
            objects (list): The joint objects.
        """
        cmds.select(objects, replace=1)
        cmds.filterCurve()                    
              
              
    def adjustTimeline(self, objects):
        """Adjusts the timeline to fit the scaled and offset animation.

        Args:
            objects (list): The joint objects.
        """
        cmds.select(objects, replace=1)
        firstKey = cmds.findKeyframe(which='first')
        lastKey = cmds.findKeyframe(which='last')        
        cmds.playbackOptions(e=1, min=firstKey, max=lastKey, animationStartTime=firstKey, animationEndTime=lastKey)
            
                    
    @classmethod
    def importAnimData(cls, file, offsetFactor=0, scaleFactor=1, timePivot=0):
        """Import the animation data.

        Args:
            file (str): The filepath
            offsetFactor (int, optional): How many frames to offset the animation. Defaults to 0.
            scaleFactor (int, optional): How much to scale the keys by. Defaults to 1.
            timePivot (int, optional): Where to scale from. Defaults to 0.
        """        
        setAnimData = cls()
        curveDict = setAnimData.importJSON(file)
        setAnimData.setAnimCurveData(curveDict)
        
        objects = list(curveDict.keys())
        setAnimData.offsetKeys(objects, offsetFactor)
        setAnimData.scaleKeys(objects, scaleFactor, timePivot)
        setAnimData.fixRotations(objects)
        setAnimData.adjustTimeline(objects)
        
                    
                    
    @classmethod    
    def exportAnimData(cls, file):
        getAnimData = cls()
        getAnimData.addObjects()
        for object, attrs in getAnimData._objectData.items():
            for attr in attrs:
                getAnimData.getAnimCurveData(object, attr)
                
        getAnimData.exportJSON(getAnimData.curveDict, file)


                
            
            
