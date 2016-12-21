import logging
import re
import site
import sys

uic = None
sip = None

def setUicLoggingLevel(uic, level=logging.INFO):
    for uic_subm in ['.properties', '.uiparser']:
        logger = logging.getLogger(uic.__name__ + uic_subm)
        logger.setLevel(level)

def setSipApiVersion(sip, version=2):
    API_NAMES = ["QDate", "QDateTime", "QString", "QTextStream", "QTime",
            "QUrl", "QVariant"]
    API_VERSION = version
    for name in API_NAMES:
        sip.setapi(name, API_VERSION)

def setPyQt4():
    global uic, sip

    from PyQt4 import uic
    import sip

    setUicLoggingLevel(uic)
    setSipApiVersion(sip)

def setPySide():
    global uic, sip

    import PySide as PyQt4
    import PySide.QtCore as QtCore
    import uiLoader
    import pysideuic as uic
    import shiboken as sip

    QtCore.pyqtSignal = QtCore.Signal
    QtCore.pyqtSlot = QtCore.Slot
    uic.loadUiType = uiLoader.loadUiType
    sip.wrapinstance = sip.wrapInstance
    setUicLoggingLevel(uic)

    sys.modules["PyQt4"] = PyQt4
    sys.modules["PyQt4.QtCore"] = QtCore
    sys.modules["sip"] = sip
    sys.modules["PyQt4.uic"] = uic

def _setPySide():
    try:
        setPySide()
    except ImportError:
        print 'cant set pyside'
        setPyQt4()

try:
    import pymel.core as pc
    version = int(re.search('\\d{4}', pc.about(v=True)).group())
    if version in range(2011, 2016):
        site.addsitedir(r"R:\Python_Scripts\maya"+str(version)+r"\PyQt")
        setPyQt4()
    else:
        _setPySide()
except ImportError:
    _setPySide()
