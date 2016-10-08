#!/usr/bin/python

"""
knows how to handle my 2016 fall CDF empty grades files built from the new classlists that contain all sorts of useful data
"""
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

empty_reader = grade_file_reader.GradeFileReader(EMPTY_GRADES)    
empty_reader.skipHeader()

matched_lines = []
for bline in empty_reader.readLines():
    line = bline.decode('UTF-8')
    m = re.search(query_string, line)
    if m:
        matched_lines.insert(0,line)
        tup = empty_reader.parseEmptyGradeFileLine(line)
        if len(tup) == 0:
            continue
        (dropped, flag_char, cdfid, sec, ta) =  tup

if len(matched_lines) == 0 :
    msg.error("failed to find any lines in", EMPTY_GRADES,"MATCHING", query_string)

#display menu of matched lines so user can select which match they meant.
menu = MatzMenu(matched_lines,"select student: ")
resp = menu.menu()
if resp < 0 or resp > len(matched_lines)-1:
    print("invalid response")
    exit(0)

line = matched_lines[resp].rstrip()

#now have a class list line, the one that matched the student

#(dropped, flag_char, cdfid, section, ta) = empty_reader.parseEmptyGradeFileLine(line)
csv = line.split(",")
data_fields = csv[1:]

f1 = csv[0]
f1_split = f1.split(' ')
stud_no = f1_split[0]
first_blank = f1.find(' ')

if not f1[first_blank] == ' ':
    msg.error("malformed line: no blank?", line)

assert f1[first_blank] == ' '  # always a blank after student number

drop_char = f1[first_blank + 1]  # two chars of flags
dropped = drop_char == 'd'
flag_char = f1[first_blank + 2]

assert f1[first_blank + 3] == ' '  # always a blank before data fields

if not f1[first_blank + 4].isalpha():  # real data has to start after blank
    self.msg.error("malformed line: after flag, then blank, must come alpha at pos", first_blank + 4, '"' + sline + '"')
# TODO assert something here along lines of is character

data_on_sline = f1[first_blank + 4:]
names = data_on_sline.split(" ")

nick_name = names[0]
print(nick_name)

#menu_items = [line, eline, cdfid, name, email, ta, "MAILTO:", "IMAGE:"]
#menu_items = [line, cdfid, ta, "MAILTO:", "IMAGE:"]
email = data_fields[-1]
menu_items = [line] + data_fields + ["MAILTO:", "IMAGE:"]

m2 = MatzMenu(menu_items, "option: ") #number of selected menu item
resp = m2.menu()
if resp <0:
    exit(0)

selected_menu_item = menu_items[resp]

print(selected_menu_item)

#hacky extension to mail student or view his picture
if selected_menu_item == "MAILTO:":
    print('open mailto:%s' % email)
    os.system('open mailto:%s' % email)
elif selected_menu_item == "IMAGE:":
    #probably should do nothing if image file doesn't exist..
    os.system('open pics/%s.jpg' % cdfid)
else:
    os.system("/bin/echo -n '%s' | pbcopy" % selected_menu_item)
