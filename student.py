#!/usr/bin/python

from __future__ import print_function  #allows print as function

Debug = False #True

import csv # see https://docs.python.org/2/library/csv.html
import sys,os
import re  #regular expressions

def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)

def errorExit(*objs):
    print("ERROR: ", *objs, file=sys.stderr)
    exit(42)

def debug_message(*objs):
    if Debug:
        print("DEBUG: ", *objs, file=sys.stderr)

def verbose_message(*objs):
    print("VERBOSE: ", *objs, file=sys.stderr)

# now parse the line
# stupid bloody ( ) 
# cdfid NNN (last, first) userid@mail.utoronto.ca
#
def parseClassListLine(line):
    print(line)
    cdfid_number_rest = line.split("(")
    name_email = cdfid_number_rest[1].split(")")
    cdfid = cdfid_number_rest[0].split(" ")[0]
    student_number = cdfid_number_rest[0].split(" ")[1]
    name = name_email[0] 
    email = name_email[1]
    return(cdfid,name,email)

# parse empty grades file. build map of cdfid to TA
#
# NNNNNNNN    c2matz,0101,TA
#
# groan, but if the students has dropped, it will look like
# NNNNNNNN  d  c2matz,0101,TA
# in which case we don't want to be here at all.

# worse, it can look like:
# NNNNNNNN    c2matz   ,0101,TA

#
# parse a line from a  grades file    
# return (student_number, cdfid, section, ta)
# ["c2matz", "0101", "TA"]
#
def parseEmptyGradeFileLine(line):
    student_number = "later" #stuff to left of blanks
    sline = line.rstrip()
    first_blank = sline.find(' ')
    #next 4 chars are blank, drop indicator, flag chars..
    assert sline[first_blank] == ' '
    assert sline[first_blank+3] == ' '
    drop_char = sline[first_blank+1]
    flag_char = sline[first_blank+2]
    dropped = drop_char == 'd'
    
    data_on_sline = sline[first_blank+4:-1]
    grade_file_tokens = data_on_sline.split(",") 
    if len(grade_file_tokens) < 3:
        errorExit("weird line in grade file len(grade_file_tokens) < 3", line )
    cdfid = grade_file_tokens[0]
    section = grade_file_tokens[1]
    ta = grade_file_tokens[2]
    debug_message(cdfid,ta)
    cdfid_to_tut[cdfid] = ta
    return (dropped, flag_char, student_number, cdfid, section, ta)

# print a cheesy little menu. If there is just one element in menu_lines, then return 0
# TODO: be nice to allow user to choose first char of line too.
def menu(menu_lines, prompt):
    if len(menu_lines) == 1:
        return 0
    n = 0    
    for a_matched_line in menu_lines :
        print(n, a_matched_line)
        n += 1

    if len(menu_lines) == 1:
        selection = 0
    else:
        ri = "fubar"
        try:
            str_selection = raw_input(prompt)
            return int(str_selection)
        except KeyboardInterrupt:
            errorExit("interrupt")
        except:
            errorExit("invalid selection:", str_selection)

if len(sys.argv) > 3 :
    debug_message( sys.argv[1], sys.argv[2])
    CLASS_LIST_FILE_NAME = sys.argv[1]
    EMPTY_GRADES = sys.argv[2]
    query_string = sys.argv[3]
    debug_message(CLASS_LIST_FILE_NAME, query_string)
else:
    warning( "usage: ", sys.argv[0], " class-list-file-from-CDF grades-empty query string")
    exit(2)

try:
    listfile = open(CLASS_LIST_FILE_NAME, 'rb')
except:
    errorExit("failed to open", CLASS_LIST_FILE_NAME)
    
try:
    empty_file = open(EMPTY_GRADES, 'rb')
except:
    errorExit("failed to open", EMPTY_GRADES)

cdfid_to_tut = {}

in_header = True    
for line in empty_file:
    if in_header:
        if len(line) == 1:
            in_header = False
        continue
    dropped, flag_char, sn,cdfid, sec, ta =  parseEmptyGradeFileLine(line)
    cdfid_to_tut[cdfid] = ta

debug_message(cdfid_to_tut)
    
matched_lines = []
for line in listfile:
    line = line.rstrip()
    m = re.search(query_string, line)
    if m:
        matched_lines.insert(0,line)

if len(matched_lines) == 0 :
    errorExit("failed to find any lines in", CLASS_LIST_FILE_NAME,"MATCHING", query_string)

line = matched_lines[menu(matched_lines, "select a match: ")].rstrip()

debug_message("hit selected=", line)

cdfid, name, email = parseClassListLine(line)
ta = cdfid_to_tut[cdfid]
debug_message(cdfid, name, email,ta)

strs_to_copy = [line, cdfid, name, email, ta]
#menu_prefix = ["LINE  ", "CDFID ", "NAME  ", "EMAIL", "TA     " ]
menu_lines = ["LINE  "+line, "CDFID "+cdfid, "NAME  "+name, "EMAIL"+email, "TA    " +ta]
str_to_clipboard = strs_to_copy[menu(menu_lines, "select what to copy to clipboard: ")]

debug_message("string to be copied to clipboard=", str_to_clipboard)
    
os.system("/bin/echo -n '%s' | pbcopy" % str_to_clipboard)
