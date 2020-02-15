
from __future__ import print_function  #allows print as function

def parse_positional_args():
    "parse the command line parameters of this program"
    import argparse, collections
    parser = argparse.ArgumentParser()
    for tuple in [
            #(arg_name,          arg_help_string,                                     nargs)
            ("cdf_csv_file",     "class list from CDF",                               1),
            ("quercus_csv_file", "class list from quercus eg: CSC300H1F-quercus.csv", 1),
            ("query_string",     "string to look for",                                '?')
            ]:
        parser.add_argument(tuple[0], help=tuple[1], nargs=tuple[2]),
    args = parser.parse_args()
    return (args.cdf_csv_file[0],args.quercus_csv_file[0], args.query_string)

def read_cdf_file(CDF_CLASS_FILE):
    # read the CDF file and make a dict key'd by utorid of each line
    cdf_line = {}
    with open(CDF_CLASS_FILE) as csv_file:
        for a_line in csv.reader(csv_file, delimiter=',', quotechar='"',dialect=csv.excel_tab):
            cdf_line[a_line[0]] = a_line
    return cdf_line

def dropped_utorid_set(q_line,cdf_line):
    "return set of likely dropped utorids"
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

    if len(dropped_utorid)>0:
        if False: print("warning: following likely dropped because not in quercus lecture section", dropped_utorid)
    return dropped_utorid

# make a menu item for each student record from quercus matched by the query
# nb utorids come from the union of quercus and cdf, so there might not be a line in quercus

def select_student_menu(matched_utorids,q_line,cdf_line):
    "print a menu to choose a utorid of those in matched_utorids"
    choose_student_menu = []
    rev_utorid_map = {}
    for utorid in matched_utorids:
        if utorid in q_line:
            cols = filter(lambda a_col: a_col and a_col != "0.0", q_line[utorid])
            
            flat_cols = ", ".join(cols)
            l = (flat_cols[:85] + '..') if len(flat_cols) > 75 else flat_cols
            choose_student_menu.append(l)
            rev_utorid_map[l] = utorid
    print("select student by entering number in left column..")
    from menu import MatzMenu
    menu = MatzMenu(choose_student_menu,"select student: ")
    resp = menu.menu()
    if resp < 0 or resp > len(choose_student_menu)-1:
        print(resp, "is invalid response")
        return None

    line = choose_student_menu[resp].rstrip()
    utorid = rev_utorid_map[line]
    return utorid


def select_student_field(utorid,q_line,cdf_line):
    "display menu so user can choose which field they want"
    IX_EMAIL_CDF = 5 #email always 5th field of CDF file
    menu_items = []
    menu_data = []
    # pluck the email out of cdf fields (IX_EMAIL_CDF magic number of field)
    if utorid in cdf_line:
        menu_items.append( cdf_line[utorid][IX_EMAIL_CDF])
        menu_data.append(cdf_line[utorid][IX_EMAIL_CDF])
    else:
        menu_items.append( "no email because " + utorid + " missing in CDF")
        menu_data.append( "no email because " + utorid + " missing in CDF")

    # display menu of fields in matched student
    # have to use this for a while to learn what want to see.
    # quercus has many many fields because grades add much cruft.

    cut_field = 6 #zillions of mark data fields follow
    all_fields = ""
    for (hdr,data) in zip(quercus_csv_reader_by_utorid.col_headers,q_line[utorid]):
        #if data and data != "0.0":
        menu_items.append(hdr + ": " +  data)
        menu_data.append(data)
        all_fields += "|" + data
        cut_field -= 1
        if cut_field ==0:
            break

    # make an all up field (useful to share with TAs, etc)
    menu_items.append("all:" + all_fields)
    menu_data.append(all_fields)

    from menu import MatzMenu
    m2 = MatzMenu(menu_items, "option: ") #number of selected menu item
    resp = m2.menu()
    if resp < 0 or  resp >= len(menu_items):
        return None
    else:
        return menu_data[resp]


def search_for_utorids(query_string,q_lines,utorid_to_cdf_line_map):
    "return list of utorid's from records matching query_string in q_lines, utorid_to_cdf_line_map"
    matched_utorids = []
    for d in [q_lines,utorid_to_cdf_line_map]:
        matched_utorids += filter(lambda u: re.search(query_string,''.join(d[u]),re.IGNORECASE), d.keys())

    if len(matched_utorids) == 0:
        print("no students matching ``"+ query_string + "''")
        return None

    matched_utorids = list(set(matched_utorids)) # squeeze out dups
    matched_utorids.sort()
    return matched_utorids

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

    # read the quercus exported csv file into dict keyed by utorid
    q_lines = quercus_csv_reader_by_utorid.read_dict()

    # read the CDF file into a dict keyed by utorid
    utorid_to_cdf_line_map = read_cdf_file(cdf_class_file)

    #TODO: this is bullshit confusing state
    is_query_string_in_parms = query_string and len(query_string)>0

    for utorid in dropped_utorid_set(q_lines,utorid_to_cdf_line_map):
        print(utorid, "warning: the student likely has dropped because not in quercus lecture section")

    while True:
        try:
            if not is_query_string_in_parms:
                query_string = input("student to search for >")
            is_query_string_in_parms = False
            
            matched_utorids = search_for_utorids(query_string,q_lines,utorid_to_cdf_line_map)
            if not matched_utorids:
                continue
            
            # warn which of the matched utorid's above are in the likely drops.
            dropped_utorid = dropped_utorid_set(q_lines,utorid_to_cdf_line_map)
            if False:
                for utorid in dropped_utorid & set(matched_utorids):
                    print(utorid, "warning: the student likely has dropped because not in quercus lecture section")

            # user selects which student if more than one utorid matched above
            utorid = select_student_menu(matched_utorids,q_lines,utorid_to_cdf_line_map)
            if not utorid:
                continue

            # user selects which field of CSV file corresponding to student to copy
            selected_field = select_student_field(utorid,q_lines,utorid_to_cdf_line_map)
            if not select_student_field:
                continue
            
            # copy the selected field into clipboard
            print("copy ``" + selected_field + "`` to clipboard")
            os.system("/bin/echo -n '%s' | pbcopy" % selected_field)

            # and now try and open the mailto in default mail client.
            if selected_field.find("@") > 0:
                resp = input("open mailto: ?  [yYnN]* >")
                if resp.lower().startswith( 'y'):
                    url = "mailto:%s" % selected_field
                    import webbrowser
                    webbrowser.open(url)
        except:
            print("")
            exit(0)

            
