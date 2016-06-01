'''
Created on Jun 1, 2016

@author: mzaleski
print out cdf to group map
'''

import matz_utils
from cdf_class_list_reader import CdfClassListFileReader
import csv_file_reader

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

    class_list_file_reader = CdfClassListFileReader(CLASS_LIST)
    ls = class_list_file_reader.readLines()
    cdfid_to_name = class_list_file_reader.cdfid_to_name(ls)

    toridmap = csv_file_reader.CsvFileToDictionaryReader(TORID_TO_CDFID_FILE).read_groups()

    torid_to_cdfid_map = {}
    for torid in toridmap.keys():
        torid_to_cdfid_map[torid] = toridmap[torid][1] 

    print("torid_to_cdfid:")
    for torid in torid_to_cdfid_map:
        print( "%s,%s" % (torid,torid_to_cdfid_map[torid]))

    r = csv_file_reader.CsvFileToDictionaryReader(MARKUS_GROUP_FILE)
    r.set_skip_first_line(False)
    g = r.read_groups();
    cdf_to_teamname = {}
    cdfid_in_groups = {} #check for typos in group file
    # seems that markus has second column that repeats group name??

    for team_name in g.keys():
        for torid in g[team_name]:
            #skip werido markus thing of having group name in group too?
            if torid == team_name:
                continue
            cdfid = torid_to_cdfid_map[torid]
            cdfid_in_groups[cdfid] = cdfid
            cdf_to_teamname[cdfid] = team_name
        
    print("group to names:")
    for team_name in g:
        member_string = ""
        for torid in g[team_name]:
            if not torid in torid_to_cdfid_map:
                continue
            cdfid = torid_to_cdfid_map[torid]
            member_string += cdfid_to_name[torid_to_cdfid_map[torid]] + "," 
        print("%s, %s" %( team_name, member_string))
        
    print("cdf id to group:")
    #chop this into grades file sorted by cdfid
    for cdfid in cdf_to_teamname:
        print( "%s,%s" % (cdfid,cdf_to_teamname[cdfid]))