#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QAction, QApplication, QDesktopWidget, 
                             QFileDialog, QMainWindow, QMessageBox, QTextEdit)

from editdialogs import (AddLineDialog, EditTimesheetSettingsDialog,
                         RemoveLineDialog, EditLineDialog)
from filedialogs import (NewTimesheetDialog, OpenTimesheetDialog, 
                         DeleteTimesheetDialog)
#from configdialogs import ConfigDataDialog
from processcsv import csv_to_html
from readconfig import ConfigParser
import re

datapath = os.path.join(os.path.expanduser('~'), '.timesheetproject')
conffile = os.path.join(datapath, 'timesheetproject.conf')

# make sure the .timesheetproject directory and config file exist
def check_path():
    if not os.path.exists(datapath):
        os.mkdir(datapath)
        with open(conffile, 'w') as fileobj:
            fileobj.write('last=None\n')


class Data:
    # separate class to handle all the data
    
    def __init__(self, project_name):
        """ Object that controls the csv (and config) data. """
        
        self.modified = False
        
        if project_name is None:
            self.csv_data = ''
            self.name = 'None'
            self.rate = ''
            self.currency = ''
            self.timebase = ''
                       
        else:            
            self.csvfile, self.conffile = self.getCsvConfFiles(project_name)
            
            with open(self.csvfile) as fileobj:
                self.csv_data = fileobj.read()
                
                
            self.cfg = ConfigParser(self.conffile)
                
            conf_data = self.cfg.read_conf()
            
            # if conf_data is not empty...
            self.name = conf_data['name']
            self.rate = conf_data['rate']
            # 'currency' and 'timebase' are a new features, so attempting to
            # read them from the config will fail first time for old versions
            # In that case, set it to defaults; user can change them, if 
            # necessary, and add them to the config file
            try:
                self.currency = conf_data['currency']
            except KeyError:
                self.currency = '£'
                self.cfg.update_conf('currency', self.currency)
            try:
                self.timebase = conf_data['timebase']
            except KeyError:
                self.timebase = 'hour'
                self.cfg.update_conf('timebase', self.timebase)
                
                
    @staticmethod
    def getCsvConfFiles(project_name):
        path = os.path.join(datapath, project_name)
        file = 'ts_' + project_name.lower()
        exts = ('.csv', '.conf')
        csvfile, conffile = (os.path.join(path, file+ext) for ext in exts)
        return csvfile, conffile
            
        
    def add_new(self, new_data):
        """ Add new line to csv. """
        self.csv_data += new_data
        self.modified = True
        
    def save(self):
        # save csv file
        if self.modified:
            with open(self.csvfile, 'w') as fileobj:
                fileobj.write(self.csv_data)
        return True
    
    
    def new_name(self, value):
        """ Set new timesheet name. """
        
        value = re.sub('\s', '_', str(value))
        
        # rename directory in .timesheetproject
        current_path = os.path.join(datapath, self.name)
        new_path = os.path.join(datapath, value)
        os.rename(current_path, new_path)
        
        # store new name variable
        self.name = value
        
        # store and update file names
        current_files = (self.csvfile, self.conffile)
        new_files = self.getCsvConfFiles(self.name)
        
        # rename the csv and conffiles
        for n in range(len(current_files)):
            file = current_files[n]
            new = new_files[n]
            _, current = os.path.split(file)
            current = os.path.join(new_path, current)
            os.rename(current, new)
            
        # store new file names
        self.csvfile, self.conffile = new_files
        
        # set new path for cfg
        self.cfg.setFilename(self.conffile)
        # update config data
        self.cfg.update_conf('name', self.name)

            
    def new_rate(self, value):
        """ Set new rate of pay. """
        # set new rate and update config file
        self.rate = str(value)
        self.cfg.update_conf('rate', str(value))
        
    def new_currency(self, value):
        """ Set new currency. """
        # set new currency and update config file
        self.currency = str(value)
        self.cfg.update_conf('currency', str(value))
        
    def new_timebase(self, value):
        """ Set new timebase. """
        # set new timebase and update config file
        self.timebase = str(value)
        self.cfg.update_conf('timebase', str(value))
    
    
