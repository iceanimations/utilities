import os
import re
import operator
import os.path as osp
import csv
try: # because of Nuke
    import pymel.core as pc
    import maya.cmds as cmds
except:
    pass
import string # for get_drives
from ctypes import windll # for get_drives

FPS_MAPPINGS = {'film (24 fps)': 'film', 'pal (25 fps)': 'pal'}

def addCamera(name):
    command = '''
    string $camera[] = `camera -n persp -hc "viewSet -p %camera"`;   viewSet -p $camera[0];   lookThroughModelPanel $camera[0] modelPanel4;   if (`optionVar -q "viewportRenderer"`== 2) ActivateViewport20; else setRendererInModelPanel base_OpenGL_Renderer modelPanel4;
    '''
    pc.mel.eval(command)
    camera = pc.ls(sl=True)[0]
    pc.rename(camera, name)
    return camera

def getUsername():
    return os.environ['USERNAME']

def addOptionVar(name, value):
    if type(value) == type(int):
        pc.optionVar(iv=(name, value))
    elif isinstance(value, basestring):
        pc.optionVar(sv=(name, value))
        
def getOptionVar(name):
    if pc.optionVar(exists=name):
        return pc.optionVar(q=name)


def getFileType():
    return cmds.file(q=True, type=True)[0]

def getExtension():
    '''returns the extension of the file name'''
    return '.ma' if getFileType() == 'mayaAscii' else '.mb'

def setRenderableCamera(camera, append=False):
    '''truns the .renderable attribute on for the specified camera. Turns
    it off for all other cameras in the scene if append is set to True'''
    if not append:
        for cam in pc.ls(cameras=True):
            if cam.renderable.get():
                cam.renderable.set(False)
    camera.renderable.set(True)

def dictionaryToDetails(_dict, anl='Reason'):
    '''converts a dictinary containing key values as strings to a string
    each key value pair separated by \n and each item (key value) both separated
    by \n\n'''
    
    return '\n\n'.join(['\n%s: '.join([key, value])%anl for key, value in _dict.items()])

def splitPath(path):
    '''splits a file or folder path and returns as a list
    'D:/path/to/folder/or/file' -> ['D:', 'path', 'to', 'folder', 'or', 'file']
    '''
    components = [] 
    while True:
        (path,tail) = os.path.split(path)
        if tail == "":
            if path:
                components.append(path)
            components.reverse()
            return components
        components.append(tail)
        
def getCSVFileData(fileName):
    '''returns list of tupples containing the csv file rows separated by comma'''
    with open(fileName, 'rb') as csvfile:
        tuples = list(csv.reader(csvfile, delimiter=','))
    return tuples

def basename(path, depth=3):
    '''returns last 'depth' entries in a file or folder path as a string'''
    return osp.join(*splitPath(path)[-depth:])

def dirname(path, depth=3):
    '''removes last 'depth' entries from a file or folder path'''
    return osp.normpath(osp.join(*splitPath(path)[:-depth]))

def mkdir(path, dirs):
    '''makes directories or folders recursively in a given path'''
    for d in splitPath(dirs):
        path = osp.join(path, d)
        try:
            os.mkdir(path)
        except:
            pass

def getAttrRecursiveGroup(node, attribute):
    '''returns the specified attribute (translation, rotation, scale) of a node traversing to the last parent'''
    attr = (0, 0, 0)
    for _ in range(200):
        attr = tuple(operator.add(attr, pc.PyNode(str(node)+ '.'+ attribute).get()))
        try:
            node= node.firstParent()
        except pc.MayaNodeError:
            break
    return attr

def getNiceName(name, full=False):
    if full:
        return name.replace(':', '_').replace('|', '_')
    return name.split(':')[-1].split('|')[-1]

def fileExists(path, fileName):
    for name in os.listdir(path):
        try:
            if re.search(fileName+'_v\d{3}', name):
                return True
        except:
            pass

