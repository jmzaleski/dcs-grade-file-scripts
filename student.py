#!/usr/bin/python

from __future__ import print_function  #allows print as function
import cdf_class_list_reader
from menu import MatzMenu

Debug = True #True

import sys,os
import re  #regular expressions
import matz_utils, grade_file_reader

msg = matz_utils.MessagePrinter(False)

if len(sys.argv) > 3 :
    msg.debug( sys.argv[1], sys.argv[2])
    CLASS_LIST_FILE_NAME = sys.argv[1]
    EMPTY_GRADES = sys.argv[2]
    query_string = sys.argv[3]
    msg.debug(CLASS_LIST_FILE_NAME, query_string)
else:
    msg.warning( "usage: ", sys.argv[0], " class-list-file-from-CDF grades-empty query string")
    exit(2)

empty_reader = grade_file_reader.GradeFileReader(EMPTY_GRADES)    
empty_reader.skipHeader()

#build maps from cdfid (which we can always parse out of these files)
cdfid_to_tut = {}
cdfid_to_empty_grades_file_line = {}

for line in empty_reader.readLines():
    (dropped, flag_char, cdfid, sec, ta) =  empty_reader.parseEmptyGradeFileLine(line)
    cdfid_to_tut[cdfid] = ta
    cdfid_to_empty_grades_file_line[cdfid] = line
     
msg.debug(cdfid_to_tut)

#read the CDF class list looking for lines that match the query
class_list_reader = cdf_class_list_reader.CdfClassListFileReader(CLASS_LIST_FILE_NAME)

lines = class_list_reader.readLines()    
matched_lines = []
for line in lines:
    line = line.rstrip()
    m = re.search(query_string, line)
    if m:
        matched_lines.insert(0,line)

if len(matched_lines) == 0 :
    msg.error("failed to find any lines in", CLASS_LIST_FILE_NAME,"MATCHING", query_string)

menu = MatzMenu(matched_lines,"select a match")
#line = matched_lines[menu(matched_lines, "select a match: ")].rstrip()
line = matched_lines[menu.menu()].rstrip()

msg.debug("hit selected=", line)

student = class_list_reader.parseClassListLine(line)
cdfid = student.cdfid
name = student.name
email= student.email

if cdfid in cdfid_to_tut:
    ta = cdfid_to_tut[cdfid]
else:
    if cdfid + "__" in cdfid_to_tut:   ####hack for too short cdfid's
        ta = cdfid_to_tut[cdfid+"__"]
    else:
        msg.error("cdf key", cdfid, "in grades file but not in  class list")
msg.debug(cdfid, name, email,ta)

mail_to = "mailto:"+ email
strs_to_copy = [line, cdfid, name, email, mail_to, ta]

menu_lines = ["CLINE " + line,
              "ELINE " + cdfid_to_empty_grades_file_line[cdfid], 
              "CDFID " + cdfid, 
              "NAME  " + name, 
              "EMAIL"  + email,
              mail_to, 
              "TA    " + ta]
m2 = MatzMenu(menu_lines, "option: ")
#str_to_clipboard = strs_to_copy[menu(menu_lines, "select what to copy to clipboard: ")]
str_to_clipboard = strs_to_copy[m2.menu()]

msg.debug("string to be copied to clipboard=", str_to_clipboard)

if str_to_clipboard == mail_to:
    os.system('open "%s"' % str_to_clipboard)
else:
    os.system("/bin/echo -n '%s' | pbcopy" % str_to_clipboard)
