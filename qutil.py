import os
import operator
import os.path as osp


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
    '''returns the specified attribute of a node traversing to the last parent'''
    attr = (0, 0, 0)
    for _ in range(200):
        attr = tuple(operator.add(attr, pc.PyNode(str(node)+ '.'+ attribute).get()))
        try:
            node= node.firstParent()
        except pc.MayaNodeError:
            break
    return attr