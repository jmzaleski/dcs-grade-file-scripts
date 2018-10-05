
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

    # duplicate. sorta. (so works on mac and windows laptops)
    sys.path.append('/home/matz/goit/dcs-grade-file-scripts/')
    sys.path.append('/Users/mzaleski/git/dcs-grade-file-scripts')

    (CDF_CLASS_FILE,QUERCUS_GRADES_FILE,query_string) = parse_positional_args()

    # "SIS Login ID" is quercus for utorid
    QUERCUS_UTORID_COL_NAME = "SIS Login ID"
    
    # read the grades files exported from quercus 
    # these are dictionaries of lists of strings. a list element from each column.
    quercus_csv_reader_by_utorid = CsvFileToDictionaryReader(QUERCUS_GRADES_FILE,QUERCUS_UTORID_COL_NAME) 
    q_line = quercus_csv_reader_by_utorid.read_dict()

    # read the CDF file and make a dict on utorid
    with open(CDF_CLASS_FILE) as csv_file:
        csv_file_reader = csv.reader(csv_file, delimiter=',', quotechar='"',dialect=csv.excel_tab)
        def acc(d, item):
            d[item[0]] = item         # because first col of CDF file always utorid
            return d
        cdf_line = functools.reduce(acc, csv_file_reader, {})

    #return is the part I can't see how to do in a lambda
    def matcher(utorid, dict): return re.search(query_string,''.join(dict[utorid]),re.IGNORECASE)
    def reducer(dict,utorid): dict.update({utorid:utorid}); return dict

    matched_utorid = functools.reduce(reducer, filter(lambda u:matcher(u,q_line), q_line.keys()),{})
    matched_utorid = functools.reduce(reducer, filter(lambda u:matcher(u,cdf_line), cdf_line.keys()), matched_utorid)
        
    def ugh(l,u,d): l.append(d[u]);  return l
    full_quercus_lines = functools.reduce(lambda l,u: ugh(l,u,q_line), matched_utorid,[])
    
    # filter out quercus cols with no data (o/w menu gets too messy)
    # this is as incscruitable as the loopy code(?)
    def ugh2(l,u,d1,d2):
        buf = ''
        if u in d1:
            for field in d1[u]:
                if field and field != "0.0":
                    buf +=  field + ", " 
        if u in d2:
            for field in d2[u]:
                if field and field != "0.0":
                    buf +=  field + ", " 
        l.append(buf)
        return l
    lines_to_display   = functools.reduce(lambda l,u: ugh2(l,u,q_line,cdf_line), matched_utorid,[])
                                              
    # lines_to_display = []
    # for utorid in matched_utorid:
    #     quercus_line = q_line[utorid]
    #     full_quercus_lines.append(quercus_line)
    #     buf = ""
    #     for field in quercus_line:
    #         if field and field != "0.0":
    #             buf += ", " + field
    #     if utorid in cdf_line:
    #         for field in cdf_line[utorid]:
    #             buf += ", " + field
    #     else:
    #         buf += ", " + utorid + " not in CDF file"
    #     lines_to_display.append(buf)

    # display menu of matched lines so user can select which match they meant.
    from menu import MatzMenu
    menu = MatzMenu(lines_to_display,"select student: ")
    resp = menu.menu()
    if resp < 0 or resp > len(lines_to_display)-1:
        print("invalid response")
  
    line = lines_to_display[resp].rstrip()

    # ugh. i've messed up order of lines by functools.reduce. what is utorid of matched line?
    IX_EMAIL_CDF = 5 #email always 5th field of CDF file
    IX_QUERCUS_UTORID = quercus_csv_reader_by_utorid.col_headers.index(QUERCUS_UTORID_COL_NAME) +1 ###HACK extra damn , in name
    utorid = line.split(",")[IX_QUERCUS_UTORID].strip()  ###HHHHHACK

    menu_items = []
    if utorid in cdf_line:
        menu_items.append( cdf_line[utorid][IX_EMAIL_CDF]) 

    # display menu of fields in matched student
    # have to use this for a while to learn what want to see.
    # quercus has a lot of BS fields, screenfuls.
    
    cut_row = 15 #too many scrolls off terminal
    for (hdr,data) in zip(quercus_csv_reader_by_utorid.col_headers,full_quercus_lines[resp]):
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
