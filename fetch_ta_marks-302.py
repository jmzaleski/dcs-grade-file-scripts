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
    print("--all", args.all, "gf", args.grade_files_to_fetch)
    return args
    
if __name__ == '__main__':
    import sys
    sys.path.append('/home/matz/git/dcs-grade-file-scripts')
    from get_google_sheet_as_jim_clarke_grades_file import write_grade_file_from_csv_metadata_and_marks 
    from get_google_sheet_as_jim_clarke_grades_file import get_sheet_data_from_url
    import os
    
    args = parse_positional_args()
    always_download = args.all
    gf = args.grade_files_to_fetch
    if always_download and len(gf)>0:
        print("usage error: cannot both say --all and name files")
        exit(0)
    #TODO: figure out how to factor this!!
    tab = {
        "https://docs.google.com/spreadsheets/d/184_Z-fGVKAOCgOuVdEI9-4z6c76EaUX8tkTI-MjG6Xs/edit#gid=0" : "fin",
        "https://docs.google.com/spreadsheets/d/1IcH0vUepBZMWQ5bGSxWttAaEVT6Ref3poUNxTLLgaOA/edit#gid=1451710455" : "term",
        "https://docs.google.com/spreadsheets/d/1PLNvWmiIhL1G0VUQE5nkbujDE3bJEbjRSTsY06d-se0/edit#gid=1270130289" : "mid",
        "https://docs.google.com/spreadsheets/d/1CCNeOXAvkKA7Z3seeoG6-Qh2FWieFJou2n_KM0lGfow/edit#gid=952112419" : "a4",
        }

    #untab lousy name for reverse mapping
    untab = {}
    for k in tab.keys():
        untab[tab[k]] = k
    print(untab)

    # if grade files have been named on command line, just do those. o/w do them all.
    if len(gf) > 0:
        l = gf
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
        assert d
        write_grade_file_from_csv_metadata_and_marks(d, ofn)

    for ofn in tab.values():
        if write_file[ofn]:
            os.system("ls -l %s" % ofn)

    exit(0)


