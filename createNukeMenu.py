from site import addsitedir as asd
asd(r'R:\Python_Scripts\Nuke')
asd('R:/Python_Scripts/maya2014/PyQt')
import nuke

def replaceReadPaths():
    import replaceReadPath as rrp
    reload(rrp)
    rrp.Window().show()

# add new script to the following dict
# key => name of the script that will appear in the nuke under ICE Scripts menu
# value => name of the function to be called when user clicks that menu item
# finally create that function somewhere above the dict

nukeMenu = {
            'Replace Read Paths': replaceReadPaths
            }

def create():
    for name, func in nukeMenu.items():
        nuke.menu('Nuke').addCommand('ICE Scripts/'+ name, func)