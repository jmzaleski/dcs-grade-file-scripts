#!/usr/bin/python

# port install python35 +readline
# else readline acts very strangely around prompts.

"""
knows how to handle my 2016 fall CDF empty grades files built from the new classlists that contain all sorts of useful data
"""
from __future__ import print_function  #allows print as function

import sys,os, re,readline, argparse

from menu import MatzMenu

def parse_positional_args():
    "parse the command line parameters of this program"
    parser = argparse.ArgumentParser()
    parser.add_argument("class_list_file_name", help="name of CDF class list file")
    parser.add_argument("grade_file_name", help="name of a Jim Clarke format grades file")
    args = parser.parse_args()
    return (args.class_list_file_name, args.grade_file_name)

def read_utorids_from_cdf_class_list_file(fn):
    """assuming fn is a csv file, which CDF class lists are,
    read the file and return an array of the utorids"""
    import csv
    utorids = []
    try:
        with open(fn, 'r') as csv_file:
            csv_file_reader = csv.reader(csv_file, delimiter=',')
            for student_record in csv_file_reader:
                # yuck. assuming first field of class file is torid
                utorid = student_record[0]
                utorids.append(student_record[0])
            return utorids
    except:
        print("exception opening or reading", fn)

def read_query_from_input(prompt):
    "UI read a line from stdin"
    try:
        # readline will do completion on utorid's but can enter any string from grade file too
        query_string = input("identifying string (tab completes on utorid, EOF or empy line to quit): ")
        if len(query_string) == 0:
            return None
        else:
            return query_string
    except KeyboardInterrupt:
        print("..keyboard interrupt..")
        return '' #empty string
    except EOFError:
        print("..eof..")
        return None

def select_a_student(gfr):
    """"UI: prompt user for query and narrow it down to one student in grade file.
    Returns a line, or None, which indicates user entered empty query or EOF, presumably to indicate they are finished"""

    while True:
        query_string = read_query_from_input("identifying string (tab completes on utorid, EOF or empy line to quit): ")
        if query_string == None:
            return None
        elif len(query_string) == 0:
            continue  # try query again..

        matched_lines = gfr.matching_lines(query_string)
        if len(matched_lines) == 0:
            print(query_string, "matched nothing.. try again")
        elif len(matched_lines) == 1:
            return matched_lines[0]
        else:
            # query_string matched more than one student.. print menu of matches
            # with an additional choice of NO
            # user choses one, we're good. User choose NO, go around again.
            matched_lines.append("NO")  # add choice that it wasn't right student
            menu = MatzMenu(matched_lines, "select a match: ")
            user_choice = matched_lines[menu.menu()].rstrip()
            if user_choice == "NO":
                continue #didn't like choices.. try again
            else:
                return user_choice  # yup, this is the oen
        assert False #never here
    return None

from set_up_readline_for_completion import set_up_readline

################## real work ###########################

(class_list_file_name, grade_file_name) =  parse_positional_args()

from grade_file_reader_writer import GradeFileReaderWriter
gfr = GradeFileReaderWriter(grade_file_name)

completion_list = read_utorids_from_cdf_class_list_file(class_list_file_name)
set_up_readline(completion_list)

# prompt for something obvious by way of identifying data, name, utorid, student number, whatever
# readline tab completion on utorid only, so if entering utorid very efficient
# however, will look for any regular expression in grades file too.

try:
    while True:
        selected_student_line = select_a_student(gfr)
        if selected_student_line == None:
            break
        else:
            if not gfr.append_mark_to_line(selected_student_line,1):
                print(selected_student_line, "not found.. have you changed it already this run?")
except:
    print("an exception happened, save (garbage??) to temp file and pick up pieces by hand")

# carefully prompt for file name. keep trying until we write the data.
# Really, really don't want to lose the typing that went on above!!
while True:
    try:
        new_file_name = input("write modified lines into file named:")
        try:
            gfr.write_to_new_grade_file(new_file_name)
        except:
            print("exception happened opening ", new_file_name, "for writing or actually writing data")
            continue
        os.system("ls -l " + new_file_name)
        exit(0)

    except EOFError:
        print("..eof..okay then, really quit w/o saving..")
        exit(2)

    except KeyboardInterrupt:
        print("really? caught that interupt but guessing you still want to save! EOF to quit")
        continue

