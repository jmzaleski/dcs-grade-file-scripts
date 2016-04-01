'''
Created on Apr 1, 2016

@author: mzaleski
'''

import csv
import matz_utils

class GroupFileReader:
    '''
    read a csv file listing the CDFID of students in each group
    '''


    def __init__(self, fn):
        '''
        given lines like:
        1,g2lev,g2lee,c6jashib,g2mark,g3hummus,g3shiv,g3jonmp
        read them up into a list of lists 
        '''
        self.msg = matz_utils.MessagePrinter(False)
        self.msg.setPrefix("GroupFileReader")
        self.fn = fn
        
    def read_groups(self):
        groups = {}
        first_line = True
        with open(self.fn, 'rb') as group_file:
            group_file_reader = csv.reader(group_file, delimiter=',', quotechar='|',dialect=csv.excel_tab)

            first_line = True
            for list_cdfid_in_group in group_file_reader:
                if first_line:
                    first_line = False
                    continue
                team_name=list_cdfid_in_group[0]
                 
                # group_cdf_id_list may contain random case CDF ids, empty strings, unmapped students
                group_cdf_id_list = list_cdfid_in_group[1:] 
        
                 #carefully collect the cdfid's for the students in the group, scrubbing it
                scrubbed = []
                for cdfid in group_cdf_id_list:
                    if len(cdfid) == 0:
                         continue
                    scrubbed.append(cdfid)
                    self.msg.verbose(cdfid)
                self.msg.debug(team_name, scrubbed)
                
                groups[team_name] = scrubbed
        return groups
