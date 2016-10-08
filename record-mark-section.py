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
import readline
from complete import SimpleCompleter

msg = matz_utils.MessagePrinter(False)

if len(sys.argv) == 3 :
    msg.debug( sys.argv[1], sys.argv[2])
    CLASS_LIST_FILE_NAME = sys.argv[1]
    EMPTY_GRADES = sys.argv[2]
else:
    msg.warning( "usage: ", sys.argv[0], " class-list-file-from-CDF grades-empty")
    exit(2)

#build maps from cdfid (which we can always parse out of these files)

empty_reader = grade_file_reader.GradeFileReader(EMPTY_GRADES)
hdr = []
for l in empty_reader.skipHeader():
    hdr.append(l)

saved_lines_by_utorid = {}

line_array = []             # saves the lines.. will be rewritten with mark
line_value_index = {}       # remembers the index of each line

ix = 0
for bline in empty_reader.readLines():
    line = bline.decode('UTF-8')
    line_array.append(line)
    line_value_index[line] = ix
    ix += 1

import csv
completion_options = []

# set up completion list. (readline will make use of it)
# TODO: move the stuff that knows about file format to class grade_file_reader
with open(CLASS_LIST_FILE_NAME, 'r') as csv_file:
    csv_file_reader = csv.reader(csv_file, delimiter=',') #, quotechar='|', dialect=csv.excel_tab)
    for student_record in csv_file_reader:
        utorid = student_record[0]
        completion_options.append(student_record[0])

#this magic forces in the utorid's as completion options
readline.set_completer(SimpleCompleter(completion_options).complete)

# Tell readline to use tab key for completion
# hack from stackoverflow. os/x python is a bit different because built atop BSD libedit
if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")

# want to prompt for something obvious by way of identifying data, name, utorid, student number, whatever
# readline tab completion on utorid only..
# if get nothing, just prompt again
# if get multiples, prompt to resolve which hit
# if get wrong single hit.. geeze, then what?
# for the last name, just enter (empty line), that goes on to write new marks file

is_more = True
try:
    while is_more:
        matched_lines = []
        while not len(matched_lines) == 1:
            try:
                query_string = input("identifying string (tab completes on utorid, empy line to quit): ")
            except:
                query_string = '' #just try again
                print("throws, so just prompt for input again.")
                continue

            if len(query_string) == 0: #empty line, we're done entering names
                is_more = False
                break

            #TODO use filter
            #look for query in lines of grades file (looking for right student)
            for line in line_array:
                m = re.search(query_string, line)
                if m:
                    matched_lines.insert(0,line)

            #query didn't match any students
            if len(matched_lines) == 0:
                print("nothing matched, try again")
                continue

            #query matched one special case.. just choose it. What if it's wrong student??
            if len(matched_lines) == 1:
                selected_student_line = matched_lines[0]
            else:
                matched_lines.append("NO") #add choice that it wasn't right student
                menu = MatzMenu(matched_lines,"select a match: ")
                selected_student_line = matched_lines[menu.menu()].rstrip()
                if selected_student_line == "NO":
                    continue

            matched_lines = [selected_student_line]

        #come out of loop with a selected_student_line
        #now have a grades file line, the one that matched the student
        #so in case of one of our 1/0 assignments, add a ,1

        if not is_more:
            break #we're done entering students.

        line_with_mark_appended = selected_student_line

        if not line_with_mark_appended.endswith(","):
            line_with_mark_appended += ","

        #todo enter mark here (as opposed to 1/0)
        line_with_mark_appended += "1"

        ix_of_line_to_modify = line_value_index[selected_student_line]
        line_array[ix_of_line_to_modify] = line_with_mark_appended
        print("line[", ix_of_line_to_modify, "] <-", line_with_mark_appended)

except:
    print("an exception happened, save to temp file and pick up pieces by hand")
#print(line_array[ix_of_line_to_modify])

try:
    new_file_name = input("write modified lines into file named:")
except KeyboardInterrupt:
    exit(2)
except:
    exit(1)

try:
    new_file = open(new_file_name,'w')
except:
    msg.error("could not open ", new_file_name, "for writing")
    exit(42)

for l in hdr:
    print(l.decode('UTF-8'), file=new_file)
for l in line_array:
    print(l, file=new_file)
new_file.close()

os.system("ls -l " + new_file_name)
exit(0)
