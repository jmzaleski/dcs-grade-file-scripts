#!/usr/bin/python

# port install python35 +readline
# else readline acts very strangely around prompts.

"""
knows how to handle my 2016 fall CDF empty grades files built from the new classlists that contain all sorts of useful data
"""
from __future__ import print_function  #allows print as function
from menu import MatzMenu

import sys,os, re,readline, argparse

#from complete import SimpleCompleter

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

class GradeFileReaderWriter(object):
    """read a Jim Clarke style grades file and squirrel away the data for later.
    Later we will use this object to retreive lines that match a given query and
    append a new mark to the lines, and finally write them to a new grades file
    """
    def __init__(self, fn):
        self.grade_file_name = fn
        self.line_array = []
        self.line_value_index = {}
        self.read_file()
        return

    def read_file(self):
        """
         reads the lines out of the grades file, including the header.
        :return:
        """
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
            raise Exception("GradeFileReader fails to read " + self.grade_file_name)

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


def set_up_readline(cl):
    """UI: python hackery to configure readline do completion on an array"""

    # Tell readline to use tab key for completion
    # hack from stackoverflow. os/x python is a bit different because built atop BSD libedit
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

    import logging
    LOG_FILENAME = '/tmp/completer.log'
    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, )

    # completer will be used by readline library when it sees a tab.
    # Hard to find a decent writeup of the protocol.
    # Seems that when you hit tab on text it calls with state 0.
    # this is when you're supposed to find the matches for text in completion_list
    # Then, each time it calls with state 1,2, and we're supposed to return the corresponding completion
    if True:
            class SimpleCompleter(object):
                """cribbed from python readline documentation"""
                def __init__(self, cl):
                    self.completion_list = sorted(cl)
                    self.matches = []
                    return
                def complete(self, text, state):
                    response = None
                    if state == 0:
                        # This is the first time for this text, so find the elements
                        # of the completion list that match text
                        if text:
                            self.matches = [s
                                            for s in self.completion_list
                                            if s and s.startswith(text)]
                            logging.debug('%s matches: %s', repr(text), self.matches)
                        else:
                            self.matches = self.completion_list[:]
                            logging.debug('(empty input) matches: %s', self.matches)

                    # Return the state'th item from the match list,
                    try:
                        response = self.matches[state]
                    except IndexError:
                        response = None
                    logging.debug('complete(%s, %s) => %s',
                                  repr(text), state, repr(response))
                    return response
            readline.set_completer(SimpleCompleter(cl).complete)
    else:
        # ******** doesn't work **************
        # I'm obviously not understanding some subtle aspect of python closures.

        matches_for_closure = []

        # A completer instance will be used by readline library when it sees a tab.
        # clue?? pycharm complains:
        # This inspection detects names that should resolve but don't.
        # Due to dynamic dispatch and duck typing, this is possible in a limited but useful number of cases.
        # Top-level and class-level items are supported better than instance items.

        def hack(saved_matches, cl): # i wanna closure over saved_matches and cl!
            def complete(text, state):
                logging.debug("complete(text=%s, state=%s)", text, state)
                logging.debug("matches=%s)", saved_matches) #how come saved_matches unresolved?

                response = None
                if state == 0:
                    # This is the first time for this text, so build a match list.
                    logging.debug("state == 0")
                    if text:
                        saved_matches = [s for s in cl if s and s.startswith(text)]
                        logging.debug('%s matches: %s', repr(text), saved_matches)
                    else:
                        matches = cl[:]  # all possible completions
                        logging.debug('(empty input) matches: %s', saved_matches)

                # Return the state'th item from the match list,
                try:
                    response = saved_matches[state]
                except IndexError:
                    response = None
                logging.debug('complete(%s, %s) => %s', repr(text), state, repr(response))
                return response
            readline.set_completer(complete)
        hack(matches_for_closure, cl)

################## real work ###########################

(class_list_file_name, grade_file_name) =  parse_positional_args()

# gfr, grade-file-reader instance
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

