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

#build maps from cdfid (which we can always parse out of these files)
cdfid_to_tut = {}
cdfid_to_empty_grades_file_line = {}
empty_reader = grade_file_reader.GradeFileReader(EMPTY_GRADES)    
empty_reader.skipHeader()
for line in empty_reader.readLines():
    (dropped, flag_char, cdfid, sec, ta) =  empty_reader.parseEmptyGradeFileLine(line)
    cdfid_to_tut[cdfid] = ta
    cdfid_to_empty_grades_file_line[cdfid] = line
     
msg.debug(cdfid_to_tut)

#read the CDF class list looking for lines that match the query
matched_lines = []
class_list_reader = cdf_class_list_reader.CdfClassListFileReader(CLASS_LIST_FILE_NAME)
for line in class_list_reader.readLines() :
    line = line.rstrip()
    m = re.search(query_string, line)
    if m:
        matched_lines.insert(0,line)

if len(matched_lines) == 0 :
    msg.error("failed to find any lines in", CLASS_LIST_FILE_NAME,"MATCHING", query_string)

#display menu of matched lines so user can select which match they meant.
menu = MatzMenu(matched_lines,"select a match")
line = matched_lines[menu.menu()].rstrip()

#now have a class list line, the one that matched the student
student = class_list_reader.parseClassListLine(line)
cdfid = student.cdfid
name = student.name
email= student.email.strip()

#futz around students who happen to have CDF id's shorter than grades files allow
if cdfid in cdfid_to_tut:
    ta = cdfid_to_tut[cdfid]
else:
    if cdfid + "__" in cdfid_to_tut:   ####hack for too short cdfid's
        ta = cdfid_to_tut[cdfid+"__"]
    else:
        msg.error("cdf key", cdfid, "in grades file but not in  class list")

eline = cdfid_to_empty_grades_file_line[cdfid]

menu_items = [line, eline, cdfid, name, email, ta, "MAILTO:", "IMAGE:"]
m2 = MatzMenu(menu_items, "option: ") #number of selected menu item
selected_menu_item = menu_items[m2.menu()]

#hacky extension to mail student or view his picture
if selected_menu_item == "MAILTO:":
    print('open mailto:%s' % email)
    os.system('open mailto:%s' % email)
elif selected_menu_item == "IMAGE:":
    #probably should do nothing if image file doesn't exist..
    os.system('open pics/%s.jpg' % cdfid)
else:
    os.system("/bin/echo -n '%s' | pbcopy" % selected_menu_item)
