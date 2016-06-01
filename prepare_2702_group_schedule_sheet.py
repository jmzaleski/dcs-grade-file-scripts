'''
Created on Jun 1, 2016

@author: mzaleski
'''

import matz_utils
from cdf_class_list_reader import CdfClassListFileReader
import group_csv_file_reader


class Prepare2702GroupSchedule_sheet(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        
        
        
if __name__ == "__main__" :
    CLASS_LIST="marks/CSC2702HY"
    MARKUS_GROUP_FILE ="groups/download_grouplist.csv"
    TORID_TO_CDFID_FILE ="marks/utorid_to_cdfid.csv"

    msg = matz_utils.MessagePrinter(True)
    msg.debug("hello from prepare_2702_group_schedule_sheet.py")
    print ("instantiate ClassListFileReader")
    class_list_file_reader = CdfClassListFileReader(CLASS_LIST)
    ls = class_list_file_reader.readLines()
    cdfid_to_name = class_list_file_reader.cdfid_to_name(ls)
    for l in ls:
        rec = class_list_file_reader.parseClassListLine(l)
#         print(rec)
        print("cdfid=", rec.cdfid, "name=", cdfid_to_name[rec.cdfid])
#         print("name", rec.name)
#         print("student_number", rec.student_number)
#         print("email", rec.email)

    toridmap = group_csv_file_reader.GroupFileReader(TORID_TO_CDFID_FILE).read_groups()
    print(toridmap)
    exit(0)
    g = group_csv_file_reader.GroupFileReader(MARKUS_GROUP_FILE).read_groups();
    cdf_to_teamname = {}
    cdfid_in_groups = {} #check for typos in group file
    # seems that markus has second column that repeats group name??
    for team_name in g.keys():
        member_string = ""
        for cdfid in g[team_name]:
            print(cdfid)
            if not cdfid in cdfid_to_name:
                continue
            cdfid_in_groups[cdfid] = cdfid
            cdf_to_teamname[cdfid] = team_name
            member_string += cdfid_to_name[cdfid] 
            member_string += ", "
            print(member_string)
        print("%s %s" %( team_name, member_string))
            #print(cdfid, cdfid_to_name[cdfid])
#     print(g)
#     print(cdfid_in_groups)
#     print(cdf_to_teamname)