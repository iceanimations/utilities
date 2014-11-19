import pymel.core as pc
import re
import site
import sys
import logging

version = int(re.search('\\d{4}', pc.about(v=True)).group())
if version == 2014:
    import PySide as PyQt4
    sys.modules["PyQt4"] = PyQt4
    import uiLoader
    import pysideuic as uic
    uic.loadUiType = uiLoader.loadUiType
    import shiboken as sip
    sip.wrapinstance = sip.wrapInstance
    sys.modules['sip'] = sip
else:
    site.addsitedir(r"R:\Python_Scripts\maya"+str(version)+r"\PyQt")
    from PyQt4 import uic

for uic_subm in ['.properties', '.uiparser']:
    logger = logging.getLogger(uic.__name__ + uic_subm)
    logger.setLevel(logging.INFO)