class Timesheetproject(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):
        
        # make sure the TimeSheet directory and config file exist
        check_path()

        # display last opened file
        self.get_last_opened()
            
        # get timesheet name
        self.name = None #self.data.name

        self.textEdit = QTextEdit(readOnly=True)
        
        # display text (as html)
        self.update_display()

        self.setCentralWidget(self.textEdit)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        
        self.statusBar()
        self.statTimeout = 1000
        self.setStyleSheet("background-color: yellow;")
        self.setWindowIcon(QIcon(''))  
        self.resize(400, 500)
        self.centre()
        
        self.show()
        
        
    def centre(self):
        """ Centre window on screen. """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        
    def get_last_opened(self):
        """ Get name of last timesheet worked on. """
        
        self.cfg_last = ConfigParser(conffile)
        
        try:
            conf_data = self.cfg_last.read_conf()
            previous = conf_data['last']
            if previous == 'None':
                previous = None
            
        except FileNotFoundError:
            previous = None
            self.cfg_last.make_conf()
        
        self.data = Data(previous)
            
        
    def update_display(self):
        """ Update text and window title """
        # check if name has changed
        self.updateName()
        # update text displayed
        self.textEdit.setHtml(csv_to_html(self.data.csv_data, 
                                          self.data.timebase,
                                          self.data.currency))
        self.setWindowTitle('Employee Timesheet - ' + self.name)
        if self.data.modified:
            self.statusBar().showMessage('Updated', self.statTimeout)
            
            
    def updateName(self):
        if self.name != self.data.name:
            self.name = self.data.name

    def newTimesheet(self):
        """ Make a new timesheet. """
        
        # prompt save
        self.maybeSave()
        
        self.ntd = NewTimesheetDialog()
        self.ntd.show()
        self.ntd.accepted.connect(self.setTimesheet)
        
    def setTimesheet(self):
        """ Set name (internally), make new Data object and display data. """
        self.name = self.ntd.name
        self.data = Data(self.name)
        self.update_display()
        
    def addLine(self):
        """ Add line(s) to timesheet. """
        self.ald = AddLineDialog(self.data)
        self.ald.show()
        self.ald.accepted.connect(self.update_display)
        
    def removeLine(self):
        """ Remove line(s) from timesheet. """
        self.rld = RemoveLineDialog(self.data)
        self.rld.show()
        self.rld.accepted.connect(self.update_display)
            
    def editEntries(self):
        self.ed = EditLineDialog(self.data)
        self.ed.show()
        self.ed.accepted.connect(self.update_display)
        
    def open(self):
        """ Open another timesheet. """
        self.otd = OpenTimesheetDialog()
        self.otd.show()
        self.otd.accepted.connect(self.setOpenVars)
        
    def setOpenVars(self):
        """ Set parameters for this timesheet. """
        
        # this is basically the same as setTimesheet, but with different object
        # to get name from
        self.name = self.otd.selected
        self.data = Data(self.name)
        self.update_display()


    def save(self):
        # use Data's save method
        if self.data.save():
            self.statusBar().showMessage('Saved', self.statTimeout)
            
    def closeEvent(self, event):
        # save the timesheet, save the name of this timesheet to the cache and
        # close the window
        self.save()
        self.cfg_last.update_conf('last', self.name)
        event.accept()

    def export(self):
        """ Write the csv data to a file of the user's choice. """
        filename, _ = QFileDialog.getSaveFileName(self, 
                     'Export timesheet as csv', os.getcwd(), 
                     'CSV Files (*.csv);;Text Files (*.txt);;All Files (*)')
        if filename:
            self.save()
            with open(filename, 'w') as fileobj:
                fileobj.write(self.data.csv_data)
                
    def deleteTimesheet(self):
        """ Delete a timesheet """
        self.dtd = DeleteTimesheetDialog()
        self.dtd.show()
        self.dtd.accepted.connect(self.reset)
        
    def reset(self):
        if self.name in self.dtd.selected:
            self.data = Data(None)
            self.name = self.data.name
            self.cfg_last.update_conf('last', self.name)
            self.update_display()

    def about(self):
        QMessageBox.about(self, "About Employee Timesheet",
                          "Create and manage employee timesheets with ease.\n"
                          "See README for more details.")
           
    def editSettings(self):
        """ Change timesheet config data """
        self.nrd = EditTimesheetSettingsDialog(self.data)
        self.nrd.show()
        self.nrd.accepted.connect(self.update_display)
    
    def createActions(self):
                    
        self.newAct = QAction(QIcon.fromTheme('document-new'), "New", self,
                shortcut=QKeySequence.New, statusTip="Create a new timesheet",
                triggered=self.newTimesheet)

        self.openAct = QAction(QIcon.fromTheme('document-open'), "&Open...",
                self, shortcut=QKeySequence.Open,
                statusTip="Open an existing timesheet", triggered=self.open)

        self.saveAct = QAction(QIcon.fromTheme('document-save'), "&Save", self,
                shortcut=QKeySequence.Save,
                statusTip="Save the timesheet", triggered=self.save)

        self.exportAct = QAction("&Export csv", self, shortcut="Ctrl+E",
                statusTip="Export the timesheet as csv",
                triggered=self.export)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                statusTip="Exit the application", triggered=self.close)

        self.aboutAct = QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)
        
        self.addAct = QAction(QIcon.fromTheme('list-add'), "Add", self,
                shortcut=QKeySequence("N"), statusTip="Add new entries",
                triggered=self.addLine)
        
        self.removeAct = QAction(QIcon.fromTheme('list-remove'), 
                "Remove", self, shortcut=QKeySequence("C"), 
                statusTip="Remove entries", triggered=self.removeLine)
        
        self.editAct = QAction(QIcon.fromTheme(''), "Edit", self,
                shortcut=QKeySequence("E"), statusTip="Edit entries",
                triggered=self.editEntries)
        
        self.editSettingsAct = QAction(QIcon.fromTheme('preferences-system'), 
                "Edit settings", self, shortcut="Ctrl+P", 
                statusTip="Set timesheet name, rate of pay and time base", 
                triggered=self.editSettings)
        
        self.deleteAct = QAction("Delete", self,
                shortcut="Ctrl+D", statusTip="Delete timesheet",
                triggered=self.deleteTimesheet)


    def createMenus(self):
        
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.exportAct)
        self.fileMenu.addAction(self.deleteAct)
        self.fileMenu.addAction(self.editSettingsAct)
        self.fileMenu.addSeparator();
        self.fileMenu.addAction(self.exitAct)
        
        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.addAct)
        self.editMenu.addAction(self.removeAct)
        self.editMenu.addAction(self.editAct)
        
        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)

    def createToolBars(self):
        
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.saveAct)
        self.fileToolBar.addAction(self.editSettingsAct)
        
        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.addAction(self.addAct)
        


    def maybeSave(self):
        if self.data.modified:
            ret = QMessageBox.warning(self, "Application",
                    "This timesheet has been modified.\nDo you want to save "
                    "your changes?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
    
            if ret == QMessageBox.Save:
                return self.save()
    
            if ret == QMessageBox.Cancel:
                return False

        return True
    

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    window = Timesheetproject()
    sys.exit(app.exec_())
