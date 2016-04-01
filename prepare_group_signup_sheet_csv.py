#!/usr/bin/python

from __future__ import print_function  #allows print as function

#M_FILE_NAME = "cdfid-to-githubid.csv" 
G_FILE_NAME = "groups-cdfid.csv" #from google signup sheet

import csv # see https://docs.python.org/2/library/csv.html
import sys
import grade_file_reader
import group_csv_file_reader
import matz_utils
 
msg = matz_utils.MessagePrinter(True) #makes for debug..
msg.setPrefix(sys.argv[0])


if len(sys.argv) != 3 :
    msg.error("usage", sys.argv[0], "groups.csv", "grades_file.csv")
    
msg.verbose( sys.argv[1])
fn = sys.argv[1]
empty_grades_file_name = sys.argv[2]
msg.debug(empty_grades_file_name)

#read the csv file giving the cdf ids of the members of each group
#this returns a dictionary keyed by teamid containing a list of cdfids    
group_file = group_csv_file_reader.GroupFileReader(fn)
g = group_file.read_groups();
cdf_to_teamname = {}
cdfid_in_groups = {} #check for typos in group file
for team_name in g.keys():
    team = g[team_name]
    for cdfid in team:
        cdfid_in_groups[cdfid] = cdfid
        cdf_to_teamname[cdfid] = team_name
msg.verbose(cdf_to_teamname)
    
#read the grades file, adding the team of each student

gf = grade_file_reader.GradeFileReader(empty_grades_file_name)
hdr_lines = gf.skipHeader()
lines = gf.readLines()

(bad, bad_cdfid_list) = gf.checkCdfid(lines, cdfid_in_groups)
    
new_body_lines = gf.readAndAppendColumnFromMap(lines,cdf_to_teamname)


# sort with (shell-command-on-region (region-beginning) (region-end) "sort --field-separator=, --key=4" nil nil nil t)

for l in hdr_lines:
    print(l)
for l in new_body_lines:
    print(l)    

if bad:
    msg.error("found CDFID in class list that were not in group file", bad_cdfid_list)

