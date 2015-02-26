import sip
sip.setapi('QString', 2)
import nuke
import nukeMenuCommands
reload(nukeMenuCommands)
from nukeMenuCommands import *

# add new script to the following dict
# key => name of the script that will appear in the nuke under ICE Scripts menu
# value => name of the function to be called when user clicks that menu item
# finally create that function in the nukeMenuCommands.py

nukeMenu = {
            'Replace Read Paths': replaceReadPaths,
            'Red To Default': fromRedToDefault,
            'Batch Render': renderWrites
            }
menuName = 'ICE Scripts/'
def create():
    nuke.menu('Nuke').removeItem(menuName[0:-1])
    for name, func in nukeMenu.items():
        nuke.menu('Nuke').addCommand(menuName+ name, func)
    nuke.menu('Nuke').menu(menuName[0:-1]).addSeparator()
    nuke.menu('Nuke').addCommand(menuName+'Rebuild this menu', rebuildMenu)