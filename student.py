#!/usr/bin/python

from __future__ import print_function  #allows print as function
import cdf_class_list_reader

Debug = True #True

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
    debug_message("no use for student number, so far", student_number)
    name = name_email[0] 
    email = name_email[1]
    return(cdfid,name,email)

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

import grade_file_reader

empty_reader = grade_file_reader.GradeFileReader(EMPTY_GRADES)    
empty_reader.skipHeader()

#build cdfid to TA map
cdfid_to_tut = {}
for line in empty_reader.readLines():
    (dropped, flag_char, cdfid, sec, ta) =  empty_reader.parseEmptyGradeFileLine(line)
    cdfid_to_tut[cdfid] = ta
     
debug_message(cdfid_to_tut)

#read the CDF class list looking for the query
class_list_reader = cdf_class_list_reader.CdfClassListFileReader(CLASS_LIST_FILE_NAME)

lines = class_list_reader.readLines()    
matched_lines = []
for line in lines:
    line = line.rstrip()
    m = re.search(query_string, line)
    if m:
        matched_lines.insert(0,line)

if len(matched_lines) == 0 :
    errorExit("failed to find any lines in", CLASS_LIST_FILE_NAME,"MATCHING", query_string)

line = matched_lines[menu(matched_lines, "select a match: ")].rstrip()

debug_message("hit selected=", line)

(cdfid, name, email) = class_list_reader.parseClassListLine(line)
ta = cdfid_to_tut[cdfid]
debug_message(cdfid, name, email,ta)

strs_to_copy = [line, cdfid, name, email, ta]

menu_lines = ["LINE  "+line, "CDFID "+cdfid, "NAME  "+name, "EMAIL"+email, "TA    " +ta]
str_to_clipboard = strs_to_copy[menu(menu_lines, "select what to copy to clipboard: ")]

debug_message("string to be copied to clipboard=", str_to_clipboard)
    
os.system("/bin/echo -n '%s' | pbcopy" % str_to_clipboard)