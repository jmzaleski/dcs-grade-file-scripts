from __future__ import print_function  #allows print as function

from grade_file_reader_writer import GradeFileReaderWriter

def test_gfr(gfr):
    import os
    from os import system
    from os import listdir

    "find the PDF's for all the students in each TAs section and zip them into a separate zip file for each TA"
    from os.path import isfile, join
    gfr.read_file()
    tas = set([ns.ta for ns in gfr.students])
    files_per_ta = {}
    for ta in tas:
        print("TA",ta)
        ta_files = []
        # assert len([ns.utorid for ns in gfr.students if ns.ta == ta]) == len(set([ns.utorid for ns in gfr.students if ns.ta == ta]))
        for utorid in [ns.utorid for ns in gfr.students if ns.ta == ta]:
            print(utorid)

if __name__ == '__main__':
    fn = "/Users/mzaleski/GoogleDrive/CSC/300/marks/TA"
    print(fn)
    contents_of_grade_file = open(fn).read()
    gfr=GradeFileReaderWriter(contents_of_grade_file,debug=True)
    test_gfr(gfr)