def getLastVersion(path, fileName, nxt=False):
    versions = []
    for version in os.listdir(path):
        try:
            versions.append(int(re.search('_v\d{3}', version).group().split('v')[-1]))
        except AttributeError:
            pass
    if versions:
        temp = max(versions) + 1 if nxt else max(versions)
        return fileName +'_v'+ str(temp).zfill(3)
    
def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1
    return drives

def getReferences(loaded=False, unloaded=False):
    refs = []
    for ref in pc.ls(type=pc.nt.Reference):
        if ref.referenceFile():
            refs.append(ref.referenceFile())
    if loaded:
        return [ref for ref in refs if ref.isLoaded()]
    if unloaded:
        return [ref for ref in refs if not ref.isLoaded()]
    return refs

def getRefFromSet(geoset):
    for ref in getReferences(loaded=True):
        if geoset in ref.nodes():
            return ref 

def addRef(path):
    try:
        namespace = os.path.basename(path)
        namespace = os.path.splitext(namespace)[0]
        match = re.match('(.*)([-._]v\d+)(.*)', namespace)
        if match:
            namespace = match.group(1) + match.group(3)
        return pc.createReference(path, namespace=namespace, mnc=False)
    except Exception as ex:
        self.errorsList.append('Could not create Reference for\n'+ path +'\nReason: '+ str(ex))

def getCombinedMesh(ref):
    '''returns the top level meshes from a reference node'''
    meshes = []
    if ref:
        for node in pc.FileReference(ref).nodes():
            if type(node) == pc.nt.Mesh:
                try:
                    node.firstParent().firstParent()
                except pc.MayaNodeError:
                    if not node.isIntermediate():
                        meshes.append(node.firstParent())
                except Exception as ex:
                    #self.errorsList.append('Could not retrieve combined mesh for Reference\n'+ref.path+'\nReason: '+ str(ex))
                    pass
    return meshes

def getMeshFromSet(ref):
    meshes = []
    if ref:
        try:
            _set = [obj for obj in ref.nodes() if 'geo_set' in obj.name()
                    and type(obj)==pc.nt.ObjectSet ][0]
            meshes = [shape
                    for transform in pc.PyNode(_set).dsm.inputs(type="transform")
                    for shape in transform.getShapes(type = "mesh", ni = True)]
            #return [pc.polyUnite(ch=1, mergeUVSets=1, *_set.members())[0]] # put the first element in list and return
            combinedMesh = pc.polyUnite(ch=1, mergeUVSets=1, *meshes)[0]
            combinedMesh.rename(qutil.getNiceName(_set) + '_combinedMesh')
            return [combinedMesh] # put the first element in list and return
        except:
            return meshes
    return meshes

def applyCache(mapping):
    '''applies cache on the combined models connected to geo_sets
    and exports the combined models'''
    errorsList = []
    if mapping:
        count = 1
        for cache, path in mapping.items():
            cacheFile = cache+'.xml'
            if osp.exists(cacheFile):
                if path:
                    if osp.exists(path):
                        ref = addRef(path)
                        meshes = getCombinedMesh(ref)
#                         if len(meshes) != 1:
#                             meshes = getMeshFromSet(ref)
                        if meshes:
                            if len(meshes) == 1:
                                pc.mel.doImportCacheFile(cacheFile.replace('\\', '/'), "", meshes, list())
                            else:
                                errorsList.append('Unable to identify Combined mesh or ObjectSet\n'+ path +'\n'+ '\n'.join(meshes))
                                pc.delete(meshes)
                                ref.remove()
                        else:
                            errorsList.append('Could not find or build combined mesh from\n'+path)
                            ref.remove()
                    else:
                        errorsList.append('LD path does not exist for '+cache+'\n'+ path)
                else:
                    errorsList.append('No LD added for '+ cache)
            else:
                errorsList.append('cache file does not exist\n'+ cache)
    else:
        errorsList.append('No mappings found in the file')
    return errorsList