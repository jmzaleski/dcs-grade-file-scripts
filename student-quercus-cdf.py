
from __future__ import print_function  #allows print as function

def parse_positional_args():
    "parse the command line parameters of this program"
    import argparse, collections
    parser = argparse.ArgumentParser()
    # either I don't understand or argparse doesn't like optional positional arguments.
    # want query_string (last parm) to be optional.
    for tuple in [
            #(arg_name,          arg_help_string,                                     nargs)
            ("cdf_csv_file",     "class list from CDF",                               1),
            ("quercus_csv_file", "class list from quercus eg: CSC300H1F-quercus.csv", 1),
            ("query_string",     "string to look for",                                '?')
            ]:
        parser.add_argument(tuple[0], help=tuple[1], nargs=tuple[2]),
    args = parser.parse_args()
    return (args.cdf_csv_file[0],args.quercus_csv_file[0], args.query_string)

# read the grades files exported from quercus and make a dict key'd by utorid. 
# value is list with element from each column
def read_course_files(CDF_CLASS_FILE,q_line):
    # read the CDF file and make a dict key'd by utorid of each line
    cdf_line = {}
    with open(CDF_CLASS_FILE) as csv_file:
        for a_line in csv.reader(csv_file, delimiter=',', quotechar='"',dialect=csv.excel_tab):
            cdf_line[a_line[0]] = a_line
    return cdf_line

def drops(q_line,cdf_line):
    dropped_utorid = set()
    if not set(q_line.keys()) == set(cdf_line.keys()):
        # find records that don't have a section field containing "CSC"
        # (for drops, quercus removes the lecture section but not the tutorial section)
        for utorid in set(q_line.keys()).difference(set(cdf_line.keys())):
            # TODO: make new method in csv_reader to fetch named column ? ask gary.
            if len(q_line[utorid])<5:
                print("ohoh quercus line has less than four fields..how did you do that??")
                print(q_line[utorid])
                exit(2)
            if len(q_line[utorid][4]) >0 and q_line[utorid][4].find("CSC") < 0:
                dropped_utorid.add(utorid)
                # print(utorid,"probably dropped because doesn't appear to be in lecture section")
        # compare utorid's to help catch case when files are out-of-date
        # TODO functionalify this!
        if False: #verbosity
            # debug output for diagnosing differences
            print("CDF classlist and quercus grade file do not contain identical sets of utorids")
            print("records in quercus but not CDF (drops?)")
            for utorid in set(q_line.keys()).difference(set(cdf_line.keys())):
                print( " ".join(filter(lambda s: len(s)>0,q_line[utorid]))[0:80]) #skip empty fields
            print("records in CDF but not quercus (adds?)")
            for utorid in set(cdf_line.keys()).difference(set(q_line.keys())):
                print( " ".join(filter(lambda s: len(s)>0,q_line[utorid]))[0:80]) #skip empty fields

    print("warning: following likely dropped because not in quercus lecture section", dropped_utorid)
    return dropped_utorid

# make a menu item for each student record from quercus matched by the query
# nb utorids come from the union of quercus and cdf, so there might not be a line in quercus
def select_student_menu(matched_utorids,q_line,cdf_line):
    choose_student_menu = []
    rev_utorid_map = {}
    for utorid in matched_utorids:
        if utorid in q_line:
            cols = filter(lambda a_col: a_col and a_col != "0.0", q_line[utorid])
            flat_cols = ", ".join(cols)
            choose_student_menu.append(flat_cols)
            rev_utorid_map[flat_cols] = utorid

    from menu import MatzMenu
    menu = MatzMenu(choose_student_menu,"select student: ")
    resp = menu.menu()
    if resp < 0 or resp > len(choose_student_menu)-1:
        print(resp, "is invalid response")
        exit(2)

    line = choose_student_menu[resp].rstrip()
    utorid = rev_utorid_map[line]
    return utorid


def select_student_field(utorid,q_line,cdf_line):
    IX_EMAIL_CDF = 5 #email always 5th field of CDF file
    menu_items = []
    menu_data = []
    if utorid in cdf_line:
        menu_items.append( cdf_line[utorid][IX_EMAIL_CDF])
        menu_data.append(cdf_line[utorid][IX_EMAIL_CDF])
    else:
        menu_items.append( "no email because " + utorid + " missing in CDF")
        menu_data.append( "no email because " + utorid + " missing in CDF")

    # display menu of fields in matched student
    # have to use this for a while to learn what want to see.
    # quercus has a lot of BS fields, screenfuls.

    cut_row = 5 #zillions of mark data fields follow
    for (hdr,data) in zip(quercus_csv_reader_by_utorid.col_headers,q_line[utorid]):
        #if data and data != "0.0":
        menu_items.append(hdr + ": " +  data)
        menu_data.append(data)
        cut_row -= 1
        if cut_row ==0:
            break

    from menu import MatzMenu
    m2 = MatzMenu(menu_items, "option: ") #number of selected menu item
    resp = m2.menu()
    if resp < 0 or  resp >= len(menu_items):
        return None
    else:
        return menu_data[resp]


def search_for(query_string,q_line,cdf_line):
    dropped_utorid = drops(q_line,cdf_line)

    # search for the QUERY_STRING in the files and record utorid's of hits in matched_utorid
    # TODO: try out doing this by starting with list of all utorids and filtering away?
    matched_utorids = []
    for d in [q_line,cdf_line]:
        matched_utorids += filter(lambda u: re.search(query_string,''.join(d[u]),re.IGNORECASE), d.keys())

    if len(matched_utorids) == 0:
        print("no students matching", query_string)
        return

    # which of the matched utorid's above are in the likely drops? warn.
    for utorid in dropped_utorid & set(matched_utorids):
        print("\n")
        print(utorid, "warning: matched student likely has dropped because not in quercus lecture section")
    print("\n")

    matched_utorids = list(set(matched_utorids)) # squeeze out dups
    matched_utorids.sort()

    utorid = select_student_menu(matched_utorids,q_line,cdf_line)
    selected_field = select_student_field(utorid,q_line,cdf_line)

    if selected_field:
        # copy the selected field into clipboard
        #selected_menu_item = menu_items[resp]
        print("copy ``" + selected_field + "`` to clipboard")
        os.system("/bin/echo -n '%s' | pbcopy" % selected_field)
    else:
        return

if __name__ == '__main__': 
    import sys, os, re, csv, functools, collections

    QUERCUS_UTORID_COL_NAME = "SIS Login ID"     # "SIS Login ID" is quercus for utorid

    # find python modules on mac,linux and windows laptops
    for dir in [
            '/home/matz/goit/dcs-grade-file-scripts/',
            '/Users/mzaleski/git/dcs-grade-file-scripts' ]:
        sys.path.append(dir)

    (cdf_class_file,quercus_grades_file,query_string) = parse_positional_args()
     
    from csv_file_reader import CsvFileToDictionaryReader
    quercus_csv_reader_by_utorid = CsvFileToDictionaryReader(quercus_grades_file,QUERCUS_UTORID_COL_NAME)

    q_lines = quercus_csv_reader_by_utorid.read_dict()
    cdf_lines = read_course_files(cdf_class_file,q_lines)

    if query_string:
        search_for(query_string,q_lines,cdf_lines)
    
    while True:
        query_string = input("student to search for >")
        search_for(query_string,q_lines,cdf_lines)
