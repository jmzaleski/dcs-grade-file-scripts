'''
Created on Apr 1, 2016

@author: mzaleski
'''

import csv
import matz_utils

class CsvFileToDictionaryReader:
    '''
    read a csv file creating a dictionary where first column is key and remaining columns are a list
    '''
    def __init__(self, fn,key_col_name):
        '''
        given lines like:
        1,g2lev,g2lee,c6jashib,g2mark,g3hummus,g3shiv,g3jonmp
        read them up into a list of lists 
        '''
        self.msg = matz_utils.MessagePrinter(False)
        self.msg.setPrefix("CsvFileToDictionaryReader")
        self.fn = fn
        self.col_name = key_col_name
        self.col_headers = None
        self.dict = {}

    # this OO idiom isn't helping.
    # challenge is how to return the col headers and the dict at the same time from a functional interface.
    # (I guess we could return a tuple. I'm not sure if these are a good idea or not yet)
    
    def read_dict(self):
        "read csv file, returning dict keyed by col_name"
        key_col_number = None
        
        with open(self.fn) as csv_file:
            csv_file_reader = csv.reader(csv_file, delimiter=',', quotechar='"',dialect=csv.excel_tab)

            # squirrel away lines containing column headers and mysterious second line
            self.col_headers = next(csv_file_reader)
            self.line2 = next(csv_file_reader)
            key_col_number = self.col_headers.index(self.col_name) #throws if not found

            def acc(d, item):
                d[item[key_col_number]] = item
                return d
                
            import functools
            self.dict = functools.reduce(acc, csv_file_reader, {})
            return self.dict            
            
if __name__ == "__main__" :
    msg = matz_utils.MessagePrinter(True)
    msg.debug("hello from group_scs_file_reader.py")
    #print ("instantiate ClassListFileReader")
#     me = CdfClassListFileReader("CSC2702HY")
#     ls = me.readLines()
#     cdfid_to_name = me.cdfid_to_name(ls)
#     for l in ls:
#         rec = me.parseClassListLine(l)
#         print(rec)
#         print("cdfid", rec.cdfid)
#         print("name", rec.name)
#         print("student_number", rec.student_number)
#         print("email", rec.email)
    MARKUS_GROUP_FILE ="download_grouplist.csv"
    me = CsvFileToDictionaryReader(MARKUS_GROUP_FILE)
    g = me.read_dict();
    
    cdf_to_teamname = {}
    cdfid_in_groups = {} #check for typos in group file
    for team_name in g.keys():
        team = g[team_name]
        for cdfid in team:
            cdfid_in_groups[cdfid] = cdfid
            cdf_to_teamname[cdfid] = team_name
    print(g)
    print(cdfid_in_groups)
    print(cdf_to_teamname)
    
