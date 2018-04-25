#!/usr/local/bin/python3

# download the google sheets the TAs enter their marks into..
# NB. they have to be properly formatted (ie. first two lines are metadata)
# in order to be converted into jim clark format grades files

def parse_positional_args():
    "parse the command line parameters of this program"
    import argparse
    parser = argparse.ArgumentParser(description='download some or all grade files')
    parser.add_argument("--all", action='store_true', help="fetch all grades files")
    parser.add_argument('grade_files_to_fetch', nargs='*',
                        help='name of grade file to fetch')
    args = parser.parse_args()
    print("--all", args.all, "grade_file_list", args.grade_files_to_fetch)
    return args
    
if __name__ == '__main__':
    import sys
    sys.path.append('/home/matz/git/dcs-grade-file-scripts')
    from get_google_sheet_as_jim_clarke_grades_file import write_grade_file_from_csv_metadata_and_marks 
    from get_google_sheet_as_jim_clarke_grades_file import get_sheet_data_from_url
    import os
    
    args = parse_positional_args()
    always_download = args.all
    grade_file_list = args.grade_files_to_fetch
    if always_download and len(grade_file_list)>0:
        print("usage error: cannot both say --all and name files")
        exit(0)
    #TODO: figure out how to factor this!!
    tab = {
        "https://docs.google.com/spreadsheets/d/1GvNb3ZzvIPERTH4LOxJXsn6M7ElnZX-lx_nmrCNLcj4/edit#gid=1371474907" : "p_tu",
        "https://docs.google.com/spreadsheets/d/19Gq_oL6WgelKszYJxhZf0YBuw1fgStt5wuoHuqbYWPs/edit#gid=1371474907" : "r",
        "https://docs.google.com/spreadsheets/d/1ZMK-85tRid15rou23mhlO0d5CURhSxtrfKqWRzT0-7c/edit#gid=475080676" : "a1",
        "https://docs.google.com/spreadsheets/d/1DLoBa2cGXAKBi9GiYHDcoSsouT7gRBL9QmrAXhJdyFE/edit#gid=475080676" : "a1r",
        "https://docs.google.com/spreadsheets/d/1iBEIbK8jrqujSVB1bXtYJGEGR1amsRujr96navUC1c8/edit#gid=790547393" : "a2",
        "https://docs.google.com/spreadsheets/d/1LggVO5-aTkDHOjTWDhTEIfbciVoBrN_ZLVyxvQGBdlU/edit#gid=790547393" : "a2r",
        "https://docs.google.com/spreadsheets/d/1NceIp3zPkVICqzhi73WuZjgt11YgHkLJyWr47YyY8N8/edit#gid=790547393" : "a3",
        "https://docs.google.com/spreadsheets/d/1-fFdqUjbSw6mV-zKsof7mgz-cv6v-Du1ZWcup_dVAk4/edit#gid=1942238050" : "term",
        "https://docs.google.com/spreadsheets/d/1IHYEGAw16Zwc_zUE6_k2yzWfYZLhXRy04xrD8Kwrxs4/edit#gid=0" : "fin",
        }

    #untab lousy name for reverse mapping
    untab = {}
    for k in tab.keys():
        untab[tab[k]] = k
    print(untab)

    # if grade files have been named on command line, just do those. o/w do them all.
    if len(grade_file_list) > 0:
        for gf in grade_file_list:
            if not gf in list(untab.keys()):
                print(gf,"unknown key", untab.keys())
                exit(2)
        l = grade_file_list
    else:
        l = list(untab.keys())
        l.sort()
    print(l)
    # don't overwrite grades files!
    write_file = {}
    for k in untab.keys():
        if always_download:
            write_file[ofn] = True
        else:
            write_file[k] = False

    if not always_download:
        for ofn in l:
            if not os.path.isfile(ofn):
                write_file[ofn] = True
                continue
            # too chicken to overwrite this file, so ask
            resp = input( "are you sure you want to overwrite " + ofn + " ? [yY]* >")
            if len(resp) == 0:
                write_file[ofn] = False
            elif resp.startswith("y") or resp.startswith("Y"):
                write_file[ofn] = True

    #REAL work
    for sheet_name in tab.keys():
        ofn = tab[sheet_name]
        if not always_download:
            if not write_file[ofn]:  
                print("skip fetch of", ofn)
                continue
        print("about to download google sheet", sheet_name, "to file", ofn)
        d = get_sheet_data_from_url(sheet_name)
        write_grade_file_from_csv_metadata_and_marks(d, ofn)

    for ofn in tab.values():
        if write_file[ofn]:
            os.system("ls -l %s" % ofn)

    exit(0)


