#!/usr/bin/python

from __future__ import print_function  #allows print as function

M_FILE_NAME = "cdfid-to-githubid.csv" 
G_FILE_NAME = "groups-cdfid.csv" #from google signup sheet

import csv # see https://docs.python.org/2/library/csv.html
import sys

def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)

def error(*objs):
    print("ERROR: ", *objs, file=sys.stderr)
    exit(42)

Debug = False

def debug_message(*objs):
    if Debug:
        print("DEBUG: ", *objs, file=sys.stderr)

def verbose_message(*objs):
    print("VERBOSE: ", *objs, file=sys.stderr)

with open(M_FILE_NAME, 'rb') as mapfile:
 map_reader = csv.reader(mapfile, delimiter=',', quotechar='|',dialect=csv.excel_tab)

 first_line = True

 cdfid_to_github = {}
 github_to_cdfid = {}

 #read the mapping file and create a map from LOWER CASE cdfid to github id
 for list_cdfid_githubid in map_reader:
     if first_line:
         first_line = False
         continue
     cdfid = list_cdfid_githubid[0]
     githubid = list_cdfid_githubid[1]
     cdfid_to_github[cdfid.lower()] = githubid
     github_to_cdfid[githubid] = cdfid
     debug_message( "cdfid=", cdfid, "githubid=","githubid,cdfid_to_github[cdfid]=", githubid,cdfid_to_github[cdfid],"github_to_cdfid[githubid]=",github_to_cdfid[githubid])
     if not cdfid_to_github[cdfid] == githubid:
         error(cdfid, "busted")
     if not github_to_cdfid[githubid] == cdfid:
         error( githubid, "busted")

 all_student_github_id = [] #keep them here to help make invite
         
 #so now we have the mappings, can read the group file and map the cdfid's to github ids
 with open(G_FILE_NAME, 'rb') as group_file:
     group_file_reader = csv.reader(group_file, delimiter=',', quotechar='|',dialect=csv.excel_tab)

     first_line = True
     for list_cdfid_in_group in group_file_reader:
         if first_line:
             first_line = False
             continue;

         team_name=list_cdfid_in_group[0]
         ta_github=list_cdfid_in_group[1]
         debug_message( "team_name=",team_name,"ta_github=",ta_github)
         
         # group_cdf_id_list may contain random case CDF ids, empty strings, unmapped students
         group_cdf_id_list = list_cdfid_in_group[2:] 
         group_githubid_list = []

         #carefully collect the cdfid's for the students in the group, scrubbing it
         scrubbed = []
         for cdfid in group_cdf_id_list:
             if len(cdfid) == 0:
                 continue
             if not cdfid in cdfid_to_github.keys():
                 warning( "SKIPPING adding to team because not in cdfid_to_github", cdfid )
                 continue
             student_github = cdfid_to_github[cdfid]
             group_githubid_list.insert(0,student_github)
             all_student_github_id.insert(0,student_github)

         #print the mapped group file out
         group_github_csv_line = "team-" + team_name
         group_github_csv_line += ","+ ta_github
         for student_github in group_githubid_list:
             group_github_csv_line += ","+ student_github
         print( group_github_csv_line )

     line = ''
     for s in all_student_github_id:
        line += "," + s
     warning(line)
             

