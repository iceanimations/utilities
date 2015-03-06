import os
import re
import operator
import os.path as osp
try: # because of Nuke
    import pymel.core as pc
except:
    pass


def splitPath(path):
    '''splits a file or folder path and returns as a list
    'D:/path/to/folder/or/file' -> ['D:', 'path', 'to', 'folder', 'or', 'file']
    '''
    components = [] 
    while True:
        (path,tail) = os.path.split(path)
        if tail == "":
            components.reverse()
            return components
        components.append(tail)

def basename3(path):
    '''returns last 3 entries in a file or folder path as a string'''
    return osp.join(*splitPath(path)[-3:])

def mkdir(path, dirs):
    '''makes directories or folders recursively in a given path'''
    for d in splitPath(dirs):
        path = osp.join(path, d)
        os.mkdir(path)
        
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

def getNiceName(name):
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