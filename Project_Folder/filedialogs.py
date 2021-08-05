""" 
Supplies NewTimesheetDialog and TimesheetsFileDialog (the base class for 
OpenTimesheetDialog and DeleteTimesheetDialog).
"""

from PyQt5.QtWidgets import (QAbstractItemView, QDialog, QDialogButtonBox, 
                             QListWidget, QListWidgetItem, QMessageBox, 
                             QVBoxLayout)
from metaclass import QtABCMeta
from configdialogs import ConfigDataDialog
import os
import re
from abc import abstractmethod
import subprocess

datapath = os.path.join(os.path.expanduser('~'), '.timesheetproject')


class NewTimesheetDialog(ConfigDataDialog):
    
    def okClicked(self):
        """ Make new timesheet."""
        
        valid = True
        
        # raise errors if name, rate or currency are empty, or if name already
        # exists
        # check name...
        name = self.nameEdit.text().strip()
        name = re.sub('\s', '_', name)
        if name:
            # if there is already a timesheet with this name, raise an error
            if not self.check_name(name):
                self.name_error(name)
                valid = False
            # needs name attribute, so that timesheet can make the data object
            # and read the csv
            self.name = name
        else:
            self.error_message('name')
            valid = False
            
        # check rate...
        rate = self.rateEdit.text().strip()
        if not rate:
            self.error_message('rate of pay')
            valid = False
            
        # check currency...
        curr = self.currencyEdit.text().strip()
        if not curr:
            self.error_message('currency')
            valid = False
            
        # get time base
        if self.dayButton.isChecked():
            timebase = 'day'
        else:
            timebase = 'hour'
            
        if valid:
            path = os.path.join(datapath, name)
            
            try:
                # if name does not already exist, make csv and config files
                os.mkdir(path)
                
                base = 'ts_' + name.lower()
                
                self.new_csv  = os.path.join(path, base+'.csv')
                self.new_conf = os.path.join(path, base+'.conf')
                
                with open(self.new_csv, 'w') as fileobj:
                    fileobj.write('Date,Duration,Activity,Rate\n')
                    
                with open(self.new_conf, 'w') as fileobj:
                    text = ('name={}\nrate={}\ncurrency={}\ntimebase={}\n'
                            .format(name, rate, curr, timebase))
                    fileobj.write(text)
            
                self.accept()
                
            except FileExistsError:
                # if name is already taken, get user to enter another one
                self.name_error()
                # and reset dialog
                self.initUI()
        
    
class TimesheetsFileDialog(QDialog, metaclass=QtABCMeta):
    
    def __init__(self):
        """ Dialog to select timesheet(s). """
        super().__init__()
        
        self.initUI()
        
    def initUI(self):
        
        # get list of timesheets from names of directories
        timesheets = list(file for file in os.listdir(datapath) 
                     if os.path.isdir(os.path.join(datapath, file)))
        
        if len(timesheets) == 0:
            self.none_message()
            self.reject()
            self.close()
            
        else:
            # make list where only one thing can be selected
            self.timesheetList = QListWidget()
#            self.timesheetList.setSelectionMode(QAbstractItemView.SingleSelection)
            # double click or 'OK' button select that timesheet
            self.timesheetList.itemDoubleClicked.connect(self.get_selected)
            
            listWidgetItems = []
            
            # set the text in the list
            for timesheet in timesheets:
                item = QListWidgetItem(self.timesheetList)
                item.setText(timesheet)
                listWidgetItems.append(item)
                
            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | 
                                         QDialogButtonBox.Cancel)
    
            buttonBox.accepted.connect(self.get_selected)
            buttonBox.rejected.connect(self.reject)
                
            layout = QVBoxLayout()
            layout.addWidget(self.timesheetList)
            layout.addWidget(buttonBox)
            
            self.setLayout(layout)
            
    @abstractmethod
    def get_selected(self): pass
        
    def none_message(self):
        title = 'No timesheets available!'
        message = 'There are no timesheets to show! Go and make one!'
        QMessageBox.warning(self, title, message)
        
        
class OpenTimesheetDialog(TimesheetsFileDialog):
    
    def __init__(self):
        """ Dialog to open a timesheet. """
        super().__init__()
        self.setWindowTitle('Open a timesheet')
        
        self.timesheetList.setSelectionMode(QAbstractItemView.SingleSelection)
    
    def get_selected(self):
        self.selected = self.timesheetList.selectedItems()[0].text()
        self.accept()
        
    
class DeleteTimesheetDialog(TimesheetsFileDialog):
    
    def __init__(self):
        """ Dialog to delete timesheet(s). """
        super().__init__()
        self.setWindowTitle('Delete timesheet(s)')
        self.timesheetList.setSelectionMode(QAbstractItemView.ExtendedSelection)
    
    def get_selected(self):
        self.selected = self.timesheetList.selectedItems()
        self.selected = list(item.text() for item in self.selected)
        self.confirm_message()
            
    def confirm_message(self):
        
        title = 'Confirm delete'
        message = 'This action will irreversibly delete:\n'
        for item in self.selected:
            message += '    - ' + item + '\n'
        message += 'Confirm deletion?'
        
        ret = QMessageBox.question(self, title, message)
        
        if ret == QMessageBox.Yes:
            # delete the directory for each
            for item in self.selected:
                # escape any spaces in name
                item = re.sub(' ', '\ ', item)
                path = os.path.join(datapath, item)
                subprocess.run(["rm", "-r", path])
                self.accept()

        if ret == QMessageBox.No:
            self.reject()
            
