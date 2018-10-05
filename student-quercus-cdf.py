
from __future__ import print_function  #allows print as function
def parse_positional_args():
    "parse the command line parameters of this program"
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("cdf_csv_file", help="class list from CDF eg: CSC300H1F-cdf.csv")
    parser.add_argument("quercus_csv_file", help="class list from quercus eg: CSC300H1F-quercus.csv")
    parser.add_argument("query_string", help="string to look for")
    args = parser.parse_args()
    return (args.cdf_csv_file,args.quercus_csv_file, args.query_string)

if __name__ == '__main__': 
    import sys, os, re, csv, functools
    from csv_file_reader import CsvFileToDictionaryReader

    # duplicate. sorta. so works on mac and windows laptops
    sys.path.append('/home/matz/goit/dcs-grade-file-scripts/')
    sys.path.append('/Users/mzaleski/git/dcs-grade-file-scripts')

    (CDF_CLASS_FILE,QUERCUS_GRADES_FILE,query_string) = parse_positional_args()

    # read the grades files exported from quercus ("SIS Login ID" is quercus for utorid)
    # these are dictionaries of lists of strings. a list element from each column.
    quercus_csv_reader_by_utorid = CsvFileToDictionaryReader(QUERCUS_GRADES_FILE,"SIS Login ID") 
    utorid_to_quercus_line = quercus_csv_reader_by_utorid.read_dict()

    # read the CDF file and make a dict on utorid
    with open(CDF_CLASS_FILE) as csv_file:
        csv_file_reader = csv.reader(csv_file, delimiter=',', quotechar='"',dialect=csv.excel_tab)
        def acc(d, item):
            d[item[0]] = item
            return d
        utorid_to_cdf_file_line_dict = functools.reduce(acc, csv_file_reader, {})

    # find the lines in BOTH files that match the query
    matched_utorid = {}
    for (utorid,line) in utorid_to_quercus_line.items():
        line_as_string = ''.join(line)
        m = re.search(query_string, line_as_string,re.IGNORECASE)
        if m:
            matched_utorid[utorid]=utorid

    #bit over the top. 
    #print(list(filter(lambda utorid: re.search(query_string,''.join(utorid_to_quercus_line[utorid]),re.IGNORECASE), utorid_to_quercus_line.keys())))
            
    matched_utorid = {}
    def pred(utorid):
        return re.search(query_string,''.join(utorid_to_quercus_line[utorid]),re.IGNORECASE)

    def mapper(utorid,dict):
        dict[utorid] = utorid

    #map(lambda utorid: mapper(utorid,matched_utorid), filter(pred, utorid_to_quercus_line.keys()))
    def reducer(d,utorid):
        d.update({utorid:utorid})
        return d
        
    print( functools.reduce(reducer,filter(pred, utorid_to_quercus_line.keys()),{}) )
    exit(0)
        
    for utorid in filter(pred, utorid_to_quercus_line.keys()):
        matched_utorid[utorid] = utorid

    print(matched_utorid)
    exit(0)
    # yeah but want to search emails too.. those are in the CDF file
    for (utorid,line) in utorid_to_cdf_file_line_dict.items():
        line_as_string = ' '.join(line)
        m = re.search(query_string, line_as_string,re.IGNORECASE)
        if m:
            matched_utorid[utorid]=utorid
            
    # filter out cols with no data (o/w menu gets too messy)
    lines_to_display = []
    full_quercus_lines = []
    for utorid in matched_utorid:
        quercus_line = utorid_to_quercus_line[utorid]
        full_quercus_lines.append(quercus_line)
        buf = ""
        for field in quercus_line:
            if field and field != "0.0":
                buf += ", " + field
        if utorid in utorid_to_cdf_file_line_dict:
            for field in utorid_to_cdf_file_line_dict[utorid]:
                buf += ", " + field
        else:
            buf += ", " + utorid + " not in CDF file"
        lines_to_display.append(buf)

    # display menu of matched lines so user can select which match they meant.
    from menu import MatzMenu
    menu = MatzMenu(lines_to_display,"select student: ")
    resp = menu.menu()
    if resp < 0 or resp > len(lines_to_display)-1:
        print("invalid response")
    line = lines_to_display[resp].rstrip()

    menu_items = []
    if utorid in utorid_to_cdf_file_line_dict:
        menu_items.append( utorid_to_cdf_file_line_dict[utorid][5]) #5th field of CDF file
        
    for (hdr,data) in zip(quercus_csv_reader_by_utorid.col_headers,full_quercus_lines[resp]):
        if data and data != "0.0":
            menu_items.append(hdr + data)

    # display menu of fields in matched student
    m2 = MatzMenu(menu_items, "option: ") #number of selected menu item
    resp = m2.menu()
    if resp < 0 or  resp >= len(menu_items):
        exit(0)

    # copy the selected field into clipboard
    selected_menu_item = menu_items[resp]
    print(selected_menu_item)
    os.system("/bin/echo -n '%s' | pbcopy" % selected_menu_item)
    exit(0)
