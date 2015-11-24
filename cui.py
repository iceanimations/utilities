try:
    from uiContainer import uic
except:
    from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os.path as osp
import logging
import tactic_client_lib as tcl
import os
import traceback

rootPath = osp.dirname(__file__)
uiPath = osp.join(rootPath, 'ui')
iconPath = osp.join(rootPath, 'icons')

Form2, Base2 = uic.loadUiType(osp.join(uiPath, 'selectionBox.ui'))
class SelectionBox(Form2, Base2):
    def __init__(self, parent=None, items=None, msg=''):
        '''
        @param items: objects of QCheckbox or QRadioButton
        '''
        super(SelectionBox, self).__init__(parent)
        self.setupUi(self)
        
        self.setMessage(msg)
        self.okButton.clicked.connect(self.ok)
        
        self.selectedItems = []
        self.items = items
        for item in items:
            self.itemsLayout.addWidget(item)
            
    def setCancelToolTip(self, tip):
        self.cancelButton.setToolTip(tip)
        
    def setMessage(self, msg):
        self.msgLabel.setText(msg)
        
    def ok(self):
        if not [item for item in self.items if item.isChecked()]:
            showMessage(self, title='Items Selection',
                        msg='Please select at least one item',
                        icon=QMessageBox.Information)
            return
        self.selectedItems = [item.text() for item in self.items if item.isChecked()]
        self.accept()
        
    def getSelectedItems(self):
        return self.selectedItems

Form1, Base1 = uic.loadUiType(osp.join(uiPath, 'multiSelectComboBox.ui'))
class MultiSelectComboBox(Form1, Base1):
    selectionDone = pyqtSignal(list)
    def __init__(self, parent=None, msg='--Select--'):
        super(MultiSelectComboBox, self).__init__(parent)
        self.setupUi(self)
        
        self.msg = msg
        self.menu = QMenu(self)
        self.menu.setStyleSheet("QMenu { menu-scrollable: 1; }")
        self.button.setMenu(self.menu)
        
        self.menu.hideEvent = self.menuHideEvent
        self.setHintText(self.msg)
        
    def addDefaultWidgets(self):
        button = QPushButton('Invert Selection', self)
        button.clicked.connect(self.invertSelection)
        checkableAction = QWidgetAction(self.menu)
        checkableAction.setDefaultWidget(button)
        self.menu.addAction(checkableAction)
        btn = self.addItem('Select All')
        btn.clicked.connect(lambda: self.toggleAll(btn.isChecked()))
        self.menu.addSeparator()
        
    def invertSelection(self):
        for cBox in self.getWidgetItems():
            cBox.setChecked(not cBox.isChecked())
        self.toggleSelectAllButton()
        
    def toggleAll(self, val):
        for cBox in self.getWidgetItems():
            cBox.setChecked(val)
            
    def toggleSelectAllButton(self):
        flag = True
        for cBox in self.getWidgetItems():
            if not cBox.isChecked():
                flag = False
                break
        for action in self.menu.actions():
            if type(action) == QAction:
                continue
            widget = action.defaultWidget()
            if widget.text() == 'Select All':
                widget.setChecked(flag)
        
    def setHintText(self, text):
        self.button.setText(text)
        
    def menuHideEvent(self, event):
        items = self.getSelectedItems()
        if items:
            s = ''
            if len(items) > 2:
                s = ',...'
            self.button.setText(','.join(items[:2]) + s)
        else:
            self.setHintText(self.msg)
        if event:
            QMenu.hideEvent(self.menu, event)
        self.selectionDone.emit(items)
        
    def getSelectedItems(self):
        return [cBox.text().strip() for cBox in self.getWidgetItems() if cBox.isChecked()]
        
    def getWidgetItems(self):
        return [cBox for cBox in
                [action.defaultWidget() for action in
                 self.menu.actions() if not type(action) is QAction] if cBox.text().strip() != 'Select All' and cBox.text().strip() != 'Invert Selection']
        
    def getItems(self):
        return [cBox.text().strip() for cBox in self.getWidgetItems()]
        
    def addItem(self, item, selected=False):
        checkBox = QCheckBox(item, self.menu)
        if selected:
            checkBox.setChecked(True)
        checkableAction = QWidgetAction(self.menu)
        checkableAction.setDefaultWidget(checkBox)
        self.menu.addAction(checkableAction)
        return checkBox
    
    def appendItems(self, items, selected=None):
        self.addItems(items, selected=selected, clear=False)

    def addItems(self, items, selected=None, clear=True):
        items = sorted(items)
        if clear:
            self.clearItems()
        self.addDefaultWidgets()
        for item in items:
            sel = False
            if selected and item in selected:
                sel = True
            btn = self.addItem(item, sel)
            btn.clicked.connect(self.toggleSelectAllButton)
        if selected:
            self.menuHideEvent(None)

    def clearItems(self):
        self.menu.clear()
        self.setHintText(self.msg)

