#!/usr/bin/python
# program that uses curses to show completions for utorids from class list and prompts for marks, writes new grades file.
# (no longer uses readline, for which completion was a bit too invisible for my taste)

# port install python35 +readline
# else readline acts very strangely around prompts.

"""
knows how to handle my 2016 fall CDF empty grades files built from the new classlists that contain all sorts of useful data
"""
from __future__ import print_function  #allows print as function

import sys,os, re, traceback

from menu import MatzMenu

def parse_positional_args():
    "parse the command line parameters of this program"
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("class_list_file_name", help="name of CDF class list file")
    parser.add_argument("grade_file_name", help="name of a Jim Clarke format grades file")
    parser.add_argument("--one", action='store_true', help="any selected utorid gets a mark of 1")
    parser.add_argument("--letter_grade", action='store_true', help="a b c d e convert to %")
    #TODO: make output grade file the third parm. Can it be made optional somehow?
    args = parser.parse_args()
    return (args.one, args.letter_grade, args.class_list_file_name, args.grade_file_name)


def read_utorid_dict_from_cdf_class_list_file(fn):
    """assuming fn is a csv file, which CDF class lists are,
    read the file and return an array of the utorids"""
    import csv
    d = {}
    try:
        with open(fn, 'r') as csv_file:
            csv_file_reader = csv.reader(csv_file, delimiter=',')
            for student_record in csv_file_reader:
                # yuck. assuming first field of class file is utorid
                utorid = student_record[0]
                line = "%30s %s %10s %25s %20s" % (student_record[1],student_record[2],student_record[3],student_record[4],student_record[5])
                # for r in student_record:
                #     line+=r
                d[utorid] = line
            return d
    except:
        print("exception opening or reading", fn)
        
def read_query_from_input(prompt):
    "UI read a line from stdin"
    try:
        # readline will do completion on utorid's but can enter any string from grade file too
        query_string = input(prompt)
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

def select_a_student(gfr,completion_dict):
    """"UI: prompt user for query and narrow it down to one student in grade file.
    Returns a line, or None, which indicates user entered empty query or EOF, presumably to indicate they are finished"""

    while True:
        from prompt_for_input_string_with_completions_curses import prompt_for_input_string_with_completions_curses

        query_string = prompt_for_input_string_with_completions_curses(
            "student id (completion on utorid, EOF to finish): ",
            20,
            completion_dict)
        
        print(query_string)
        if query_string == None:
            return None
        elif len(query_string) == 0:
            continue  # try query again..

        # this behaviour might not be right for all use cases!
        # if user hit return on a query that was the prefix of only one
        # completion (but not the exact utorid) we record the mark for that student.
        # or, if first chars or utorid are ilegigle and have to type student number or a few chars of name..
        
        matched_lines = gfr.matching_lines(query_string)
        if len(matched_lines) == 0:
            print(query_string, "matched nothing.. try again")
            continue
        elif len(matched_lines) == 1:
            print(matched_lines[0])
            return matched_lines[0]
        else:
            # query_string matched more than one student.. print UGLY menu of plain text matches
            # with an additional choice of NO (try again)
            # user choses one, we're good. User choose NO, go around again.
            matched_lines.append("NO")  # add choice that it wasn't right student
            menu = MatzMenu(matched_lines, "select a match: ")
            user_choice = matched_lines[menu.menu()].rstrip()
            if user_choice == "NO":
                # didn't like choices.. try again
                continue 
            else:
                return user_choice
    return None


def paranoidly_open_file_for_write(gfr):
    "open the new file name, also write contents of gfr to it too make really, really sure write is working"
    while True:
        try:
            new_file_name = input("write modified lines into file named:")
            if new_file_name == grade_file_name:
                print("too dangerous to output to the same file we are reading.. choose another file")
                continue
        except EOFError:
            print("..okay then, you really don't want to set an output file name so just quitting..")
            exit(2)
        except KeyboardInterrupt:
            print("really? caught that interupt but guessing you still want to name an output file. Try again (EOF to quit)")
            continue

        #okay, so have a file name.. does the file system think we can write it?
        try:
            if os.path.exists(new_file_name):
                print(new_file_name, "exists.. and we refuse to overwrite. Try another")
                continue
        except:
            print("unexpected throw on os.access. bail")
            traceback.print_exc(file=sys.stdout)
            exit(3)

        #now try writing empty string.. 
        try:
            with open(new_file_name, "w") as output_file:
                output_file.write('')
                os.system("ls -l " + new_file_name)
        except:
            print(new_file_name, "failed to write empty string to file? really? bail!")
            traceback.print_exc(file=sys.stdout)
            exit(3)

        #so try copying input data to the new file..
        try:
            gfr.write_to_new_grade_file(new_file_name)
            os.system("ls -l " + new_file_name)
            break
        except:
            print("exception happened opening ", new_file_name, "for writing or actually writing data")
            print("just tried to write a copy of input into", new_file_name, "and failed! giving up")
            exit(4)
    return new_file_name

from set_up_readline_for_completion import set_up_readline

################## real work ###########################
if __name__ == '__main__':
    (is_one, is_letter_grade, class_list_file_name, grade_file_name) =  parse_positional_args()

    from grade_file_reader_writer import GradeFileReaderWriter
    gfr = GradeFileReaderWriter(open(grade_file_name).read())
    gfr.read_file()

    d = read_utorid_dict_from_cdf_class_list_file(class_list_file_name)
    new_file_name = paranoidly_open_file_for_write(gfr)
    
    # prompt for something obvious by way of identifying data, name, utorid, student number, whatever
    try:
        while True:
            selected_student_line = select_a_student(gfr,d)
            if selected_student_line == None:
                break
            #print(selected_student_line)
            
            if is_one: #attendance, cr/ncr, or other all-or-nothing assignment
                mark = 1
            elif is_letter_grade:
                mark_input = read_query_from_input("mark (a b c d e): ")
                if mark_input == "a":
                    mark = 80
                elif mark_input == "b":
                    mark = 70
                elif mark_input == "c":
                    mark = 60
                elif mark_input == "d":
                    mark = 50
                elif mark_input == "e":
                    mark = 40
            else:
                mark_input = read_query_from_input("mark:")
                mark = int(mark_input)
                
            print("`%s'" % (mark))

            # append the new mark to the line of the grade file
            try:
                appendage = "%s" % (int(mark))
                if not gfr.append_mark_to_line(selected_student_line,appendage):
                    print(selected_student_line, "not found.. have you changed student record already this run?")
            except:
                traceback.print_exc(file=sys.stdout)
                print("threw when appending marks")
                
            # finally try and write what has been entered to the new file identified earlier.
            # paranoidly write entire mark file out each time a single grade is entered.
            try:
                gfr.write_to_new_grade_file(new_file_name)
            except:
                print("exception happened writing ", new_file_name, "weird given we wrote it earlier successfully")
                exit(1)
        os.system("ls -l " + new_file_name)

    except:
        print("an exception happened, save (garbage??) to temp file and pick up pieces by hand")
        traceback.print_exc(file=sys.stdout)
        print("threw when adding together marks or adding them. try writing to another file name.")
        paranoidly_open_file_for_write(gfr) #try try again?

