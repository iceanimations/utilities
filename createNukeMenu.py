import sip
sip.setapi('QString', 2)
import nuke
from nukeMenuCommands import *

# add new script to the following dict
# key => name of the script that will appear in the nuke under ICE Scripts menu
# value => name of the function to be called when user clicks that menu item
# finally create that function in the nukeMenuCommands.py

nukeMenu = {
            'Replace Read Paths': replaceReadPaths,
            'Red To Default': fromRedToDefault,
            'Render Write (One by One)': renderWrites
            }

def create():
    for name, func in nukeMenu.items():
        nuke.menu('Nuke').addCommand('ICE Scripts/'+ name, func)