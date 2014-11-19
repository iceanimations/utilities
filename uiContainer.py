import pymel.core as pc
import re
import site
import sys
import logging

version = int(re.search('\\d{4}', pc.about(v=True)).group())
if version > 2013:
    import PySide as PyQt4
    sys.modules["PyQt4"] = PyQt4
    import uiLoader
    import pysideuic as uic
    uic.loadUiType = uiLoader.loadUiType
    import shiboken as sip
    sip.wrapinstance = sip.wrapInstance
else:
    site.addsitedir(r"R:\Python_Scripts\maya"+str(version)+r"\PyQt")
    from PyQt4 import uic
    import sip

sys.modules['sip'] = sip

for uic_subm in ['.properties', '.uiparser']:
    logger = logging.getLogger(uic.__name__ + uic_subm)
    logger.setLevel(logging.INFO)

from PyQt4.QtGui import QMessageBox

def showMessage(parent, title = 'Shot Export',
                msg = 'Message', btns = QMessageBox.Ok,
                icon = None, ques = None, details = None):

    if msg:
        mBox = QMessageBox(parent)
        mBox.setWindowTitle(title)
        mBox.setText(msg)
        if ques:
            mBox.setInformativeText(ques)
        if icon:
            mBox.setIcon(icon)
        if details:
            mBox.setDetailedText(details)
        mBox.setStandardButtons(btns)
        mBox.closeEvent = lambda event: mBox.deleteLater()
        buttonPressed = mBox.exec_()
        return buttonPressed
