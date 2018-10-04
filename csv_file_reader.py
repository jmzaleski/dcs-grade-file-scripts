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

    def read_dict(self):
        "read csv file, returning dict keyed by col_name"
        key_col_number = None
        
        with open(self.fn) as csv_file:
            csv_file_reader = csv.reader(csv_file, delimiter=',', quotechar='|',dialect=csv.excel_tab)
            # squirrel away header line
            list_first_line = next(csv_file_reader)
            
            self.col_headers = list_first_line
            # look for column containing col_name.. that will be the key
            ix=0
            for col_hdr in list_first_line:
                #print(col_hdr)
                if col_hdr == self.col_name: #one we are looking for
                    key_col_number = ix
                    break
                ix += 1
                        
            if not key_col_number:
                print("error: could not find column header", self.col_name, "in first line of file", self.fn);
                exit(2)
                
            #print(key_col_number)
            
            junk_second_line = next(csv_file_reader)

            # here's a stupid thing. quercus has:
            # in header row, Student, ID, SS User ID, SIS Login ID, Section
            # in data row, Student col firstname COMMA last name.. so counts are off
            # 
            key_col_number += 1 #to account for comma in STudent column. doh.

            for l in csv_file_reader:
                self.dict[l[key_col_number]] = l
                
    # def read_groups(self):
    #     groups = {}

    #     #with open(self.fn, 'rb') as group_file:
    #     with open(self.fn) as group_file:
    #         group_file_reader = csv.reader(group_file, delimiter=',', quotechar='|',dialect=csv.excel_tab)

    #         first_line = self.get_skip_first_line()
    #         for list_cdfid_in_group in group_file_reader:
    #             if first_line:
    #                 first_line = False
    #                 continue
    #             team_name=list_cdfid_in_group[0]
                 
    #             # group_cdf_id_list may contain random case CDF ids, empty strings, unmapped students
    #             group_cdf_id_list = list_cdfid_in_group[1:] 
        
    #             #carefully collect the cdfid's for the students in the group, scrubbing it
    #             scrubbed = []
    #             for cdfid in group_cdf_id_list:
    #                 if len(cdfid) == 0:
    #                     continue
    #                 scrubbed.append(cdfid)
    #                 self.msg.verbose(cdfid)
    #             self.msg.debug(team_name, scrubbed)
                
    #             groups[team_name] = scrubbed
    #     return groups
    # skip_first_line = property(get_skip_first_line, set_skip_first_line, del_skip_first_line, "skip_first_line's docstring")
    
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
    
