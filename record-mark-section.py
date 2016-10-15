#!/usr/bin/python

# port install python35 +readline
# else readline acts very strangely around prompts.

"""
knows how to handle my 2016 fall CDF empty grades files built from the new classlists that contain all sorts of useful data
"""
from __future__ import print_function  #allows print as function
import cdf_class_list_reader
from menu import MatzMenu

import sys,os, re, readline, argparse

from complete import SimpleCompleter

def parse_positional_args():
    "parse the command line parameters of this program"
    parser = argparse.ArgumentParser()
    parser.add_argument("class_list_file_name", help="name of CDF class list file")
    parser.add_argument("grade_file_name", help="name of a Jim Clarke format grades file")
    args = parser.parse_args()
    return (args.class_list_file_name, args.grade_file_name)

def read_utorids_from_cdf_class_list_file(fn):
    """assuming fn is a csv file, which CDF class lists are, read the file and return an array of the utorids"""
    import csv
    completion_options = []
    try:
        with open(fn, 'r') as csv_file:
            csv_file_reader = csv.reader(csv_file, delimiter=',')
            for student_record in csv_file_reader:
                # yuck. assuming first field of class file is torid
                utorid = student_record[0]
                completion_options.append(student_record[0])
            return completion_options
    except:
        print("exception opening or reading", fn)

class GradeFileReaderWriter(object):
    """read a Jim Clarke style grades file and squirrel away the data for later.
    Later we will use this object to retreive lines that match a given query.
    """
    def __init__(self, fn):
        self.grade_file_name = fn
        self.line_array = []
        self.line_value_index = {}
        self.read_file()
        return

    def read_file(self):
        try:
            with open(self.grade_file_name, 'rb') as grade_file:
                grade_file = open(grade_file_name, 'rb')
                ix = 0
                for bline in grade_file:
                    line = bline.decode('UTF-8').rstrip('\n')
                    self.line_array.append(line)
                    self.line_value_index[line] = ix  # remember the spot in line_array..
                    ix += 1
                grade_file.close()
        except:
            print("failed to open", grade_file_name)

    def print(self):
        print("GradeFileReader.line_array", self.line_array)
        print("GradeFileReader.line_value_array", self.line_value_index)


(class_list_file_name, grade_file_name) =  parse_positional_args()

gfr = GradeFileReaderWriter(grade_file_name)
gfr.print()

completion_options = read_utorids_from_cdf_class_list_file(class_list_file_name)

#magic forces in the utorid's as completion options
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
                #readline will do completion on utorid's but can enter any string from grade file too
                query_string = input("identifying string (tab completes on utorid, EOF or empy line to quit): ")
            except KeyboardInterrupt:
                query_string = '' #just try again
                print("..keyboard interrupt..")
                continue
            except EOFError:
                is_more = False
                print("..eof..")
                break

            #gimme to users who doesn't know how to make EOF
            if len(query_string) == 0: #empty line, we're done entering names
                is_more = False
                break

            #TODO use filter
            #look for query in lines of from GRADES file (looking for right student)
            for line in gfr.line_array:
                m = re.search(query_string, line)
                if m:
                    matched_lines.insert(0,line)

            #query didn't match any students
            if len(matched_lines) == 0:
                print(query_string, "matched nothing.. try again")
                continue

            #query matched one special case.. just choose it. What if it's wrong student??
            if len(matched_lines) == 1:
                selected_student_line = matched_lines[0]
            else:
                #query_string matched more than one student.. print menu of matches
                matched_lines.append("NO") #add choice that it wasn't right student
                menu = MatzMenu(matched_lines,"select a match: ")
                selected_student_line = matched_lines[menu.menu()].rstrip()
                if selected_student_line == "NO":
                    continue

            matched_lines = [selected_student_line]

        # come out of loop with a selected_student_line, which is a
        # grades file line, the one that matched the student identified by query_string
        # append mark to line..

        if not is_more:
            break #we're done entering students.

        line_with_mark_appended = selected_student_line

        if not line_with_mark_appended.endswith(","):
            line_with_mark_appended += ","

        #todo enter mark here (as opposed to 1/0)
        line_with_mark_appended += "1"

        #if this fails to find a student it means that line has changed already.
        #maybe make this explict by adding a dict of booleans?
        if selected_student_line in gfr.line_value_index:
            ix_of_line_to_modify = gfr.line_value_index[selected_student_line]
            gfr.line_array[ix_of_line_to_modify] = line_with_mark_appended
            print("line[", ix_of_line_to_modify, "] <-", line_with_mark_appended)
        else:
            print(selected_student_line, "not in", gfr.line_value_index)

except:
    print("an exception happened, save to temp file and pick up pieces by hand")
#print(line_array[ix_of_line_to_modify])

while True:
    try:
        new_file_name = input("write modified lines into file named:")
        try:
            new_file = open(new_file_name, 'w')
        except:
            print("could not open ", new_file_name, "for writing")
            continue
        break
    except:
        print("really? interupt and you don't get to save!")
        continue

for l in gfr.line_array:
    print(l, file=new_file)
new_file.close()

os.system("ls -l " + new_file_name)
exit(0)
