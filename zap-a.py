#!/usr/local/bin/python3

# for the flat file of files created after downloading and unzipping quercus assignments,
# copy the PDF's into a new directory for each TA according to the section indicated.

# quercus has changed stuff a lot. Now pretty well all data comes from "grades" file.
# eg: 2018-09-30T1137_Grades-CSC300H1_F_LEC0101.csv

# Student,ID,SIS User ID,SIS Login ID,Section,A1 (64868),A2 (64870),A3 (64872),A4 (64875),Debate-prep (64880),tutorial-participation (64882),class-participation (64883),tutorial-sept-26 (75740),tutorial-sept-19 (76762),A1-group Current Score,A1-group Unposted Current Score,A1-group Final Score,A1-group Unposted Final Score,A2 Current Score,A2 Unposted Current Score,A2 Final Score,A2 Unposted Final Score,A3 Current Score,A3 Unposted Current Score,A3 Final Score,A3 Unposted Final Score,A4 Current Score,A4 Unposted Current Score,A4 Final Score,A4 Unposted Final Score,Debate Current Score,Debate Unposted Current Score,Debate Final Score,Debate Unposted Final Score,participation Current Score,participation Unposted Current Score,participation Final Score,participation Unposted Final Score,exam Current Score,exam Unposted Current Score,exam Final Score,exam Unposted Final Score,Current Score,Unposted Current Score,Final Score,Unposted Final Score

#    Points Possible,,,,,10.0,10.0,100.0,0.0,100.0,10.0,10.0,1.0,1.0,(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only),(read only)

#"Aayani, Simon",125821,1001729999,aayanisi,CSC300H1-F-LEC0101-20189 and DINA-Tut0101,,,,,,,,1.0,1.0,,,0.0,0.0,,,0.0,0.0,,,0.0,0.0,,,,,,,0.0,0.0,100.0,100.0,9.09,9.09,,,,,100.0,100.0,1.82,1.82

# key thing here is that there is a column called "Section" containing strings like "CSC300H1-F-LEC0101-20189 and DINA-Tut0101"

from __future__ import print_function  #allows print as function
def parse_positional_args():
    "parse the command line parameters of this program"
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("assignment_id", help="markus id of assignment. eg: a2r")
    args = parser.parse_args()
    return args.assignment_id

if __name__ == '__main__': 
    import sys
    import os
    #duplicate. sorta. so works on mac and windows laptops
    for dir in ['/home/matz/goit/dcs-grade-file-scripts/','/Users/mzaleski/git/dcs-grade-file-scripts']:
        sys.path.append(dir)

    assn = parse_positional_args() #eg: a1

    # this is usually a symlink to a dir in Google Drive File Stream file system..
    # (i've only ever done this for csc300, so leave it hardcoded)
    CLASS_DIR = "/Users/mzaleski/links/300"
    dest = os.path.join(CLASS_DIR, "zipped-submit", assn)

    if os.path.exists(dest):
        print(dest, "already exists, this script too chicken to overwrite")
        exit(2)
    
    from csv_file_reader import CsvFileToDictionaryReader

    src = os.path.join(CLASS_DIR,"submit",assn)
    if not os.path.exists(src):
        print(src, "dir does not exist, something very wrong")
        exit(2)

    # up-to-date downloaded quercus grades file in marks folder copied to 
    QUERCUS_GRADES_FILE = os.path.join(
        CLASS_DIR,
        "marks",
        "CSC300H1F-quercus.csv")

    if not os.path.exists(QUERCUS_GRADES_FILE):
        print(QUERCUS_GRADES_FILE,"file does not exist, something very wrong")
        exit(2)
    
    csv_reader_by_utorid = CsvFileToDictionaryReader(QUERCUS_GRADES_FILE,"SIS Login ID") 
    utorid_to_grade_file_line_dict = csv_reader_by_utorid.read_dict()

    def gather(d,assoc,ix):
        "for each student record the indicated column of csv file row"
        (utorid,cols) = assoc
        d[utorid] = cols[ix]
        return d

    # more quercus inconsistency. suppose tut section is AAA and lecture section is CSC300H...
    # if AAA is lexically before CSC300 quercus lists student section as
    # AAA and CSC300H
    # otherwise other way around, ie:
    # CSC300H1F and AAA
    
    def gather_section(d,assoc,ix):
        "look up quercus section col and dig out the tutorial section"
        (utorid,cols) = assoc
        section_quercus = cols[ix]
        tutorial = None
        FRIGGING_QUERCUS_AND = " and "
        if section_quercus.find(FRIGGING_QUERCUS_AND) > 0: # has and.. dropped students don't
            if section_quercus.index("CSC300") == 0:       # sigh. CSC300 before tutorial
                tutorial = section_quercus.split(FRIGGING_QUERCUS_AND)[1]
            else:
                tutorial = section_quercus.split(FRIGGING_QUERCUS_AND)[0]
        d[utorid] = tutorial
        return d

    ix_section= csv_reader_by_utorid.col_headers.index("Section")
    ix_ID     = csv_reader_by_utorid.col_headers.index("ID")
    
    from zip_assignments_for_ta import zip_assignments_for_ta_q
    import functools

    #could copy less by map'ing sections after gathering them
    zip_assignments_for_ta_q(
        functools.reduce( lambda d,assoc: gather_section(d,assoc,ix_section), utorid_to_grade_file_line_dict.items(), {} ),
        functools.reduce( lambda d,assoc: gather(d,assoc,ix_ID), utorid_to_grade_file_line_dict.items(),{}),
        quercus_download_dir=src,
        dest_dir = dest)

    exit(0)
