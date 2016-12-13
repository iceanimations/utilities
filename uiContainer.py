import re
import site
import sys
import logging

uic = None
sip = None

def setUicLoggingLevel(level=logging.INFO):
    for uic_subm in ['.properties', '.uiparser']:
        logger = logging.getLogger(uic.__name__ + uic_subm)
        logger.setLevel(level)

def setPyQt4():
    global uic, sip
    from PyQt4 import uic
    import sip
    setUicLoggingLevel()
    setSipApiVersion()

def setPySide():
    global uic
    import PySide as PyQt4
    PyQt4.QtCore.pyqtSignal = PyQt4.QtCore.Signal
    PyQt4.QtCore.pyqtSlot = PyQt4.QtCore.Slot
    import uiLoader
    import pysideuic as uic
    setUicLoggingLevel()
    uic.loadUiType = uiLoader.loadUiType
    import shiboken as sip
    sip.wrapinstance = sip.wrapInstance
    sys.modules["PyQt4"] = PyQt4
    sys.modules['sip'] = sip

def setSipApiVersion(version=2):
    API_NAMES = ["QDate", "QDateTime", "QString", "QTextStream", "QTime",
            "QUrl", "QVariant"]
    API_VERSION = 2
    for name in API_NAMES:
        sip.setapi(name, API_VERSION)

try:
    import pymel.core as pc
    version = int(re.search('\\d{4}', pc.about(v=True)).group())
    if version in range(2011, 2016):
        site.addsitedir(r"R:\Python_Scripts\maya"+str(version)+r"\PyQt")
        setPyQt4()
    else:
        setPySide()
except ImportError:
    try:
        setPySide()
    except ImportError:
        setPyQt4()
