
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

def read_cdf_file(cdf_class_file):
    # read the CDF file and make a dict key'd by utorid of each line
    cdf_map = {}
    with open(cdf_class_file) as csv_file:
        for a_line in csv.reader(csv_file, delimiter=',', quotechar='"',dialect=csv.excel_tab):
            cdf_map[a_line[0]] = a_line
    return cdf_map

def dropped_utorid_set(q_map,cdf_map):
    "return set of likely dropped utorids"
    dropped_utorid = set()
    if not set(q_map.keys()) == set(cdf_map.keys()):
        # find records that don't have a section field containing "CSC"
        # (for drops, quercus removes the lecture section but not the tutorial section)
        for utorid in set(q_map.keys()).difference(set(cdf_map.keys())):
            # TODO: make new method in csv_reader to fetch named column ? ask gary.
            if len(q_map[utorid])<5:
                print("ohoh quercus line has less than four fields..how did you do that??")
                print(q_map[utorid])
                exit(2)
            if len(q_map[utorid][4]) >0 and q_map[utorid][4].find("CSC") < 0:
                dropped_utorid.add(utorid)
                # print(utorid,"probably dropped because doesn't appear to be in lecture section")
        # compare utorid's to help catch case when files are out-of-date
        # TODO functionalify this!
        if False: #verbosity
            # debug output for diagnosing differences
            print("CDF classlist and quercus grade file do not contain identical sets of utorids")
            print("records in quercus but not CDF (drops?)")
            for utorid in set(q_map.keys()).difference(set(cdf_map.keys())):
                print( " ".join(filter(lambda s: len(s)>0,q_map[utorid]))[0:80]) #skip empty fields
            print("records in CDF but not quercus (adds?)")
            for utorid in set(cdf_map.keys()).difference(set(q_map.keys())):
                print( " ".join(filter(lambda s: len(s)>0,q_map[utorid]))[0:80]) #skip empty fields

    if len(dropped_utorid)>0:
        if False: print("warning: following likely dropped because not in quercus lecture section", dropped_utorid)
    return dropped_utorid

# make a menu item for each student record from quercus matched by the query
# nb utorids come from the union of quercus and cdf, so there might not be a line in quercus

def select_student_menu(matched_utorids,q_map,cdf_map):
    "print a menu to choose a utorid of those in matched_utorids"
    choose_student_menu = []
    rev_utorid_map = {}
    for utorid in matched_utorids:
        if utorid in q_map:
            cols = filter(lambda a_col: a_col and a_col != "0.0", q_map[utorid])
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
    #print("got utorid", utorid)
    return utorid

def select_student_field(utorid,q_map,cdf_map,q_col_headers):
    "display menu so user can choose which field they want"
    IX_EMAIL_CDF = 5 #email always 5th field of CDF file
    menu_items = []
    menu_data = []
    # pluck the email out of cdf fields (IX_EMAIL_CDF magic number of field)
    if utorid in cdf_map:
        menu_items.append( cdf_map[utorid][IX_EMAIL_CDF])
        menu_data.append(cdf_map[utorid][IX_EMAIL_CDF])
    else:
        menu_items.append( "no email because " + utorid + " missing in CDF")
        menu_data.append( "no email because " + utorid + " missing in CDF")

    # display menu of fields in matched student
    # hard to know what want to see in this menu.
    # quercus has many many fields because grades add much cruft.
    #print("q_map[utorid]",q_map[utorid])
    cut_field = 6 #zillions of mark data fields follow
    all_fields = ""
    for (hdr,data) in zip(q_col_headers,q_map[utorid]):
        #if data and data != "0.0":
        menu_items.append(hdr + ": " +  data)
        menu_data.append(data)
        all_fields += "|" + data
        cut_field -= 1
        if cut_field == 0:
            break

    # make an all-included field (useful to share with TAs, etc)
    menu_items.append("all:" + all_fields)
    menu_data.append(all_fields)

    from menu import MatzMenu
    m2 = MatzMenu(menu_items, "option: ") #number of selected menu item
    resp = m2.menu()
    if resp < 0 or  resp >= len(menu_items):
        return None
    else:
        return menu_data[resp]

