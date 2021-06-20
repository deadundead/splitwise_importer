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
import requests
import yaml
import os,sys
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
#sys.path.append('./splitwise')
from splitwise import *
from splitwise.user import ExpenseUser
#import iso18245
import pandas
import math
from time import strftime,sleep

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

# main class with Splitwise object
class splitwiseConnector:
    def __init__(self):
        # load config file
        with open(CURR_DIR+'/config.yaml') as f:
            config = yaml.safe_load(f)
            self.config = Struct(**config)
            self.layout = Struct(**self.config.bank_layout)

        # load bank-splitwise category correspondence dictionary
        with open(CURR_DIR+'/mccDic.yaml') as f:
            self.mccDic = yaml.safe_load(f)

        self.sObj = Splitwise(self.config.consumer_key,self.config.consumer_secret,api_key=self.config.api_key)
        
        #['Utilities','Uncategorized','Entertainment','Food and drink','Home','Transportation','Life']
        cats = self.sObj.getCategories()
        self.cats=cats
        # create dict with splitwise category objects and their names
        self.catDic = {}
        for cat in cats:
            for subcat in cat.getSubcategories():
                self.catDic[subcat.name] = subcat

    def parseEntry(self,entry):        
        parsedEntry = Struct()
        parsedEntry.type = entry[self.layout.type_col]
        # identify Expense type
        if parsedEntry.type in self.mccDic:
            # return splitwise category name
            catName = self.mccDic[parsedEntry.type]
        else:
            catName = "General"

        # set category object
        parsedEntry.category = self.catDic[catName]
        # set date
        ts = pandas.to_datetime(entry[self.layout.date_col],dayfirst=True)
        parsedEntry.date = strftime("%d/%m/%Y",ts.timetuple())
        parsedEntry.description = entry[self.layout.comment_col]
        # round cost
        parsedEntry.paid = round(-1.*(entry[self.layout.sum_col]),2)
        return parsedEntry


    def createEqualExpenseFromEntry(self,entry):
        # create an equally split expense
        # entry - pandas.DataFrame or Series object

        parsedEntry = self.parseEntry(entry)

        expense = Expense()
        expense.setCost(parsedEntry.paid)
        expense.setDescription(parsedEntry.description)
        expense.setCategory(parsedEntry.category) 
        expense.setGroupId(self.config.group_id)
        expense.setSplitEqually() 
        expense.setCurrencyCode(self.config.currency_code)
        expense.setDate(parsedEntry.date)

        # calculate equally split share
        members = self.sObj.getGroup(self.config.group_id).getMembers()
        share = round(parsedEntry.paid/len(members),2)
        # account for any rounding errors
        # to prevent errors when total OwedShare is not equal to cost
        mainShare = parsedEntry.paid - (len(members)-1)*share
        
        # add main user (payer)
        user1 = ExpenseUser()
        user1.setId(self.sObj.getCurrentUser().getId())
        user1.setPaidShare(parsedEntry.paid)
        user1.setOwedShare(mainShare)
        users = []
        users.append(user1)

        # add all other users in group
        for i in members:
            if i.getId() != user1.getId():
                user = ExpenseUser()
                user.setId(i.getId())
                user.setPaidShare('0.00')
                user.setOwedShare(share)
                users.append(user)


        expense.setUsers(users)
        expense.setSplitEqually() 
        # create expense on Splitwise and return errors object
        expense, errors = self.sObj.createExpense(expense)
        return errors
    
    # def createEqualExpenseFromEntryDummy(self,entry):
    #     import random
    #     if random.randint(0,1):
    #         error = SplitwiseError("This is a dummy error fo tests")
    #     else:
    #         error = SplitwiseError()
    #     sleep(0.3)
    #     return error
