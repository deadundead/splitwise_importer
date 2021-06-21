#    splitwise_importer - a simple TUI program to export your bank log to Splitwise
#    Copyright (C) 2021  Dmitry Frolov
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#   DISCLAIMER: 
#   This is not an official API. All the trademarks and copyright belongs to Splitwise.com

#!/usr/bin/env python3
import os,sys
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,CURR_DIR+'/npyscreen')
import npyscreen
import pandas
import yaml
#from splitwise import *
from auth import splitwiseConnector
from math import floor

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class App(npyscreen.StandardApp):
    def onStart(self):
        self.addForm("MAIN", MainForm, name="Splitwise Importer")

class LogBox(npyscreen.BoxTitle):
    # TitleBufferPager теперь будет окружен боксом
    _contained_widget = npyscreen.BufferPager

class MainForm(npyscreen.ActionForm):
    def create(self):

        with open(CURR_DIR+'/config.yaml') as f:
            config = yaml.safe_load(f)
            self.config = Struct(**config)
            self.layout = Struct(**config['bank_layout'])    
        
        new_handlers = {
        # Set Ctrl+q for exit
           "^Q": self.exit_func,
           #"^s" : self.save_func
        }
        self.add_handlers(new_handlers)
        
        file = npyscreen.selectFile('./',)
    
        y, x = self.useable_space()
        # create a MultiSelect form with entris from the database 
        self.indices = self.add(npyscreen.TitleMultiSelect, name="Pick entries to send", values=self.load_data(file),max_height=-5, scroll_exit=True)
        # display status of messages
        self.box = self.add(LogBox,name='log',width=x-20,scroll_exit=True)
        self.pager = self.box.entry_widget
        self.pager.buffer([" Wating for selection"])

    #def event_value_edited(self, event):
    #    self.pager.display()
    def load_data(self,file):
        # read csv file
        self.csvfile = pandas.read_csv(file,encoding='windows-1251',lineterminator='\n',delimiter=';',decimal=',')
        
        if self.layout.negative_payments:
            # sort only negative operations
            self.csvfile = self.csvfile[self.csvfile.iloc[:,self.layout.sum_col]<0]
            entries = self.csvfile.copy()
        else:
            # sort only postive operations
            self.csvfile = self.csvfile[self.csvfile.iloc[:,self.layout.sum_col]>0]
            entries = self.csvfile.copy()
        # cut long strings
        maxChars = 17
        for col in entries.select_dtypes(include=[object]):
            entries[col] = entries[col].str.slice(0, maxChars)
        # get number of elements 
        numel = self.csvfile.shape[0]  
        # set list of column numbers
        columns = [self.layout.date_col, self.layout.status_col, self.layout.sum_col, self.layout.type_col, self.layout.comment_col]
        # set multiselect values
        vals = [entries.iloc[i,columns].to_string(index=False) for i in range(0,numel)]
        return vals

    def on_ok(self):
        self.sender_func()

    def on_cancel(self):
        self.parentApp.setNextForm(None)
        self.exit_func 

    def sender_func(self):
        sc = splitwiseConnector()
        # for every value chosen create expense
        counter = 0;
        # logging
        self.pager.buffer(["total entries: "+str(len(self.indices.value))])
        for i in self.indices.value:
            entry = self.csvfile.iloc[i,:]
            errors = sc.createEqualExpenseFromEntry(entry)
            # logging
            try:
                self.pager.buffer([str(counter)+" "+str(errors.getErrors())])
            except:
                self.pager.buffer([str(counter)+" "+"OK"])
            counter += 1
            self.pager.display()
        self.pager.buffer(["press ctrl+q to exit"])
        self.pager.buffer(["\n"])
        self.pager.display()
    
    def exit_func(self, _input):
        exit(0)

if __name__ == '__main__':             
    MyApp = App()
    MyApp.run()