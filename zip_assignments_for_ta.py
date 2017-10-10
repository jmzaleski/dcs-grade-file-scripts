from __future__ import print_function  #allows print as function

def zip_assignments_for_ta(gfr, markus_download_dir, dest_dir):
    import os
    from os import system
    from os import listdir

    "find the PDF's for all the students in each TAs section and zip them into a separate zip file for each TA"
    from os.path import isfile, join
    gfr.read_file()
    tas = set([ns.ta for ns in gfr.students])
    files_per_ta = {}
    for ta in tas:
        print(ta)
        ta_files = []
        # assert len([ns.utorid for ns in gfr.students if ns.ta == ta]) == len(set([ns.utorid for ns in gfr.students if ns.ta == ta]))
        for utorid in [ns.utorid for ns in gfr.students if ns.ta == ta]:
            rel_path = utorid
            dir = "%s/%s/" % (markus_download_dir, rel_path) ###hack
            if not os.path.isdir(dir):
                print("no dir for", utorid)
                continue
            print(dir, "for", utorid)
            for fn in [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]:
                ta_files.append(os.path.join(rel_path, fn))
        files_per_ta[ta] = ta_files

    for ta in tas:
       print(ta, len(files_per_ta[ta]), files_per_ta[ta])

    from shutil import copy

    os.makedirs(dest_dir)

    for ta in tas:
        print(ta, ": ", end='')
        ta_dir = os.path.join(dest_dir, ta)
        assert not os.path.isfile(ta_dir)  # oh no a FILE exists where we want to mkdir
        if not os.path.isdir(ta_dir):
            os.makedirs(ta_dir)
        for fn in files_per_ta[ta]:
            src_path = os.path.join(markus_download_dir, fn)
            print(fn, end='')
            copy(src_path, ta_dir)
        print()
        #os.chdir(ta_dir)  ####### so can make zip files with relative path
        zip_cmd = "zip --junk-paths -r %s.zip %s" % (ta_dir, ta_dir)
        print(zip_cmd)
        #junk = input("doit?")
        # zip all the files in the ta_dir into ta_dir.zip
        os.system(zip_cmd)
        os.system("ls -ld %s.zip" % ta_dir)