class MessageBox(QMessageBox):
    def __init__(self, parent=None):
        super(MessageBox, self).__init__(parent)

    def closeEvent(self, event):
        self.deleteLater()

def showMessage(parent, title = 'Shot Export',
                msg = 'Message', btns = QMessageBox.Ok,
                icon = None, ques = None, details = None, **kwargs):

    mBox = MessageBox(parent)
    mBox.setWindowTitle(title)
    mBox.setText(msg)
    if ques:
        mBox.setInformativeText(ques)
    if icon:
        mBox.setIcon(icon)
    if details:
        mBox.setDetailedText(details)
    customButtons = kwargs.get('customButtons')
    mBox.setStandardButtons(btns)
    if customButtons:
        for btn in customButtons:
            mBox.addButton(btn, QMessageBox.AcceptRole)
    pressed = mBox.exec_()
    if customButtons:
        cBtn = mBox.clickedButton()
        if cBtn in customButtons:
            return cBtn
    return pressed


class QTextLogHandler(QObject, logging.Handler):
    appended = pyqtSignal(str)

    def __init__(self, text):
        logging.Handler.__init__(self)
        QObject.__init__(self, parent=text)
        self.text=text
        self.text.setReadOnly(True)
        self.appended.connect(self._appended)
        self.loggers = []

    def __del__(self):
        for logger in self.loggers:
            self.removeLogger(logger)

    def _appended(self, msg):
        self.text.append(msg)
        self.text.repaint()

    def emit(self, record):
        try:
            self.appended.emit(self.format(record))
        except:
            pass

    def addLogger(self, logger=None):
        if logger is None:
            logger = logging.getLogger()
        if logger not in self.loggers:
            self.loggers.append(logger)
            logger.addHandler(self)

    def removeLogger(self, logger):
        if logger in self.loggers:
            self.loggers.remove(logger)
            logger.removeHandler(self)

    def setLevel(self, level, setLoggerLevels=True):
        super(QTextLogHandler, self).setLevel(level)
        if setLoggerLevels:
            for logger in self.loggers:
                logger.setLevel(level)

Form3, Base3 = uic.loadUiType(osp.join(uiPath, 'tacticLogin.ui'))
class TacticLogin(Form3, Base3):
    def __init__(self, parent=None):
        super(TacticLogin, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon(osp.join(iconPath, 'login.png')))
        self.server = None
        
        self.usernameBox.setText(os.environ['USERNAME'])
        
        self.loginButton.clicked.connect(self.login)
        self.cancelButton.clicked.connect(self.reject)
        self.projectBox.activated.connect(self.closeWindow)
        self.passwordBox.setFocus()
        
    def populateProjects(self):
        projs = self.server.eval('@GET(sthpw/project.code)')
        if projs:
            self.projectBox.addItems(projs)
    
    def closeWindow(self):
        if self.projectBox.currentText() == '--Select Project--':
            return
        self.server.set_project(self.projectBox.currentText())
        self.accept()
        
    def login(self):
        username = self.usernameBox.text()
        if not username: return
        password = self.passwordBox.text()
        if not password: return
        try:
            self.server = tcl.TacticServerStub(server='dbserver', login='qurban.ali', password='13490', project='test_mansour_ep')
#             self.server = tcl.TacticServerStub(setup=False)
#             self.server.set_server('dbserver')
#             ticket = self.server.get_ticket(username, password)
#             self.server.set_ticket(ticket)
        except Exception as ex:
            showMessage(self, title='Login Error', msg=str(ex), icon=QMessageBox.Critical)
            traceback.print_exc()
            return
        self.populateProjects()
    
    def getServer(self):
        return self.server
    
class FlowLayout(QLayout):
    '''reimplements QLayout to adjust the elements in the avaible width in the window'''
    def __init__(self, parent=None, margin=0, spacing=-1):
        self.mysuper = super(FlowLayout, self)
        super(FlowLayout, self).__init__(parent)
        self.itemList = []
        self.setContentsMargins(0,0,0,0)

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        self.mysuper.setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.margin(), 2 * self.margin())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        return y + lineHeight - rect.y()

borderColor = '#252525'
flat = '\nborder-style: solid;\nborder-color: '+borderColor+';\nborder-width: 1px;\nborder-radius: 0px;\n'
styleSheet = ('QComboBox {'+ flat +'\nmin-height: 25;\nmin-width: 125}'+
             'QPushButton {'+ flat +'\nheight: 23;\nwidth: 75;\n}\n'+
             'QPushButton:hover, QToolButton:hover {\nbackground-color: #353535;\nborder-style: solid;\nborder-color: #4876FF\n}'+
             'QLineEdit {height: 23;'+ flat +'}\n'
             'QToolButton {'+ flat +'}'+
             'QPlainTextEdit {'+ flat +'}')