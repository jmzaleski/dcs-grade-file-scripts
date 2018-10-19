
from __future__ import print_function  #allows print as function

def parse_positional_args():
    "parse the command line parameters of this program"
    import argparse, collections
    parser = argparse.ArgumentParser()
    collections.deque(
        map( lambda tuple: parser.add_argument(tuple[0], help=tuple[1]),
            [("cdf_csv_file",     "class list from CDF"),
            ("quercus_csv_file", "class list from quercus eg: CSC300H1F-quercus.csv"),
            ("query_string",     "string to look for")
            ]))
    # surely less weird to say:
    # parser = argparse.ArgumentParser()
    # for tuple in [
    #         ("cdf_csv_file",     "class list from CDF"),
    #         ("quercus_csv_file", "class list from quercus eg: CSC300H1F-quercus.csv"),
    #         ("query_string",     "string to look for") ]:
    #     parser.add_argument(tuple[0], help=tuple[1]),
    args = parser.parse_args()
    return (args.cdf_csv_file,args.quercus_csv_file, args.query_string)

if __name__ == '__main__': 
    import sys, os, re, csv, functools, collections
    from csv_file_reader import CsvFileToDictionaryReader

    # so finds my modules both on mac and windows laptops
    for dir in ['/home/matz/goit/dcs-grade-file-scripts/','/Users/mzaleski/git/dcs-grade-file-scripts']:
        sys.path.append(dir)

    (CDF_CLASS_FILE,QUERCUS_GRADES_FILE,QUERY_STRING) = parse_positional_args()

    QUERCUS_UTORID_COL_NAME = "SIS Login ID"     # "SIS Login ID" is quercus for utorid
    
    # read the grades files exported from quercus and make a dict key'd by utorid. 
    # value is list with element from each column
    quercus_csv_reader_by_utorid = CsvFileToDictionaryReader(QUERCUS_GRADES_FILE,QUERCUS_UTORID_COL_NAME) 
    q_line = quercus_csv_reader_by_utorid.read_dict()

    # read the CDF file and make a dict key'd by utorid of each line
    cdf_line = {}
    with open(CDF_CLASS_FILE) as csv_file:
        collections.deque(map(lambda a_line: cdf_line.update({a_line[0]: a_line}),csv.reader(csv_file, delimiter=',', quotechar='"',dialect=csv.excel_tab)))

    # compare utorid's to help catch case when files are out-of-date
    if not set(q_line.keys()) == set(cdf_line.keys()):
        print("CDF classlist and quercus grade file do not contain identical sets of utorids")
        print("records in quercus but not CDF (drops?)")
        for utorid in set(q_line.keys()).difference(set(cdf_line.keys())):
            print( " ".join(filter(lambda s: len(s)>0,q_line[utorid]))[0:80]) #skip empty fields
        print("records in CDF but not quercus (adds?)")
        for utorid in set(cdf_line.keys()).difference(set(q_line.keys())):
            print( " ".join(filter(lambda s: len(s)>0,q_line[utorid]))[0:80]) #skip empty fields
    
    # search for the QUERY_STRING in the files and record utorid's of hits
    matched_utorids = []
    for d in [q_line,cdf_line]:
        matched_utorids += filter(lambda u: re.search(QUERY_STRING,''.join(d[u]),re.IGNORECASE), d.keys())
    if len(matched_utorids) == 0:
        print("no students matching", QUERY_STRING)
        exit(1)
        
    matched_utorids = list(set(matched_utorids)) # squeeze out dups
    matched_utorids.sort()

    # make the menu items to choose between matched from the utorids
    # using the lines matched in the quercus file put 
    choose_student_menu = []
    rev_utorid_map = {}
    for utorid in matched_utorids:
        if utorid in q_line:
            cols = filter(lambda a_col: a_col and a_col != "0.0", q_line[utorid])
            flat_cols = ", ".join(cols)
            choose_student_menu.append(flat_cols)
            rev_utorid_map[flat_cols] = utorid

    # display menu of matched lines so user can select which match they meant.
    from menu import MatzMenu
    menu = MatzMenu(choose_student_menu,"select student: ")
    resp = menu.menu()
    if resp < 0 or resp > len(choose_student_menu)-1:
        print(resp, "is invalid response")
        exit(2)

    line = choose_student_menu[resp].rstrip()
    utorid = rev_utorid_map[line]

    IX_EMAIL_CDF = 5 #email always 5th field of CDF file
    menu_items = []
    if utorid in cdf_line:
        menu_items.append( cdf_line[utorid][IX_EMAIL_CDF])
    else:
        menu_items.append( "no email because " + utorid + " missing in CDF")

    # display menu of fields in matched student
    # have to use this for a while to learn what want to see.
    # quercus has a lot of BS fields, screenfuls.
    
    cut_row = 15 #too many scrolls off terminal
    for (hdr,data) in zip(quercus_csv_reader_by_utorid.col_headers,q_line[utorid]):
        #if data and data != "0.0":
        menu_items.append(hdr + ": " +  data)
        cut_row -= 1
        if cut_row ==0:
            break

    m2 = MatzMenu(menu_items, "option: ") #number of selected menu item
    resp = m2.menu()
    if resp < 0 or  resp >= len(menu_items):
        exit(0)

    # copy the selected field into clipboard
    selected_menu_item = menu_items[resp]
    print(selected_menu_item)
    os.system("/bin/echo -n '%s' | pbcopy" % selected_menu_item)
    exit(0)
