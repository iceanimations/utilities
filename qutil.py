import os
import os.path as osp

def splitPath(path):
    components = [] 
    while True:
        (path,tail) = os.path.split(path)
        if tail == "":
            components.reverse()
            return components
        components.append(tail)

def basename3(path):
    return osp.join(*splitPath(path)[-3:])

def mkdir(path, dirs):
    for d in splitPath(dirs):
        path = osp.join(path, d)
        os.mkdir(path)