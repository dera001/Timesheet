"""
Base class for NewTimesheetDialog and EditTimesheetSettingsDialog.

Also provides QDialog_CTRL_Q base class.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QAction,  QDialog, QDialogButtonBox, QGridLayout, 
                             QLabel, QLineEdit, QMessageBox, QRadioButton,  
                             QVBoxLayout)
from metaclass import QtABCMeta
import os
import re
from abc import abstractmethod

datapath = os.path.join(os.path.expanduser('~'), '.timesheetproject')


class QDialog_CTRL_Q(QDialog):
    """ QDialog subclass with CRTL+Q shortcut to close window.
    
        Standard QDialog close shortcut is ESC, which still applies here.
    """
    
    def __init__(self):
        
        super().__init__()
        
        self.exitAct = QAction("E&xit", self, 
                               shortcut="CTRL+Q",
                               statusTip="Exit the application", 
                               triggered=self.close)
        self.addAction(self.exitAct)
        

class ConfigDataDialog(QDialog_CTRL_Q, metaclass=QtABCMeta):
    
    def __init__(self, data=None):
        """ Set values that appear in the config file.
        
            Parameters
            ----------
            data : Data object, optional
                object which holds all the csv data. If no data object exists
                yet, data=None
        """
        super().__init__()
        
        self.initUI(data)
        
        
    def initUI(self, data):
        
        self.data = data
        
        # timesheet name
        nameLabel = QLabel('Employee name:')
        self.nameEdit = QLineEdit(self)
        
        # rate of pay
        rateLabel = QLabel('Default rate of pay:')
        rateLabel.setAlignment(Qt.AlignRight)
        self.rateEdit = QLineEdit(self)
        self.rateEdit.selectAll()
        
        # time base
        timeLabel = QLabel('per')
        self.dayButton = QRadioButton('day')
        self.hourButton = QRadioButton('hour')
        
        radioLayout = QVBoxLayout()
        radioLayout.addWidget(self.dayButton)
        radioLayout.addWidget(self.hourButton)
        
        # currency
        currencyLabel = QLabel('Currency:')
        currencyLabel.setAlignment(Qt.AlignRight)
        self.currencyEdit = QLineEdit(self)
        
        # if we have a data object, set text
        if self.data:
            self.nameEdit.setText(self.data.name)
            self.rateEdit.setText(self.data.rate)
            self.currencyEdit.setText(self.data.currency)
        # if timebase is already set, check the right button
        if self.data and self.data.timebase == 'hour':
            self.hourButton.setChecked(True)
        # else, default to day
        else:
            self.dayButton.setChecked(True)
        
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | 
                                     QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.okClicked)
        buttonBox.rejected.connect(self.reject)

        editLayout = QGridLayout()
        
        row = 0
        editLayout.addWidget(nameLabel, row, 0)
        editLayout.addWidget(self.nameEdit, row, 1)
        
        row += 1
        editLayout.addWidget(rateLabel, row, 0)
        editLayout.addWidget(self.rateEdit, row, 1)
        editLayout.addWidget(timeLabel, row, 2)
        editLayout.addLayout(radioLayout, row, 3)
        
        row += 1
        editLayout.addWidget(currencyLabel, row, 0)
        editLayout.addWidget(self.currencyEdit, row, 1)
        
        layout = QVBoxLayout()
        layout.addLayout(editLayout)
        layout.addWidget(buttonBox)
 
        self.setLayout(layout)
        
        self.setWindowTitle('Edit timesheet settings')
        
        
    @abstractmethod     
    def okClicked(self): pass

    def check_name(self, name):
        # if name has been changed, check if it is valid
        if True:
            name = re.sub('\s', '_', name)
            path = os.path.join(datapath, name)
            if os.path.exists(path):
                return False
        return True
        
    def error_message(self, which):
        title = 'No {} provided!'.format(which)
        message = 'Please provide a {} for the new timesheet.'.format(which)
        QMessageBox.warning(self, title, message)
        
    def name_error(self, name):
        title = 'Timesheet already exists!'
        message = '''There is already a timesheet called "{}". Please provide 
another name.'''.format(name)
        QMessageBox.critical(self, title, message)
        
