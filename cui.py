try:
    from uiContainer import uic
except:
    from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os.path as osp
import logging

rootPath = osp.dirname(__file__)
uiPath = osp.join(rootPath, 'ui')

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

