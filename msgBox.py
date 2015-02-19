from PyQt4.QtGui import QMessageBox

class MessageBox(QMessageBox):
    def __init__(self, parent=None):
        super(MessageBox, self).__init__(parent)

    def closeEvent(self, event):
        self.deleteLater()

    def hideEvent(self, event):
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