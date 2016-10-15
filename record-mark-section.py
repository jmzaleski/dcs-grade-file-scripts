#!/usr/bin/python

# port install python35 +readline
# else readline acts very strangely around prompts.

"""
knows how to handle my 2016 fall CDF empty grades files built from the new classlists that contain all sorts of useful data
"""
from __future__ import print_function  #allows print as function
from menu import MatzMenu

import sys,os, re,readline, argparse

from complete import SimpleCompleter

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

def read_query_from_input(prompt):
    "read a line from stdin"
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

    def matching_lines(self, query):
        "return lines that match the query"
        return [l for l in self.line_array if re.search(query,l)]

    def append_mark_to_line(self,student_line,mark):
        """append the mark, which may be a string or a number, to the right line.
        Returns true if line is found and mark appended correctly, o/w False"""
        if student_line in self.line_value_index:
            ix = self.line_value_index[student_line]
            before = self.line_array[ix]
            after = before
            if not after.endswith(","):
                after += ","
            after += str(mark)
            self.line_array[ix] = after
            print("line[", ix, "] <-", after)
            return True
        else:
            #print(student_line, "not in", self.line_value_index)
            return False

    def print(self):
        """debugging.. print the arrays"""
        print("GradeFileReader.line_array", self.line_array)
        print("GradeFileReader.line_value_array", self.line_value_index)

    def write_to_new_grade_file(self,fn):
        """write the modified lines out to a new file name"""
        with open(fn,'w') as new_file:
            for l in self.line_array:
                print(l, file=new_file)


def select_a_student(gfr):
    """"prompt user for query and narrow it down to one student in grade file.
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


(class_list_file_name, grade_file_name) =  parse_positional_args()

gfr = GradeFileReaderWriter(grade_file_name)

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

