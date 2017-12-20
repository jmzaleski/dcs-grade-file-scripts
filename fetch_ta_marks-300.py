#!/usr/local/bin/python3

# download the google sheets the TAs enter their marks into..
# NB. they have to be properly formatted (ie. first two lines are metadata)
# in order to be converted into jim clark format grades files

def parse_positional_args():
    "parse the command line parameters of this program"
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--yes", action='store_true', help="fetch all grades files")
    args = parser.parse_args()
    return args
    

if __name__ == '__main__':
    yes = parse_positional_args().yes
    import sys
    sys.path.append('/home/matz/git/dcs-grade-file-scripts')
    from get_google_sheet_as_jim_clarke_grades_file import write_grade_file_from_csv_metadata_and_marks 
    from get_google_sheet_as_jim_clarke_grades_file import get_sheet_data
    import os
    tab = {
        "exam-raw" : "exam-raw",
        "tutorial-participation" : "p_tu",
        "Debate" : "deb",
        "a1r" : "a1",
        "a2r" : "a2",
        "a3" : "a3",
        "a4" : "a4"
        }
    #don't overwrite grades files!
    write_file = {}
    l = list(tab.values())
    l.sort()
    for ofn in l:
        if yes:
            write_file[ofn] = True
            continue
        if not os.path.isfile(ofn):
            write_file[ofn] = True
            continue
        # too chicken to overwrite this file, so ask
        resp = input( "are you sure you want to overwrite " + ofn + " ? [yY]* >")
        if len(resp) == 0:
            write_file[ofn] = False
        elif resp.startswith("y") or resp.startswith("Y"):
            write_file[ofn] = True
        else:
           write_file[ofn] = False

    #REAL work
    for sheet_name in tab.keys():
        ofn = tab[sheet_name]
        if not yes or not write_file[ofn]:
            print("skip fetch of", ofn)
            continue
        print("about to download google sheet", sheet_name, "to file", ofn)
        d = get_sheet_data(sheet_name)
        write_grade_file_from_csv_metadata_and_marks(d, ofn)

    for ofn in tab.values():
        if write_file[ofn]:
            os.system("ls -l %s" % ofn)

    exit(0)

    def parse_positional_args():
        "parse the command line parameters of this program"
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("google_sheet_doc_name", help="name of google sheet. eg: tutorial-participation")
        parser.add_argument("output_grade_file_name", help="name of jim clarke grade file to write eg: p_tu")
        args = parser.parse_args()
        return args
    args = parse_positional_args()
    write_grade_file_from_csv_metadata_and_marks(
        get_sheet_data(args.google_sheet_doc_name),
        args.output_grade_file_name)

    #args = parse_positional_args()