def search_for_utorids(query_string,utorid_to_quercus_line_map,utorid_to_cdf_line_map):
    "return list of utorid's from records matching query_string in utorid_to_quercus_line_map, utorid_to_cdf_line_map"
    matched_utorids = []
    for d in [utorid_to_quercus_line_map,utorid_to_cdf_line_map]:
        matched_utorids += filter(lambda u: re.search(query_string,''.join(d[u]),re.IGNORECASE), d.keys())

    if len(matched_utorids) == 0:
        print("no students matching ``"+ query_string + "''")
        return None

    matched_utorids = list(set(matched_utorids)) # squeeze out dups
    matched_utorids.sort()
    return matched_utorids

import functools
def read_dict(fn,col_name):
    """read csv file returning dict with association for each line in fn, keyed by field in col_name"""
    key_col_number = None
        
    with open(fn) as csv_file:
        csv_file_reader = csv.reader(csv_file, delimiter=',', quotechar='"',dialect=csv.excel_tab)
        # squirrel away lines containing column headers and mysterious second line
        col_headers = next(csv_file_reader)
        line2 = next(csv_file_reader)
        key_col_number = col_headers.index(col_name) #throws if not found
        def acc(d, item):
            d[item[key_col_number]] = item
            return d
        return functools.reduce(acc, csv_file_reader, {})

if __name__ == '__main__': 
    import sys, os, re, csv, functools, collections

    #this is the quercus column header naming the utorid column in a grades file
    QUERCUS_UTORID_COL_NAME = "SIS Login ID"     # what quercus calls utorid

    # find python modules on mac,linux and windows laptops
    for dir in ['/home/matz/goit/dcs-grade-file-scripts/',
                '/Users/mzaleski/git/dcs-grade-file-scripts' ]:
        sys.path.append(dir)

    (cdf_class_file,quercus_grades_file,query_string) = parse_positional_args()

    # will need column headers later to print menu
    q_col_headers = None
    # read the quercus exported grade CSV file into dict keyed by utorid
    utorid_to_quercus_line_map = None
    with open(quercus_grades_file) as csv_file:
        csv_file_reader = csv.reader(csv_file, delimiter=',', quotechar='"',dialect=csv.excel_tab)
        q_col_headers = next(csv_file_reader)
        next(csv_file_reader) 
        def acc(d, item):
            d[item[q_col_headers.index(QUERCUS_UTORID_COL_NAME)]] = item
            return d
        utorid_to_quercus_line_map = functools.reduce(acc, csv_file_reader, {})

    if False: print("utorid_to_quercus_line_map",utorid_to_quercus_line_map)

    utorid_to_cdf_line_map = read_cdf_file(cdf_class_file)

    for utorid in dropped_utorid_set(utorid_to_quercus_line_map,utorid_to_cdf_line_map):
        print(utorid, "warning: the student likely has dropped because not in quercus lecture section")

    #TODO: this bullshit confusing flag notices when first search query comes from command line parms
    is_query_string_in_parms = query_string and len(query_string)>0

    while True:
        try:
            if not is_query_string_in_parms:
                query_string = input("student to search for >")
            is_query_string_in_parms = False
            
            matched_utorids = search_for_utorids(query_string,utorid_to_quercus_line_map,utorid_to_cdf_line_map)
            if not matched_utorids:
                continue

            dropped_utorid = dropped_utorid_set(utorid_to_quercus_line_map,utorid_to_cdf_line_map)
            if False:
                for utorid in dropped_utorid & set(matched_utorids):
                    print(utorid, "warning: the student likely has dropped because not in quercus lecture section")

            # user selects which student if more than one utorid matched above
            if len(matched_utorids)==1:
                utorid = matched_utorids[0]
            else:
                utorid = select_student_menu(matched_utorids,utorid_to_quercus_line_map,utorid_to_cdf_line_map)
            if not utorid:
                continue

            # user selects which field of CSV file corresponding to student to copy
            selected_field = select_student_field(utorid,utorid_to_quercus_line_map,utorid_to_cdf_line_map,q_col_headers)
            if not selected_field:
                continue
            
            print("copy ``" + selected_field + "`` to clipboard")
            os.system("/bin/echo -n '%s' | pbcopy" % selected_field)

            # if email selected.. try and open the mailto in default mail client.
            if selected_field.find("@") > 0:
                url = "mailto:%s" % selected_field
                print(url)
                resp = input("open mailto: ?  [yYnN]* >")
                if resp.lower().startswith( 'y'):
                    import webbrowser
                    webbrowser.open(url)
        except:
            print("")
            exit(0)

            
