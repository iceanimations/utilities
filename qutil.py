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

def getUsername():
    return os.environ['USERNAME']


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